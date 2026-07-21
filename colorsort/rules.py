"""판정 규칙. 순수 함수이며 파일 시스템을 모른다.

검사 순서가 중요하다. 위쪽이 아래쪽을 가린다.
  1. 투명 픽셀   - 배경과 구분 불가이므로 최우선
  2. 색 공간     - 빨강이 있으면 예상 밖 입력
  3. 신호 부족   - 판정할 근거가 없음
  4. 중간색 과다 - 제3의 색이지 하이브리드가 아님
  5. 순수 / 하이브리드
"""

import statistics
from dataclasses import replace

from .config import Config
from .models import Decision, FileResult, Measurements, Msg


def decide(m: Measurements, config: Config) -> Decision:
    """측정값 하나로 판정을 내린다.

    사람이 읽는 문장을 만들지 않는다. 열쇠와 숫자를 담은 Msg만 만들고,
    실제 문장은 출력 직전에 선택된 언어로 렌더링된다.
    """
    low = m.is_low_confidence

    if m.has_transparent_pixels:
        return Decision("ABSTAIN", Msg("reason.transparent"), True)

    if m.max_red > 0:
        return Decision("ABSTAIN", Msg("reason.colorspace", {"max_red": m.max_red}), True)

    if m.gate_used is None:
        # "완전 검정"이라고 단정하지 않는다. 검출 한계 이하라고만 말하고 근거를 붙인다.
        return Decision("ABSTAIN", Msg("reason.no_signal", {
            "needed": config.n_min,
            "found": m.n_lit_1,
            "peak": m.peak,
            "file_bytes": m.file_bytes,
        }), True)

    if m.n_gated and m.n_intermediate / m.n_gated > config.max_intermediate_frac:
        return Decision("ABSTAIN", Msg("reason.intermediate", {
            "percent": 100 * m.n_intermediate / m.n_gated,
        }), True)

    total = m.n_blue + m.n_green
    if total == 0:
        return Decision("ABSTAIN",
                        Msg("reason.all_intermediate", {"n_gated": m.n_gated}), True)

    f_b = m.f_blue
    f_b_energy = m.f_blue_energy
    gap = abs(f_b - f_b_energy)

    is_pure_blue = f_b >= 1 - config.purity_eps and m.n_green < config.minority_floor
    is_pure_green = f_b <= config.purity_eps and m.n_blue < config.minority_floor

    common = {"n_gated": m.n_gated, "n_blue": m.n_blue, "n_green": m.n_green,
              "peak": m.peak, "f_blue": f_b}

    if is_pure_blue or is_pure_green:
        # 일관성 검사는 순수 분기에서만 한다.
        # 하이브리드에 적용하면 밝기가 치우친 진짜 하이브리드를 대량으로 억제한다.
        if gap > config.consistency_max:
            return Decision("ABSTAIN", Msg("reason.inconsistent", {
                "f_blue": f_b, "f_blue_energy": f_b_energy,
            }), True)
        key = "reason.pure_blue" if is_pure_blue else "reason.pure_green"
        label = "BLUE" if is_pure_blue else "GREEN"
        return Decision(label, Msg(key, common), low)

    if min(m.n_blue, m.n_green) >= config.minority_floor:
        return Decision("HYBRID", Msg("reason.mixed", common), low)

    return Decision("ABSTAIN", Msg("reason.ambiguous", common), True)


def crosscheck_file_sizes(results: list[FileResult], config: Config) -> list[FileResult]:
    """말뭉치 수준 교차 검사.

    픽셀은 비었는데 파일 크기가 크면 뭔가 놓쳤을 가능성이 있다. 픽셀 논리와 무관한
    독립 증거이므로, 둘이 어긋날 때가 바로 사람이 봐야 할 때다.
    """
    sizes = [r.measurements.file_bytes for r in results if r.measurements.file_bytes > 0]
    if not sizes:
        return results

    median = statistics.median(sizes)
    threshold = median * config.empty_size_warn_ratio

    out = []
    for r in results:
        if r.decision.reason_code == "no_signal" and r.measurements.file_bytes > threshold:
            warning = Msg("warn.empty_but_large", {
                "file_bytes": r.measurements.file_bytes,
                "median": median,
            })
            new_warnings = r.decision.warnings + (warning,)
            out.append(replace(r, decision=replace(r.decision, warnings=new_warnings)))
        else:
            out.append(r)
    return out
