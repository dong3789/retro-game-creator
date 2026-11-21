# R36S GBC 크리에이터

> AI에게 게임을 시키면 **진짜 게임보이 컬러 ROM(`.gbc`)** 이 나오고, 그게 R36S나 아무 에뮬레이터에서 바로 돌아갑니다.
> A skill kit that turns an AI coding agent into a Game Boy Color game developer — build, playtest, ship.

![TILE HOP gameplay](docs/images/gameplay.gif)

OpenAI × ModRetro가 Chromatic(게임보이 하드웨어 호환 휴대기기)으로 보여 준 "AI가 C를 쓰고 → GBDK로 ROM을 굽고 → 에뮬레이터 프레임을 눈으로 검수한다"는 흐름을,
**$200 기기를 사지 않고 이미 있는 R36S에서** 그대로 쓰도록 만든 오픈 스킬킷입니다.
스킬 문서(`SKILL.md`) + 자동화 도구 3개 + 실제로 빌드·플레이테스트까지 통과한 예제 게임이 들어 있습니다.

---

## 들어 있는 것

```
SKILL.md                  AI 에이전트용 본문 — 하드웨어 제약, GBDK API, 제작·검수 루프
AGENTS.md / CLAUDE.md     Codex · Claude Code가 레포 루트에서 바로 읽는 요약 규칙
tools/
  png2gbc.py              PNG → 8×8 2bpp 타일 + BGR555 팔레트 C 코드 (+ 타일 그리드 미리보기)
  artfont.py              5×7 픽셀 폰트로 로고·문구를 PNG에 그리기
  playtest.py             PyBoy 헤드리스 실행 + 키 입력 시퀀스 + 스크린샷 스트립
  check_env.sh            GBDK / python / pillow / pyboy 점검
templates/minimal-gbc/    실제로 도는 예제 게임 "TILE HOP" (타이틀 → 플레이 → 점수 → 클리어)
docs/images/              검수 스크린샷 (위 GIF 포함)
.github/workflows/        푸시할 때마다 ROM을 빌드해 아티팩트로 올리는 CI
```

## 예제 게임 — TILE HOP

| | |
| --- | --- |
| 조작 | 방향키 이동, `START` 시작, `SELECT` 타이틀로 |
| 목표 | 별 6개를 다 먹으면 `CLEAR!`, 별이 다시 깔리고 점수 리셋 (무한 반복) |
| 구현된 것 | 컬러 팔레트 5종, BG/OBJ 팔레트 분리, 타일 충돌, 스프라이트 애니메이션, 사운드, HUD |
| 크기 | ROM 32 KiB, 타일 182개 / VRAM 384개 |

| 타이틀 | 플레이 | 클리어 |
| --- | --- | --- |
| ![title](docs/images/title-screen.png) | ![strip](docs/images/playtest-strip.png) | ![clear](docs/images/clear-screen.png) |

오른쪽 스트립은 `tools/playtest.py`가 실제로 ROM을 돌리며 찍은 프레임입니다 —
타이틀 → 시작 → 오른쪽으로 걸어가 별 획득(SCORE 00→01, STAR 6→5) → 이동 → 타이틀 복귀.
**"빌드됐다"가 아니라 "화면에서 확인했다"** 가 이 킷의 기준입니다.

## 30초 시작

```bash
git clone https://github.com/dong3789/gbc-game-creator.git
cd gbc-game-creator

./tools/check_env.sh                 # 뭐가 깔려 있고 뭐가 없는지
./templates/minimal-gbc/build.sh     # 예제 ROM 빌드 → build/tile-hop.gbc

python3 tools/playtest.py --rom templates/minimal-gbc/build/tile-hop.gbc \
  --script "wait:8,press:start:4,wait:16,hold:right:36,snap:score" \
  --out build/strip.png
```

`build/strip.png`를 열어 보세요. 이게 게임입니다.

GBDK-2020은 <https://github.com/gbdk-2020/gbdk-2020/releases> 에서 받아 아무 데나 풀고
`export GBDKDIR=/경로/gbdk/` ( **끝에 `/` 꼭** ) 하면 됩니다. `build.sh`가 `/opt/gbdk`, `~/gbdk` 등도 알아서 찾습니다.
`make`가 없어도 `build.sh`로 빌드됩니다.

## AI 에이전트에 붙이기

| 도구 | 하는 일 |
| --- | --- |
| **Claude Code** | 레포에서 열면 `CLAUDE.md`를 읽습니다. "TILE HOP 복사해서 슈팅 게임으로 바꿔줘"처럼 시키면 `SKILL.md` 규칙대로 진행합니다. |
| **Codex / 기타** | `AGENTS.md`를 읽습니다. 안 읽는 도구라면 대화 첫머리에 `SKILL.md`를 읽으라고 한 줄 붙이면 됩니다. |
| **Claude Skill 형식** | `SKILL.md`가 frontmatter(`name`, `description`)를 갖춘 표준 스킬 문서라 그대로 스킬 폴더에 넣어도 됩니다. |

