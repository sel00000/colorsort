"""불변 자료구조. 로직을 넣지 않는다."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class Msg:
    """언어에 독립적인 메시지. 열쇠와 숫자만 담고 문장은 담지 않는다.

    이것이 언어 선택 기능의 핵심이다. 판정 시점에 문장을 만들어 버리면
    나중에 다른 언어로 바꿀 수 없다.
    """

    key: str  # 예: "reason.no_signal"
    params: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class LoadResult:
    """PNG 한 장을 읽은 결과. rgb는 항상 .convert('RGB')를 거친 배열이다."""

    path: Path
    rgb: np.ndarray  # (H, W, 3) int32
    width: int
    height: int
    file_bytes: int
    has_transparent_pixels: bool
    palette_size: int | None  # 팔레트 모드가 아니면 None
    load_error: "Msg | None" = None


@dataclass(frozen=True)
class Measurements:
    """픽셀 측정 결과. 파일이나 경로를 모른다."""

    n_pixels: int
    max_red: int
    peak: int  # max(G, B)의 최댓값
    n_lit_1: int  # max(G, B) >= 1 인 픽셀 수
    gate_used: int | None  # 사용된 게이트. None이면 신호 부족
    n_gated: int
    n_blue: int
    n_green: int
    n_intermediate: int
    energy_blue: int
    energy_green: int
    file_bytes: int
    has_transparent_pixels: bool

    @property
    def is_low_confidence(self) -> bool:
        """게이트가 완화된 경우 저신뢰로 본다."""
        return self.gate_used is not None and self.gate_used != 5

    @property
    def f_blue(self) -> float:
        """파랑 픽셀 비율. 파랑도 초록도 없으면 0.0."""
        denom = self.n_blue + self.n_green
        return self.n_blue / denom if denom else 0.0

    @property
    def f_blue_energy(self) -> float:
        """밝기로 가중한 파랑 비율."""
        denom = self.energy_blue + self.energy_green
        return self.energy_blue / denom if denom else 0.0


@dataclass(frozen=True)
class Decision:
    """한 장에 대한 판정. 사람이 읽는 문장을 담지 않는다."""

    label: str  # "BLUE" | "GREEN" | "HYBRID" | "ABSTAIN" — 언어와 무관한 기계용 값
    reason: Msg
    low_confidence: bool
    warnings: tuple[Msg, ...] = ()

    @property
    def reason_code(self) -> str:
        """집계와 테스트에 쓰는 짧은 이름. 'reason.no_signal' -> 'no_signal'"""
        return self.reason.key.rsplit(".", 1)[-1]

    def folder(self, config: "object") -> str:
        """이 판정이 들어갈 출력 폴더 이름.

        폴더 이름은 언어를 따라가지 않는다. 언어를 바꿔 다시 돌리면 폴더가
        둘로 갈라져 결과가 쪼개지기 때문이다. Config에서만 바꿀 수 있다.
        """
        if self.label == "BLUE":
            return config.folder_blue
        if self.label == "GREEN":
            return config.folder_green
        return config.folder_review  # HYBRID와 ABSTAIN은 모두 사람 검토 대상


@dataclass(frozen=True)
class FileResult:
    """한 장에 대한 전체 결과. CSV 한 줄에 대응한다."""

    path: Path
    measurements: Measurements
    decision: Decision


@dataclass(frozen=True)
class CopyItem:
    """원본 한 개를 사본 한 개로 복사하는 계획."""

    source: Path
    dest: Path
    label: str
