# Retro Game Creator

[English](../README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · **简体中文** · [Português](README.pt.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [हिन्दी](README.hi.md)

**让 AI 编程助手做一款游戏，你会得到一个真正的 Game Boy Color ROM（`.gbc`）。**

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/output-.gbc-8b6b2e.svg" alt="Output: .gbc ROM">
  <img src="https://img.shields.io/badge/compiler-GBDK--2020%204.5.0-2f9e44.svg" alt="Compiler: GBDK-2020 4.5.0">
  <img src="https://img.shields.io/badge/agents-Claude%20Code%20%2B%20Codex-6e56cf.svg" alt="Agents: Claude Code and Codex">
</p>

<p align="center">
  <img src="images/gameplay.gif" width="480" alt="示例游戏 TILE HOP 在模拟器中运行">
</p>

一份技能文档（`SKILL.md`）、三个自动化工具，以及一款**真正通过构建和试玩测试的示例游戏**。

OpenAI × ModRetro 的 [Chromatic](https://openai.com/zh-Hans-CN/supply/co-lab/chromatic/)（兼容 Game Boy 硬件的掌机）演示的流程是：AI 写 C → GBDK 编译 ROM → 用眼睛检查模拟器的画面。这个工具包让你不用买 $200 的设备，在已有的机器上照样跑通。

`R36S · Miyoo Mini · Anbernic · iPhone（Delta） · PC/网页模拟器 · 真机` — 一个 `.gbc` 文件，全都能跑。

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

打开 `build/strip.png`，那就是游戏。

GBDK-2020 从[发布页](https://github.com/gbdk-2020/gbdk-2020/releases)下载，解压到任意位置，然后
`export GBDKDIR=/路径/gbdk/`（**末尾的 `/` 一定要有**）。`build.sh` 也会自己找 `/opt/gbdk`、`~/gbdk` 等地，没有 `make` 也能构建。

## 示例游戏 — TILE HOP

不是空壳：一款从标题 → 游玩 → 计分 → 通关完整跑通的游戏就放在这里。复制过去改就行。

| | |
| --- | --- |
| 操作 | 方向键移动，`START` 开始，`SELECT` 回标题 |
| 目标 | 吃完 6 颗星出现 `CLEAR!`，星星重新布置、分数清零（无限循环） |
| 实现内容 | 5 种彩色调色板、BG/OBJ 调色板分离、图块碰撞、精灵动画、音效、HUD |
| 大小 | ROM 32 KiB · 图块 182 / VRAM 384 |

| 标题 | 游玩 | 通关 |
| --- | --- | --- |
| ![title](images/title-screen.png) | ![strip](images/playtest-strip.png) | ![clear](images/clear-screen.png) |

右边那组画面是 `tools/playtest.py` 实际运行 ROM 时抓的帧——
标题 → 开始 → 向右走吃到星星（SCORE 00→01，STAR 6→5）→ 移动 → 回到标题。
**这个工具包的标准是"在屏幕上看到了"，而不是"编译通过了"。**

## 在哪里都能运行

`.gbc` 是标准的 Game Boy Color ROM，同一个文件在下面哪里都能直接跑。

| 设备 | 方法 |
| --- | --- |
| **R36S（ArkOS）** | 复制到 microSD 的 `EASYROMS` 分区里的 GBC 文件夹 → Gambatte 或 SameBoy 核心（详见下文） |
| **Miyoo Mini（Onion）、Anbernic RG35XX 等** | 道理一样——放进掌机的 GBC ROM 文件夹即可 |
| **iPhone / iPad** | 用 Delta 应用打开 `.gbc` |
| **PC / Mac** | SameBoy、mGBA |
| **真机** | Game Boy Color + 烧录卡 |

### 装进 R36S

1. 把 microSD 插到电脑，打开 **EASYROMS** 分区（不是 `BOOT` 分区）。
2. 把 `.gbc` 复制到 GBC 文件夹——通常是 `EASYROMS/roms/gbc/`（取决于镜像，也可能是 `EASYROMS/gbc/`）。
   文件夹名区分大小写。游戏不显示时，错的是文件夹，不是 ROM。
3. 运行。核心用 **Gambatte**（默认，够用）或 **SameBoy**（最准确）。
4. 画面设置：GBC 是 160×144，正好 **10:9**，而 R36S 屏幕是 640×480（4:3）。
   在 `设置 → 视频 → 缩放` 里选 **Aspect Ratio: Core Provided + Integer Scale: ON → 480×432（3 倍）**。
   像素会落在整齐的正方形网格上。4 倍（640×576）在 480 行里放不下，最后还是退回 3 倍。
   "铺满屏幕"会把 10:9 硬塞进 4:3，横向拉长约 20%——像素画不建议。

## 仓库里有什么

```
SKILL.md                  给 AI 助手的正文 — 硬件限制、GBDK API、制作与验证循环
AGENTS.md / CLAUDE.md     Codex 和 Claude Code 在仓库根目录直接读取的摘要规则
tools/
  png2gbc.py              PNG → 8×8 2bpp 图块 + BGR555 调色板 C 代码（+ 图块网格预览）
  artfont.py              用 5×7 像素字体把标志和文字画进 PNG
  playtest.py             PyBoy 无头运行 + 按键序列 + 截图条
  check_env.sh            检查 GBDK / python / pillow / pyboy
templates/minimal-gbc/    真正能跑的示例游戏 "TILE HOP"（标题 → 游玩 → 计分 → 通关）
docs/images/              验证截图（包括上面的 GIF）
docs/ci.md                CI 工作流全文 + 一次性注册方法（尚未提交到仓库）
```

## 接到你的 AI 助手

| 工具 | 怎么被读到 |
| --- | --- |
| **Claude Code** | 在仓库里打开就会读 `CLAUDE.md`。让它"把 TILE HOP 复制一份改成射击游戏"，它会按 `SKILL.md` 的规则来做。 |
| **Codex / 其他助手** | 会读 `AGENTS.md`。如果你的工具两个都不读，在对话开头加一句让它读 `SKILL.md` 就行。 |
| **Claude Skill 格式** | `SKILL.md` 带 frontmatter（`name`、`description`），是标准技能文档，直接放进技能文件夹就能用。 |

技能强制的东西：384 个图块的 VRAM 预算、每块 4 色、8×8 对齐、OAM 40 个且每条扫描线 10 个、
`vsync()` 循环、CGB 寄存器保护，以及**构建之后一定要用眼睛看试玩截图条**。

## 制作流程（技能里写的循环）

1. **一段策划 + 一行通过标准** — "向右走 36 帧能吃到星星，分数从 0 变 1"
2. **PNG 美术** → 用 `tools/png2gbc.py` 转成图块和调色板，看预览确认
3. **C 代码** — 复制 `templates/minimal-gbc/src/main.c` 来改
4. **构建** — `./build.sh`（lcc）
5. **试玩测试** — 跑按键脚本 → 生成截图条 PNG
6. **自己打开截图条检查** → 改，再重复
7. **留下证据** — 截图条和截图放进 `docs/images/`，从 README 链接过去

## 三个工具

```bash
# 1) 美术：sprite 是 3 色 + 透明，bg 是 4 色。--dedup 合并重复图块，--palette 固定调色板
python3 tools/png2gbc.py assets/player.png --mode sprite --name player -o src/gen/player
python3 tools/png2gbc.py assets/level.png  --mode bg --map --dedup --name level -o src/gen/level

# 2) 文字：用 5×7 字体把标志和文字画进 PNG（整数倍放大）
python3 tools/artfont.py "PRESS START" --scale 2 --color "#FFEBC2" --out press.png

# 3) 试玩测试：wait / press / hold / release / snap
python3 tools/playtest.py --rom build/tile-hop.gbc \
  --script "wait:40,press:start:4,wait:20,snap:play,hold:right:40,release:right,snap:score" \
  --out build/strip.png
```

`playtest.py` 会提醒典型的失败："每一帧都一样（= 按键没进游戏）""颜色只有 2 种或更少（= 调色板/显示问题）"
"空白帧"。出现警告就当成 bug 去修。

## 硬件速查（详见 `SKILL.md`）

| 项目 | 值 |
| --- | --- |
| 屏幕 | 160×144（20×18 图块） |
| 图块 | 8×8，2bpp = 每块 4 色，16 字节 |
| VRAM | 384 块（8 KiB）——背景和精灵**共用同一片空间** |
| 调色板 | BG 8 个 + OBJ 8 个 × 4 色，BGR555 15 位 |
| 精灵 | OAM 40 个，**每条扫描线 10 个** |
| 帧 | 59.7 fps，约 70,224 个周期 |
| 声音 | 4 声道（2 方波·1 波形·1 噪声） |

## CI

[`docs/ci.md`](ci.md) 里有完整的工作流——Ubuntu 运行器下载 GBDK-2020 4.5.0，构建
`templates/minimal-gbc`，检查 ROM 头（大小、标题、卡带类型 `0x1B`、CGB 标志 `0x80`），
跑 PyBoy 试玩测试（`--strict`），再把 `.gbc` 和截图条作为产物上传。

> 这个仓库里 `.github/workflows/build-rom.yml` **还没有注册。**
> 第一次推送用的 GitHub 令牌没有 `workflows` 权限，GitHub 拒绝了这个文件。
> 把 `docs/ci.md` 里的文件在网页端粘贴一次，之后每次推送都会运行。

## 致谢

- 编译器：[GBDK-2020](https://github.com/gbdk-2020/gbdk-2020)（基于 SDCC）
- 模拟器：[PyBoy](https://github.com/Baekalfen/PyBoy) — 用于无头验证
- 参考：Pan Docs（Game Boy 硬件文档）、GBDK 2020 Docs
- 灵感：OpenAI × ModRetro **Chromatic: Codex Edition**

MIT License — 见 [LICENSE](../LICENSE)。游戏可以做、可以改、也可以卖。
问题和 bug 请到 [Issues](https://github.com/dong3789/retro-game-creator/issues)；用这个工具包做的游戏随时欢迎来晒。
