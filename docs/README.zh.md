# Retro Game Creator

[English](../README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · **简体中文** · [Português](README.pt.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [हिन्दी](README.hi.md)

**让 AI 编程代理做一个游戏，你会得到一个真正的 Game Boy Color ROM（`.gbc`）。**

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/output-.gbc-8b6b2e.svg" alt="Output: .gbc ROM">
  <img src="https://img.shields.io/badge/compiler-GBDK--2020%204.5.0-2f9e44.svg" alt="Compiler: GBDK-2020 4.5.0">
  <img src="https://img.shields.io/badge/games_shipped-2-ff6b6b.svg" alt="Games shipped: 2">
  <img src="https://img.shields.io/badge/agents-Claude%20Code%20%2B%20Codex-6e56cf.svg" alt="Agents: Claude Code and Codex">
</p>

<p align="center">
  <img src="images/bungeoppang-plus-gameplay.gif" width="320" alt="《鲷鱼烧大亨 Plus》运行画面：夜市摊位、四个烤模、顾客点单与售卖">
</p>
<p align="center">
  <em>《鲷鱼烧大亨 Plus》——用这套工具做成，画面取自已发布的 ROM。
  <a href="https://github.com/dong3789/bungeoppang-tycoon-plus-gbc">仓库</a> ·
  <a href="https://github.com/dong3789/bungeoppang-tycoon-plus-gbc/releases/tag/v1.0">直接玩</a></em>
</p>

一份技能文档（`SKILL.md`）、三个自动化工具、一个起步模板——以及**两个真正发布的游戏**，它们现在就能在你包里的掌机上运行。

它把 OpenAI × ModRetro 的 [Chromatic](https://openai.com/en-US/supply/co-lab/chromatic/)（一台兼容 Game Boy 硬件的掌机）演示的流程——“AI 写 C，GBDK 烧录 ROM，再用眼睛检查模拟器帧”——搬到你自己已经有的设备上，而不是再买一台 200 美元的机器。

`R36S · Miyoo Mini · Anbernic · iPhone（Delta） · 桌面与网页模拟器 · 实机` —— 一个 `.gbc` 文件，以上全都能跑。

---

## 展示 — 用这套工具做出来的游戏

两个游戏，都以 `.gbc` 发布。它们出自本仓库强制执行的同一套循环：照着 `SKILL.md` 写 C，用 GBDK-2020 编译，用 `tools/playtest.py` 无头重放 ROM，看帧，改，再来。下面所有动图和条带都取自**已发布的 ROM**，不是画的示意图。

### 1. 鲷鱼烧大亨 Plus（Bungeoppang Tycoon Plus）

> 夜市鲷鱼烧摊，限时 90 秒。

[仓库](https://github.com/dong3789/bungeoppang-tycoon-plus-gbc) · [发布 v1.0 · `bungeoppang-plus.gbc`（32 KiB）](https://github.com/dong3789/bungeoppang-tycoon-plus-gbc/releases/tag/v1.0)

| | |
| --- | --- |
| 类型 | 90 秒冲分料理游戏 |
| 循环 | 烤网上四个模具，四种馅料 BEAN / CREAM / CHEESE / PIZZA。倒面糊，烤到金黄，再按顾客点的馅料卖出 |
| 操作 | 十字键：选模具 · **A**：倒糊 / 卖出 / 铲掉烤糊的 · **B**：切换馅料（长按连发） · **SELECT**：反向切换 · **START**：开始、重来 |
| 深度 | 顾客带着馅料要求和耐心条上门；每卖对一次连击加一；90 秒结束后按营业额给出 S/A/B/C 评级（S = 6000 金） |
| 硬件预算 | 背景图块索引 256 个中的 246 个，OAM 精灵 40 个中的 28 个。四种馅料共用同一套图块，只换调色板——切换不占 VRAM |
| ROM | 仅 CGB（`0xC0`），32 KiB，MBC5+RAM+电池（`0x1B`） |

<p align="center"><img src="images/bungeoppang-plus-strip.png" width="848" alt="《鲷鱼烧大亨 Plus》的五个画面：标题、顾客点单、倒好面糊的三个模具、金黄、卖出 100 金"></p>

条带是从已发布 ROM 里抽出的五帧：标题画面、顾客要 CREAM、倒好面糊的三个模具、金黄、以及成交（`GOLD 100 · COMBO 1`）。

### 2. RAMEN TIME

> 三轮、五步、一个按键——以及比你更快的游标。

[仓库](https://github.com/dong3789/ramen-time-gbc) · [发布 v1.0 · `ramen-time.gbc`（32 KiB）](https://github.com/dong3789/ramen-time-gbc/releases/tag/v1.0)

| | |
| --- | --- |
| 类型 | 节奏 / 时机料理游戏 |
| 循环 | **BOIL → NOODLES → SOUP → TOPPING → STOP**，每轮五步，共三轮。游标经过绿区时按下 |
| 操作 | **A**：掐时机（TOPPING 阶段放蛋） · **B**：加葱 · **START**：开始 / 再来一局 · **SELECT**：回标题 |
| 深度 | 112 像素量尺正中的 16 像素是 PERFECT（100 分），GOOD 60 分，错过 0 分。游标速度：第一轮 2 帧 1 像素、第二轮 1 帧 1 像素、第三轮 1 帧 2 像素。停得太早面是 HARD，太晚就 SOGGY。满分 1260 |
| 硬件预算 | VRAM 384 格中的背景 215 + 精灵 3，OAM 40 个中的 3 个——每阶段只换锅的一行图块 |
| ROM | 支持 CGB（`0x80`），32 KiB，MBC5+RAM+电池（`0x1B`） |

<p align="center"><img src="images/ramen-time-gameplay.gif" width="320" alt="RAMEN TIME 运行画面：锅在沸腾，游标扫过量尺，PERFECT 100 分，接着面下锅"></p>

<p align="center"><img src="images/ramen-time-strip.png" width="848" alt="RAMEN TIME 的五个画面：标题、游标移动中的 BOIL、PERFECT +100、NOODLES、评级 S、1260 分的结算卡"></p>

最右边的结算卡是真跑完 15 个阶段的结果——通过从模拟器内存里读取游标精灵来操作：评级 **S**、得分 **1260**、*PERFECT NOODLES*。

**两个游戏的共同点才是重点：** 输入 → 计分 → 评级的完整循环、只换调色板的美术变化，以及人真的能看懂的试玩条带。这就是这套工具要求的门槛。

---

## 30 秒上手

```bash
git clone https://github.com/dong3789/retro-game-creator.git
cd retro-game-creator

./tools/check_env.sh                 # 检查 GBDK、python、pillow、pyboy
./templates/minimal-gbc/build.sh     # 构建示例 ROM → build/tile-hop.gbc

python3 tools/playtest.py --rom templates/minimal-gbc/build/tile-hop.gbc \
  --script "wait:8,press:start:4,wait:16,hold:right:36,snap:score" \
  --out build/strip.png
```

打开 `build/strip.png`。那就是游戏。

从[发布页](https://github.com/gbdk-2020/gbdk-2020/releases)下载 GBDK-2020，解压到任意位置，
`export GBDKDIR=/path/to/gbdk/`（**末尾的 `/` 不能少**）。`build.sh` 也会在 `/opt/gbdk`、`~/gbdk` 等位置查找，没有 `make` 也能构建。

## 起步模板 — TILE HOP

`templates/minimal-gbc/` 是你复制后开工的底座。它不是空壳：从标题到游玩、计分、通关整条链路都通着，需要保留的部件（vsync 循环、按键边沿检测、图块地图、精灵、声音、HUD）都已经接好。

| | |
| --- | --- |
| 操作 | 十字键移动，`START` 开始，`SELECT` 回标题 |
| 目标 | 吃光 6 颗星得到 `CLEAR!`，星重新铺开、分数清零（无限循环） |
| 已包含 | 5 套调色板、BG/OBJ 调色板分离、图块碰撞、精灵动画、声音、HUD |
| 大小 | ROM 32 KiB · 图块 182 / 384 |

| 标题 | 游玩 | 通关 |
| --- | --- | --- |
| ![title](images/title-screen.png) | ![strip](images/playtest-strip.png) | ![clear](images/clear-screen.png) |

中间的条带是 `tools/playtest.py` 真跑 ROM 时抓的帧——
标题 → 开始 → 向右走吃到星星（SCORE 00→01、STAR 6→5）→ 移动 → 回到标题。
**标准不是“编译过了”，而是“屏幕上看到了”。**

## 随处运行

`.gbc` 是标准 Game Boy Color ROM，同一个文件在下面任何地方都能跑——上面两个展示游戏也一样。

| 设备 | 方法 |
| --- | --- |
| **R36S（ArkOS）** | 复制到 microSD `EASYROMS` 分区的 GBC 文件夹 → Gambatte 或 SameBoy 核心（详见下文） |
| **Miyoo Mini（Onion）、Anbernic RG35XX 等** | 同理——放进掌机的 GBC ROM 文件夹 |
| **iPhone / iPad** | 用 Delta 应用打开 `.gbc` |
| **PC / Mac** | SameBoy、mGBA |
| **实机** | Game Boy Color + 烧录卡 |

### 放进 R36S

1. 把 microSD 插进电脑，打开 **EASYROMS** 分区（不是 `BOOT`）。
2. 把 `.gbc` 复制进 GBC 文件夹——通常是 `EASYROMS/roms/gbc/`，某些镜像里是 `EASYROMS/gbc/`。
   文件夹名区分大小写。游戏不出现，是文件夹不对，不是 ROM 有问题。
3. 启动。核心用 **Gambatte**（默认，够用）或 **SameBoy**（最准确）。
4. 显示设置：GBC 是 160×144，正好 **10:9**，而 R36S 屏幕是 640×480（4:3）。
   在 `设置 → 视频 → 缩放` 里选 **Aspect Ratio: Core Provided** 和 **Integer Scale: ON → 480×432（3 倍）**。
   像素落在干净的正方网格上。4 倍（640×576）在 480 行里放不下，实际也会退回 3 倍。
   “铺满屏幕”会把 10:9 拉成 4:3，大约横向拉伸 20%——像素画不建议。

## 仓库内容

```
SKILL.md                  给 AI 代理看的正文——硬件限制、GBDK API、制作与验收循环
AGENTS.md / CLAUDE.md     Codex 与 Claude Code 在仓库根目录直接读取的摘要规则
tools/
  png2gbc.py              PNG → 8×8 2bpp 图块 + BGR555 调色板 C 代码（含图块网格预览）
  artfont.py              用 5×7 像素字体把标志和文字画进 PNG
  playtest.py             PyBoy 无头运行 + 按键脚本 + 截图条带
  check_env.sh            检查 GBDK / python / pillow / pyboy
templates/minimal-gbc/    起步游戏 “TILE HOP”（标题 → 游玩 → 计分 → 通关）
docs/images/              从真实 ROM 抓的画面与 GIF（两个展示游戏 + TILE HOP）
docs/ci.md                CI 工作流全文 + 一次性注册方法（尚未登记进仓库）
```

两个展示游戏分别在各自的仓库里——
[`bungeoppang-tycoon-plus-gbc`](https://github.com/dong3789/bungeoppang-tycoon-plus-gbc) 和
[`ramen-time-gbc`](https://github.com/dong3789/ramen-time-gbc)——源码、构建脚本、`docs/` 截图都在里面。

## 接上你的 AI 代理

| 工具 | 读取方式 |
| --- | --- |
| **Claude Code** | 打开仓库就会读 `CLAUDE.md`。说“把 TILE HOP 复制一份改成射击游戏”，它按 `SKILL.md` 的规则做。 |
| **Codex / 其他代理** | 它们读 `AGENTS.md`。如果你的工具两个都不读，在对话开头加一句让它读 `SKILL.md`。 |
| **Claude Skill 格式** | `SKILL.md` 带 frontmatter（`name`、`description`），可以直接放进 skills 文件夹使用。 |

技能强制的内容：384 图块的 VRAM 预算、每图块 4 色、8×8 对齐、OAM 40 个且每条扫描线 10 个、
`vsync()` 循环、CGB 寄存器守卫，以及**构建后一定要亲眼看试玩条带**。

## 制作循环（技能里写的那套）

1. **一段设计 + 一行通过标准** —— “向右走 36 帧吃掉一颗星，分数从 0 变 1”
2. **PNG 美术** → 用 `tools/png2gbc.py` 转成图块与调色板，用预览肉眼检查
3. **C 代码** —— 复制 `templates/minimal-gbc/src/main.c` 改写
4. **构建** —— `./build.sh`（lcc）
5. **试玩** —— 跑按键脚本 → 得到条带 PNG
6. **自己打开条带看** → 修，重复
7. **留下证据** —— 条带和截图放进 `docs/images/`，在 README 里链接

两个展示游戏也是把这条循环转到“条带值得给人看”为止。当自动化比截图更有价值时，不要去猜，直接读游戏运行时的状态：上面的 RAMEN TIME 动图是从精灵属性表读出时机游标、在 PERFECT 区间按 `A`；鲷鱼烧动图是从帧缓冲采样顾客点的馅料，再用 `B` 选到它。

## 三个工具

```bash
# 1) 美术：精灵 3 色 + 透明，背景 4 色。--dedup 合并重复图块，--palette 固定调色板
python3 tools/png2gbc.py assets/player.png --mode sprite --name player -o src/gen/player
python3 tools/png2gbc.py assets/level.png  --mode bg --map --dedup --name level -o src/gen/level

# 2) 文字：用 5×7 字体把标志和文字画进 PNG（整数倍缩放）
python3 tools/artfont.py "PRESS START" --scale 2 --color "#FFEBC2" --out press.png

# 3) 试玩：wait / press / hold / release / snap
python3 tools/playtest.py --rom build/tile-hop.gbc \
  --script "wait:40,press:start:4,wait:20,snap:play,hold:right:40,release:right,snap:score" \
  --out build/strip.png
```

`playtest.py` 还会点出典型故障：“每帧都一样（= 输入没进去）”、“只有两种颜色或更少（= 调色板或显示问题）”、
“空白帧”。把它当成 bug 去修。

## 硬件速查（更多见 `SKILL.md`）

| 项目 | 值 |
| --- | --- |
| 屏幕 | 160×144（20×18 图块） |
| 图块 | 8×8，2bpp = 每块 4 色，16 字节 |
| VRAM | 384 图块（8 KiB）——背景与精灵**共用同一块** |
| 调色板 | 8 个 BG + 8 个 OBJ × 4 色，BGR555 15 位 |
| 精灵 | OAM 40 个，**每条扫描线 10 个** |
| 帧 | 59.7 fps，约 70,224 周期 |
| 声音 | 4 通道（方波 2、波表 1、噪声 1） |

## CI

[`docs/ci.md`](ci.md) 里有完整工作流——Ubuntu runner 拉取 GBDK-2020 4.5.0，构建
`templates/minimal-gbc`，检查 ROM 头（大小、标题、卡带类型 `0x1B`、CGB 标志 `0x80`），跑
PyBoy 试玩（`--strict`），并把 `.gbc` 和截图条带作为产物上传。

> 本仓库尚未**登记** `.github/workflows/build-rom.yml`。首次推送使用的 GitHub token 缺少 `workflows` 权限，
> GitHub 拒绝了该文件。把 `docs/ci.md` 里的文件在网页界面粘贴一次，之后每次推送都会运行。

## 致谢

- 编译器：[GBDK-2020](https://github.com/gbdk-2020/gbdk-2020)（基于 SDCC）
- 模拟器：[PyBoy](https://github.com/Baekalfen/PyBoy) —— 用于无头验收
- 参考：Pan Docs（Game Boy 硬件文档）、GBDK 2020 Docs
- 灵感：OpenAI × ModRetro **Chromatic: Codex Edition**

MIT License —— 见 [LICENSE](../LICENSE)。做游戏、改游戏、卖游戏都行。
问题和 bug 请提到 [Issues](https://github.com/dong3789/retro-game-creator/issues)；用这套工具做的游戏随时欢迎分享。
