# Retro Game Creator

[English](../README.md) · [한국어](README.ko.md) · **日本語** · [简体中文](README.zh.md) · [Português](README.pt.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [हिन्दी](README.hi.md)

**AI コーディングエージェントにゲームを作らせると、本物のゲームボーイカラー ROM（`.gbc`）が出てきます。**

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/output-.gbc-8b6b2e.svg" alt="Output: .gbc ROM">
  <img src="https://img.shields.io/badge/compiler-GBDK--2020%204.5.0-2f9e44.svg" alt="Compiler: GBDK-2020 4.5.0">
  <img src="https://img.shields.io/badge/games_shipped-2-ff6b6b.svg" alt="Games shipped: 2">
  <img src="https://img.shields.io/badge/agents-Claude%20Code%20%2B%20Codex-6e56cf.svg" alt="Agents: Claude Code and Codex">
</p>

<p align="center">
  <img src="images/bungeoppang-plus-gameplay.gif" width="320" alt="Bungeoppang Tycoon Plus のプレイ画面 — 夜市場の屋台、焼き型4つ、客の注文と販売">
</p>
<p align="center">
  <em>Bungeoppang Tycoon Plus — このキットで作り、公開済みの ROM からそのままキャプチャ。
  <a href="https://github.com/dong3789/bungeoppang-tycoon-plus-gbc">リポジトリ</a> ·
  <a href="https://github.com/dong3789/bungeoppang-tycoon-plus-gbc/releases/tag/v1.0">遊ぶ</a></em>
</p>

スキル文書 1 本（`SKILL.md`）、自動化ツール 3 本、スターターテンプレート — そして**実際に世に出したゲーム 2 本**。どちらも今かばんの中にある携帯機でそのまま動きます。

OpenAI × ModRetro の [Chromatic](https://openai.com/en-US/supply/co-lab/chromatic/)（ゲームボーイ互換ハード）が示した「AI が C を書き → GBDK が ROM を焼き → エミュレータのフレームを目で検収する」流れを、$200 の端末を買わずに、すでに持っている機械で回せるようにしたものです。

`R36S · Miyoo Mini · Anbernic · iPhone（Delta） · PC/ウェブエミュレータ · 実機` — `.gbc` ファイル 1 つで全部動きます。

---

## ショーケース — このキットで作ったゲーム

ゲーム 2 本、どちらも `.gbc` として公開済みです。このリポジトリが強制するのと同じループから出てきました。`SKILL.md` を見て C を書き、GBDK-2020 でコンパイルし、`tools/playtest.py` で ROM をヘッドレス再生し、フレームを目で見て、直して、繰り返す。以下のアニメーションとストリップはすべて**公開済みの ROM**から撮ったもので、モックアップではありません。

### 1. Bungeoppang Tycoon Plus

> 夜市場のたい焼き屋台、制限時間 90 秒。

[リポジトリ](https://github.com/dong3789/bungeoppang-tycoon-plus-gbc) · [リリース v1.0 · `bungeoppang-plus.gbc`（32 KiB）](https://github.com/dong3789/bungeoppang-tycoon-plus-gbc/releases/tag/v1.0)

| | |
| --- | --- |
| ジャンル | 90 秒スコアアタックの調理ゲーム |
| ループ | 焼き型 4 つ、具は BEAN / CREAM / CHEESE / PIZZA の 4 種。生地を流し、きつね色になったら客が注文した具で売る |
| 操作 | 十字ボタン: 型を選ぶ · **A**: 流す / 売る / 焦げを削る · **B**: 具を変える（長押しで連続） · **SELECT**: 逆回り · **START**: 開始・やり直し |
| 深さ | 客は具と我慢ゲージを持って来店。正しく売るたびにコンボが伸び、90 秒終了時に売上で S/A/B/C 評価（S = 6000 ゴールド） |
| ハードウェア予算 | 背景タイル番号 256 個のうち 246、OAM スプライト 40 個のうち 28。具 4 種はタイルを共有し、パレットだけ差し替えます — 切り替えに VRAM は不要 |
| ROM | CGB 専用（`0xC0`）、32 KiB、MBC5+RAM+電池（`0x1B`） |

<p align="center"><img src="images/bungeoppang-plus-strip.png" width="848" alt="Bungeoppang Tycoon Plus の 5 コマ: タイトル、具を注文する客、最初の型に生地を流したところ、きつね色、100 ゴールドの会計"></p>

ストリップは公開 ROM から抜いた 5 コマです。タイトル画面、CREAM を注文する客、最初の型に生地を流したところ、きつね色、そして販売（`GOLD 100 · COMBO 1`）。

### 2. RAMEN TIME

> 3 ラウンド、5 ステップ、ボタンはひとつ — そしてあなたより速いカーソル。

[リポジトリ](https://github.com/dong3789/ramen-time-gbc) · [リリース v1.0 · `ramen-time.gbc`（32 KiB）](https://github.com/dong3789/ramen-time-gbc/releases/tag/v1.0)

| | |
| --- | --- |
| ジャンル | タイミング／リズムの調理ゲーム |
| ループ | **BOIL → NOODLES → SOUP → TOPPING → STOP** を 1 ラウンドに 5 回、3 ラウンド。動くカーソルが緑の範囲にあるときに押す |
| 操作 | **A**: タイミング（TOPPING では卵） · **B**: ねぎを入れる · **START**: 開始 / もう一度 · **SELECT**: タイトルへ |
| 深さ | 112 px ゲージの中央 16 px が PERFECT（100 点）、GOOD は 60 点、外すと 0 点。カーソルは 1 ラウンド 2 フレームで 1 px、2 ラウンド 1 フレームで 1 px、3 ラウンド 1 フレームで 2 px。早く止めると麺は HARD、遅いと SOGGY。満点は 1260 点 |
| ハードウェア予算 | VRAM 384 枠のうち背景 215 + スプライト 3、OAM 40 個のうち 3 個 — 段階ごとに鍋のタイル 1 行だけ差し替えます |
| ROM | CGB 対応（`0x80`）、32 KiB、MBC5+RAM+電池（`0x1B`） |

<p align="center"><img src="images/ramen-time-gameplay.gif" width="320" alt="RAMEN TIME のプレイ画面 — 鍋が沸騰し、カーソルがゲージを渡り、PERFECT 100 点、続いて麺が入る"></p>

<p align="center"><img src="images/ramen-time-strip.png" width="848" alt="RAMEN TIME の 5 コマ: タイトル、カーソルが動く BOIL、PERFECT +100、NOODLES、評価 S・1260 点の結果カード"></p>

右端の結果カードは、エミュレータのメモリからカーソルのスプライトを読みながら 15 段階を実際にプレイした結果です。評価 **S**、スコア **1260**、*PERFECT NOODLES*。

**2 本に共通していることが要点です。** 入力 → スコア → 評価まで通る完全なループ、パレットだけで変えるアートのバリエーション、そして人間が実際に読めるプレイテストストリップ。このキットが求める基準はそこです。

---

## 30 秒で開始

```bash
git clone https://github.com/dong3789/retro-game-creator.git
cd retro-game-creator

./tools/check_env.sh                 # GBDK・python・pillow・pyboy の確認
./templates/minimal-gbc/build.sh     # サンプル ROM をビルド → build/tile-hop.gbc

python3 tools/playtest.py --rom templates/minimal-gbc/build/tile-hop.gbc \
  --script "wait:8,press:start:4,wait:16,hold:right:36,snap:score" \
  --out build/strip.png
```

`build/strip.png` を開いてください。それがゲームです。

GBDK-2020 は[リリースページ](https://github.com/gbdk-2020/gbdk-2020/releases)から取得して好きな場所に展開し、
`export GBDKDIR=/path/to/gbdk/`（**末尾の `/` を忘れずに**）を設定します。`build.sh` は `/opt/gbdk`、`~/gbdk` なども探し、`make` がなくてもビルドできます。

## スターターテンプレート — TILE HOP

`templates/minimal-gbc/` はコピーして始める土台です。空の殻ではなく、タイトル → プレイ → スコア → クリアまで通るゲームなので、残すべき部品（vsync ループ、ジョイパッドのエッジ検出、タイルマップ、スプライト、サウンド、HUD）はすでに配線済みです。

| | |
| --- | --- |
| 操作 | 十字ボタンで移動、`START` で開始、`SELECT` でタイトルへ |
| 目的 | 星 6 個を全部食べると `CLEAR!`、星が再配置されスコアはリセット（無限） |
| 入っているもの | カラーパレット 5 種、BG/OBJ パレット分離、タイル衝突、スプライトアニメーション、サウンド、HUD |
| サイズ | ROM 32 KiB · タイル 182 / VRAM 384 |

| タイトル | プレイ | クリア |
| --- | --- | --- |
| ![title](images/title-screen.png) | ![strip](images/playtest-strip.png) | ![clear](images/clear-screen.png) |

中央のストリップは `tools/playtest.py` が実際に ROM を動かしながら撮ったフレームです —
タイトル → 開始 → 右へ歩いて星を取得（SCORE 00→01、STAR 6→5）→ 移動 → タイトルに戻る。
**基準は「ビルドが通った」ではなく「画面で確認した」。**

## どこでも動かす

`.gbc` は標準のゲームボーイカラー ROM なので、同じファイルが下のどこでもそのまま動きます — 上のショーケースの 2 本も同じです。

| 端末 | 方法 |
| --- | --- |
| **R36S（ArkOS）** | microSD の `EASYROMS` パーティションの GBC フォルダにコピー → Gambatte か SameBoy コア（下記） |
| **Miyoo Mini（Onion）、Anbernic RG35XX など** | 同じ要領 — SD カードの GBC ROM フォルダに入れるだけ |
| **iPhone / iPad** | Delta アプリで `.gbc` を開く |
| **PC / Mac** | SameBoy、mGBA |
| **実機** | ゲームボーイカラー + フラッシュカート |

### R36S に入れる

1. microSD を PC に挿し、**EASYROMS** パーティションを開きます（`BOOT` ではありません）。
2. GBC フォルダに `.gbc` をコピーします — ふつうは `EASYROMS/roms/gbc/`、イメージによっては `EASYROMS/gbc/`。
   フォルダ名は大文字小文字を区別します。ゲームが出てこないときは、ROM ではなくフォルダが違います。
3. 起動。コアは **Gambatte**（既定、無難）か **SameBoy**（最も正確）。
4. 画面設定: GBC は 160×144 = ちょうど **10:9**、R36S のパネルは 640×480（4:3）です。
   `設定 → ビデオ → スケーリング` で **Aspect Ratio: Core Provided** と **Integer Scale: ON → 480×432（3 倍）**。
   ピクセルがきれいな正方グリッドに乗ります。4 倍（640×576）は縦 480 に入らないので、結局 3 倍になります。
   「画面いっぱい」は 10:9 を 4:3 に引き伸ばして約 20% 横長になります — ピクセルアートには非推奨。

## 中身

```
SKILL.md                  AI エージェント向け本文 — ハードウェア制約、GBDK API、制作・検収ループ
AGENTS.md / CLAUDE.md     Codex と Claude Code がリポジトリ直下で読む要約ルール
tools/
  png2gbc.py              PNG → 8×8 2bpp タイル + BGR555 パレットの C コード（+ タイルグリッドのプレビュー）
  artfont.py              5×7 ピクセルフォントでロゴや文字を PNG に描く
  playtest.py             PyBoy のヘッドレス実行 + キー入力スクリプト + スクリーンショットストリップ
  check_env.sh            GBDK / python / pillow / pyboy の確認
templates/minimal-gbc/    スターターゲーム「TILE HOP」（タイトル → プレイ → スコア → クリア）
docs/images/              実際の ROM から撮った画面と GIF（ショーケース 2 本 + TILE HOP）
docs/ci.md                CI ワークフロー全文 + 1 回だけの登録方法（まだリポジトリ未登録）
```

ショーケースの 2 本はそれぞれ別のリポジトリにあります —
[`bungeoppang-tycoon-plus-gbc`](https://github.com/dong3789/bungeoppang-tycoon-plus-gbc) と
[`ramen-time-gbc`](https://github.com/dong3789/ramen-time-gbc) — ソース、ビルドスクリプト、`docs/` のスクリーンショットまで全部入っています。

## AI エージェントにつなぐ

| ツール | 読み込まれ方 |
| --- | --- |
| **Claude Code** | リポジトリを開くと `CLAUDE.md` を読みます。「TILE HOP をコピーしてシューティングに変えて」と頼めば、`SKILL.md` の規約どおりに進みます。 |
| **Codex / その他のエージェント** | `AGENTS.md` を読みます。どちらも読まないツールなら、会話の冒頭に `SKILL.md` を読むよう 1 行添えてください。 |
| **Claude Skill 形式** | `SKILL.md` は frontmatter（`name`、`description`）を持つ標準的なスキル文書なので、そのままスキルフォルダに入ります。 |

スキルが強制すること: 384 タイルの VRAM 予算、1 タイル 4 色、8×8 整列、OAM 40 個・走査線あたり 10 個、
`vsync()` ループ、CGB レジスタのガード、そして**ビルド後にかならずプレイテストストリップを目で見ること**。

## 制作ループ（スキルに書かれている手順）

1. **設計を 1 段落 + 合否ラインを 1 行** — 「右へ 36 フレーム歩くと星を食べ、スコアが 0→1 になる」
2. **PNG アート** → `tools/png2gbc.py` でタイルとパレットに変換し、プレビューを目で確認
3. **C コード** — `templates/minimal-gbc/src/main.c` をコピーして書き換える
4. **ビルド** — `./build.sh`（lcc）
5. **プレイテスト** — キー入力スクリプトを実行 → ストリップ PNG を得る
6. **ストリップを自分で開く** → 直して繰り返す
7. **証拠を残す** — ストリップやスクリーンショットを `docs/images/` に置き、README からリンクする

ショーケースの 2 本も、ストリップが「見せる価値のある絵」になるまでこのループを回しました。スクリーンショットより自動化が効く場面では、推測ではなくゲームの状態を実行中に直接読みます。上の RAMEN TIME の GIF はスプライト属性テーブルからタイミングカーソルを読んで PERFECT の範囲で `A` を押しており、Bungeoppang の GIF は画面から客の注文をサンプリングしてその具を `B` で選んでいます。

## ツール 3 本

```bash
# 1) アート: スプライトは 3 色 + 透明、背景は 4 色。--dedup でタイル重複を統合、--palette でパレット固定
python3 tools/png2gbc.py assets/player.png --mode sprite --name player -o src/gen/player
python3 tools/png2gbc.py assets/level.png  --mode bg --map --dedup --name level -o src/gen/level

# 2) 文字: ロゴや文言を 5×7 フォントで PNG に描く（整数倍）
python3 tools/artfont.py "PRESS START" --scale 2 --color "#FFEBC2" --out press.png

# 3) プレイテスト: wait / press / hold / release / snap
python3 tools/playtest.py --rom build/tile-hop.gbc \
  --script "wait:40,press:start:4,wait:20,snap:play,hold:right:40,release:right,snap:score" \
  --out build/strip.png
```

`playtest.py` は定番の失敗も指摘します。「全フレームが同じ（＝入力が届いていない）」「色が 2 色以下（＝パレット／表示の問題）」
「空のフレーム」。警告が出たらバグとして直してください。

## ハードウェア早見表（詳細は `SKILL.md`）

| 項目 | 値 |
| --- | --- |
| 画面 | 160×144（20×18 タイル） |
| タイル | 8×8、2bpp = 1 タイル 4 色、16 バイト |
| VRAM | 384 タイル（8 KiB）— 背景とスプライトが**同じ場所**を共有 |
| パレット | BG 8 + OBJ 8 × 4 色、BGR555 15 ビット |
| スプライト | OAM 40 個、**走査線あたり 10 個** |
| フレーム | 59.7 fps、約 70,224 サイクル |
| サウンド | 4 チャンネル（矩形波 2・波形・ノイズ） |

## CI

[`docs/ci.md`](ci.md) にワークフロー全文があります — Ubuntu ランナーが GBDK-2020 4.5.0 を取得して
`templates/minimal-gbc` をビルドし、ROM ヘッダー（サイズ・タイトル・カート種別 `0x1B`・CGB フラグ `0x80`）を検査し、
PyBoy のプレイテスト（`--strict`）を回して `.gbc` とスクリーンショットストリップをアーティファクトに上げます。

> このリポジトリにはまだ `.github/workflows/build-rom.yml` が**登録されていません。**
> 最初のプッシュに使った GitHub トークンに `workflows` 権限がなく、GitHub がそのファイルを拒否したためです。
> `docs/ci.md` のファイルをウェブ UI で一度貼り付ければ、それ以降は毎プッシュで動きます。

## クレジット

- コンパイラ: [GBDK-2020](https://github.com/gbdk-2020/gbdk-2020)（SDCC ベース）
- エミュレータ: [PyBoy](https://github.com/Baekalfen/PyBoy) — ヘッドレス検収用
- 参考: Pan Docs（ゲームボーイのハードウェア文書）、GBDK 2020 Docs
- 着想: OpenAI × ModRetro **Chromatic: Codex Edition**

MIT License — [LICENSE](../LICENSE) を参照。ゲームを作って、改造して、売ってもかまいません。
質問やバグは [Issues](https://github.com/dong3789/retro-game-creator/issues) へ。このキットで作ったゲームの自慢はいつでも歓迎です。