스킬이 강제하는 것: 384타일 VRAM 예산, 4색/타일, 8×8 정렬, OAM 40개·스캔라인 10개,
`vsync()` 루프, CGB 레지스터 가드, 그리고 **빌드 후 반드시 플레이테스트 스트립을 눈으로 볼 것**.

## R36S에 넣기

1. 마이크로SD를 PC에 꽂고 **EASYROMS** 파티션을 엽니다 (`BOOT` 파티션이 아닙니다).
2. GBC 폴더에 `.gbc`를 복사합니다 — 보통 `EASYROMS/roms/gbc/` (이미지에 따라 `EASYROMS/gbc/`).
   폴더 이름은 소문자·대소문자를 구분합니다. 게임이 안 보이면 롬이 아니라 폴더가 틀린 겁니다.
3. 실행. 코어는 **Gambatte**(기본, 무난) 또는 **SameBoy**(가장 정확).
4. 화면 설정: GBC는 160×144 = 정확히 **10:9**, R36S 패널은 640×480(4:3)입니다.
   `설정 → 비디오 → 스케일링`에서 **Aspect Ratio: Core Provided + Integer Scale: ON → 480×432 (3배)**.
   픽셀이 정사각으로 딱 떨어집니다. 4배(640×576)는 세로 480에 안 들어가서 결국 3배로 떨어집니다.
   "화면 꽉 채우기"는 10:9를 4:3에 밀어넣어 약 20% 늘어납니다 — 픽셀아트에는 비추천.

같은 ROM이 Miyoo Mini(Onion), Anbernic RG35XX, 데스크톱 `sameboy`/`mgba`, 실기 + 플래시카트에서도 그대로 돕니다.

## 만드는 순서 (스킬에 적힌 루프)

1. **기획 한 문단 + 합격 기준 한 줄** — "오른쪽으로 36프레임 걸으면 별을 먹고 점수가 0→1이 된다"
2. **PNG 아트** → `tools/png2gbc.py`로 타일·팔레트 변환, 미리보기로 눈 확인
3. **C 코드** — `templates/minimal-gbc/src/main.c`를 복사해서 고침
4. **빌드** — `./build.sh` (lcc)
5. **플레이테스트** — 키 입력 스크립트 실행 → 스트립 PNG 생성
6. **스트립을 직접 열어 검수** → 고치고 반복
7. **증거 남기기** — 스트립/스크린샷을 `docs/images/`에, README에 링크

## 도구 세 개

```bash
# 1) 아트:  sprite는 3색+투명, bg는 4색. --dedup으로 타일 중복 제거, --palette로 팔레트 고정
python3 tools/png2gbc.py assets/player.png --mode sprite --name player -o src/gen/player
python3 tools/png2gbc.py assets/level.png  --mode bg --map --dedup --name level -o src/gen/level

# 2) 글자: 로고/문구를 5×7 폰트로 PNG에 그리기 (정수 배율)
python3 tools/artfont.py "PRESS START" --scale 2 --color "#FFEBC2" --out press.png

# 3) 플레이테스트: wait/press/hold/release/snap
python3 tools/playtest.py --rom build/tile-hop.gbc \
  --script "wait:40,press:start:4,wait:20,snap:play,hold:right:40,release:right,snap:score" \
  --out build/strip.png
```

`playtest.py`는 "모든 프레임이 똑같다(= 입력이 안 들어간다)", "색이 2개 이하(= 팔레트/디스플레이 문제)",
"빈 프레임" 같은 전형적 실패를 경고로 짚어 줍니다. 경고가 뜨면 버그로 보고 고치세요.

## 하드웨어 요약 (자세한 건 `SKILL.md`)

| 항목 | 값 |
| --- | --- |
| 화면 | 160×144 (20×18 타일) |
| 타일 | 8×8, 2bpp = 타일당 4색, 16바이트 |
| VRAM | 384타일(8 KiB) — 배경·스프라이트가 **같은 곳**을 씀 |
| 팔레트 | BG 8개 + OBJ 8개 × 4색, BGR555 15비트 |
| 스프라이트 | OAM 40개, **스캔라인당 10개** |
| 프레임 | 59.7 fps, 약 70,224 사이클 |
| 사운드 | 4채널 (스퀘어2·웨이브·노이즈) |

## CI

`.github/workflows/build-rom.yml` — 푸시/PR마다 우분투 러너에서 GBDK-2020 4.5.0을 받아
`templates/minimal-gbc`를 빌드하고, `.gbc`를 아티팩트로 올리고, PyBoy 플레이테스트까지 돌립니다.
빌드 결과는 Actions 탭 → Artifacts에서 바로 받아 SD카드에 넣을 수 있습니다.

## 크레딧

- 컴파일러: [GBDK-2020](https://github.com/gbdk-2020/gbdk-2020) (SDCC 기반)
- 에뮬레이터: [PyBoy](https://github.com/Baekalfen/PyBoy) — 헤드리스 검수용
- 레퍼런스: Pan Docs (게임보이 하드웨어 문서), GBDK 2020 Docs

라이선스는 아직 정하지 않았습니다(저장소 소유자에게 문의).
