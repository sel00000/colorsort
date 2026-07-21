"""판정 임계값. 코드가 아니라 데이터로 둔다.

LUT이 바뀌면 코드를 고치지 않고 이 값만 조정한다.
각 값의 근거는 설계 문서 3.3절 참조.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # 픽셀별 색 판정 경계. rho = B / (G + B)
    # 초록 LUT의 실측 rho는 약 0.154, 파랑은 정확히 1.0이므로 여유가 크다.
    rho_blue: float = 0.90
    rho_green: float = 0.35

    # 밝기 게이트. 위에서부터 시도하고 픽셀이 부족하면 다음으로 완화한다.
    gates: tuple[int, ...] = (5, 2, 1)

    # 판정에 필요한 최소 픽셀 수. 200은 정상 사진 4장을 놓치므로 30을 쓴다.
    n_min: int = 30

    # 소수파 절대 하한. 떠돌이 픽셀 몇 개가 순수 사진을 하이브리드로 뒤집는 것을 막는다.
    minority_floor: int = 50

    # 중간색 비율이 이보다 크면 제3의 색으로 보고 기권한다.
    max_intermediate_frac: float = 0.10

    # 순수 판정 허용 오차. f_blue가 0.02 이하 또는 0.98 이상이어야 순수로 본다.
    purity_eps: float = 0.02

    # 순수 분기에서만 적용하는 일관성 검사 한계.
    # 하이브리드 분기에 적용하면 진짜 하이브리드의 85%를 억제하므로 절대 확대 적용 금지.
    consistency_max: float = 0.10

    # 신호 없음으로 판정된 파일의 크기가 말뭉치 중앙값의 이 비율을 넘으면 경고한다.
    # 픽셀은 비었는데 파일이 크다 = 뭔가 놓쳤을 가능성.
    empty_size_warn_ratio: float = 0.5

    # 출력 폴더 이름. 언어를 따라 바뀌지 않는다.
    # 언어를 바꿔 다시 돌리면 폴더가 둘로 갈라져 결과가 쪼개지기 때문이다.
    # 한글 폴더명을 원하면 folder_review="확인필요" 처럼 지정한다.
    folder_blue: str = "blue"
    folder_green: str = "green"
    folder_review: str = "review"


DEFAULT_CONFIG = Config()
