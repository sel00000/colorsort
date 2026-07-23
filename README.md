# Colorsort

**사진의 실제 픽셀 색을 읽어 파랑 / 초록으로 자동 분류하는 Windows 프로그램**
**A Windows app that sorts photos into Blue / Green by reading their actual pixel colors**

[📦 다운로드 · Download (Releases)](../../releases/latest) &nbsp;·&nbsp; [한국어 설명](#한국어) &nbsp;·&nbsp; [English guide](#english)

![Colorsort 메인 화면 / main window](docs/screenshots/library-ko.png)

---

## 한국어

### 무엇을 하는 프로그램인가요?

사진의 **픽셀 색**을 직접 읽어 파랑과 초록으로 나눠 폴더에 정리합니다.

- 파일 이름은 판정에 쓰지 않습니다. 이름이 무엇이든 사진의 실제 색만 봅니다.
- 지원 형식: **PNG · JPG · JPEG · BMP · GIF · WEBP · TIFF** — 하위 폴더까지 모두 찾습니다.
- 판단이 애매한 사진은 `review`(확인 필요)로 분리해 사람에게 넘깁니다.
- **원본 사진은 절대 수정되지 않습니다.** 언제나 사본만 만듭니다.

### 다운로드

[Releases 페이지](../../releases/latest)에서 **`Colorsort-2.1.0.zip`** 을 받으세요.
실행 파일(`Colorsort.exe`)과 첫 실행 안내, 사용 설명서(영/한)가 함께 들어 있습니다.

Windows 10/11이면 됩니다. 설치할 것도, 인터넷도 필요 없습니다.

### 사용 방법

> **⚠️ 중요: 사진을 한 장씩 클릭하는 것이 아닙니다.**
> **사진들이 모여 있는 "폴더"를 선택하면 프로그램이 알아서 작동합니다.**
> 폴더만 고르면 그 안(하위 폴더 포함)의 모든 사진을 자동으로 찾아 분류합니다.

1. zip 압축을 풀고 `Colorsort.exe`를 더블클릭합니다.
   - 처음 한 번 "Windows의 PC 보호" 파란 창이 뜨면 **"추가 정보" → "실행"** 을 누르세요.
   - 첫 실행은 몇 초 걸릴 수 있습니다. 정상입니다.
2. 언어를 고릅니다 (한국어 / English). 나중에 설정에서 바꿀 수 있습니다.
3. **"폴더 선택" 버튼을 눌러 사진 모음 폴더를 고르거나, 그 폴더를 창에 끌어다 놓으세요.**
   바로 분류가 시작됩니다.
4. 끝나면 카드에 숫자가 뜹니다: 검사 / 파랑 / 초록 / 확인 필요.
   결과는 고른 폴더 안 `results`에 **사본**으로 저장됩니다.

```
사진폴더\results\blue                파랑 사진 (사본)
사진폴더\results\green               초록 사진 (사본)
사진폴더\results\review\no-signal    거의 새까만 사진
사진폴더\results\review\mixed        파랑+초록이 함께 있는 사진
사진폴더\results\review\other        그 밖의 애매한 사진
사진폴더\results\results.csv         모든 판정과 그 이유 (엑셀에서 열림)
```

### 애매한 사진은 직접 확정

![검사관 화면 — 판정 근거 색칠](docs/screenshots/inspector-ko.png)

- 썸네일을 **더블클릭**하면 크게 열립니다. 어두운 사진도 자동 보정되어 형태가 보입니다.
- "판정 색칠" 버튼은 프로그램이 어느 픽셀을 파랑/초록으로 셌는지 그대로 보여줍니다.
- **[파랑으로] / [초록으로]** 버튼으로 직접 확정하면 사본이 그 폴더로 이동합니다.
- 확정은 사진 내용의 지문으로 기억됩니다 — 다시 분류해도, 파일 이름이 바뀌어도 유지됩니다.

### 원본은 안전합니다

이 프로그램은 사진을 **복사만** 합니다. 옮기거나, 지우거나, 이름을 바꾸지 않습니다.
같은 폴더를 다시 분류해도 이전 결과 폴더를 알아보고 건너뛰므로 사본이 이중으로 세어지지 않습니다.

### 명령줄(CLI) 버전 — 파이썬 사용자용

GUI와 같은 판정 로직을 쓰는 CLI도 들어 있습니다. 파이썬 3.10 이상이 필요합니다.

```
py -3 -m pip install pillow numpy          # 처음 한 번만
py -3 -m colorsort 사진폴더 --output results          # 미리보기 (사진은 건드리지 않음)
py -3 -m colorsort 사진폴더 --output results --apply  # 실제 복사
```

`--apply`를 붙였을 때만 사본을 만듭니다. `--lang en`으로 영어 출력, `--lang-reset`으로 언어 선택을 초기화합니다.

### 개발자 안내

```
py -3 -m pytest                                      # 테스트
py -3.12 packaging\make_icon.py                      # 아이콘 생성
py -3.12 -m PyInstaller packaging\colorsort.spec --noconfirm   # exe 빌드 → dist\Colorsort.exe
```

구조·판정 규칙 다이어그램(한/영 9종)은 [`docs/diagrams`](docs/diagrams)에 있습니다.

---

## English

### What it does

Sorts photos into **Blue / Green** by reading their **pixel colors** directly.

- File names are ignored — only the actual colors count.
- Reads **PNG · JPG · JPEG · BMP · GIF · WEBP · TIFF**, subfolders included.
- Photos it cannot judge go to `review` for your eyes.
- **Your original photos are NEVER modified.** The app only makes copies.

### Download

Get **`Colorsort-2.1.0.zip`** from the [Releases page](../../releases/latest).
It contains the executable (`Colorsort.exe`), a first-run note, and the user guide (EN/KO).

Windows 10 or 11. Nothing to install, no internet needed.

### How to use

> **⚠️ Important: you do NOT click photos one by one.**
> **Select the folder that contains your photos, and the program does the rest.**
> Pick one folder and every photo inside it (subfolders included) is found and sorted automatically.

1. Unzip and double-click `Colorsort.exe`.
   - If Windows shows "Windows protected your PC" the first time, click **"More info" → "Run anyway"**.
   - The first launch can take a few seconds. This is normal.
2. Pick your language (English / 한국어). You can change it later in Settings.
3. **Click "Choose folder" and select the folder your photos are in — or drag that folder onto the window.**
   Sorting starts right away.
4. When done, the cards show the counts: Scanned / Blue / Green / Review.
   Results are saved as **copies** inside your photo folder, under `results`:

```
your-folder\results\blue                blue photos (copies)
your-folder\results\green               green photos (copies)
your-folder\results\review\no-signal    nearly black photos
your-folder\results\review\mixed        blue + green in one photo
your-folder\results\review\other        anything else unclear
your-folder\results\results.csv         every judgment, with the reason (opens in Excel)
```

### Deciding the unclear ones yourself

- **Double-click** any thumbnail to open it big — dark photos open already brightened.
- The "Judgment" view paints exactly which pixels were counted as blue / green.
- **[To Blue] / [To Green]** moves that photo's copy to the chosen folder.
- Decisions are remembered by the photo's content fingerprint — they survive re-sorting and file renames.

### Your originals are safe

The app only **copies** photos. It never moves, deletes, or renames your files.
Re-sorting the same folder never counts the copies twice — previous result folders are recognized and skipped.

### Command-line (CLI) version — for Python users

The same judgment logic is available as a CLI. Requires Python 3.10+.

```
py -3 -m pip install pillow numpy          # once
py -3 -m colorsort your-folder --output results          # preview (touches nothing)
py -3 -m colorsort your-folder --output results --apply  # actually copy
```

Copies are made only with `--apply`. Use `--lang en` for English output, `--lang-reset` to reset the language choice.

### For developers

```
py -3 -m pytest                                      # run tests
py -3.12 packaging\make_icon.py                      # generate the icon
py -3.12 -m PyInstaller packaging\colorsort.spec --noconfirm   # build → dist\Colorsort.exe
```

Architecture and rule diagrams (9 kinds, KO/EN) live in [`docs/diagrams`](docs/diagrams).
