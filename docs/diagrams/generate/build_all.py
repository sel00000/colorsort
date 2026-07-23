"""다이어그램 18장(9종 × 한/영) 일괄 재생성 + 폰트 경고 검사."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = ["01-architecture.py", "02-structure.py", "03-dependency-graph.py",
           "gen_04_class.py", "gen_05_sequence_gui.py", "gen_06_sequence_cli.py",
           "gen_07_flowchart_rules.py", "08-call-graph.py", "gen_09_data_flow.py"]

bad = 0
for sc in SCRIPTS:
    for lang in ("ko", "en"):
        r = subprocess.run([sys.executable, str(HERE / sc), lang],
                           capture_output=True, text=True)
        out = r.stdout + r.stderr
        problem = ("실행 실패" if r.returncode != 0 else
                   "폰트 경고" if ("missing from font" in out or "Glyph" in out)
                   else "")
        if problem:
            bad += 1
            print(f"[문제] {sc} {lang}: {problem}\n{out[-800:]}")
        else:
            print(f"[OK] {sc} {lang}")
sys.exit(1 if bad else 0)
