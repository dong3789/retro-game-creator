# Retro Game Creator

[English](../README.md) · [한국어](README.ko.md) · **日本語** · [简体中文](README.zh.md) · [Português](README.pt.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [हिन्दी](README.hi.md)

**AI コーディングエージェントに「ゲームを作って」と頼むと、本物のゲームボーイカラー ROM（`.gbc`）が出てきます。**

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/output-.gbc-8b6b2e.svg" alt="Output: .gbc ROM">
  <img src="https://img.shields.io/badge/compiler-GBDK--2020%204.5.0-2f9e44.svg" alt="Compiler: GBDK-2020 4.5.0">
  <img src="https://img.shields.io/badge/agents-Claude%20Code%20%2B%20Codex-6e56cf.svg" alt="Agents: Claude Code and Codex">
</p>

<p align="center">
  <img src="images/gameplay.gif" width="480" alt="エミュレーターで動くサンプルゲーム TILE HOP">
</p>

スキル文書 1 枚（`SKILL.md`）、自動化ツール 3 つ、そして**実際にビルドとプレイテストを通過したサンプルゲーム**が入ったオープンスキルキットです。

OpenAI × ModRetro の [Chromatic](https://openai.com/ja-JP/supply/co-lab/chromatic/)（ゲームボーイ互換ハードウェア）が示した「AI が C を書き → GBDK で ROM を焼き → エミュレーターのフレームを目で検証する」流れを、$200 の端末を買わずに、すでに手元にある機械でそのまま使えるようにしました。

`R36S · Miyoo Mini · Anbernic · iPhone（Delta） · PC/Web エミュレーター · 実機` — `.gbc` ファイル 1 つでどれでも動きます。

---

## 30秒で試す

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

GBDK-2020 は[リリースページ](https://github.com/gbdk-2020/gbdk-2020/releases)から取得して任意の場所に展開し、
`export GBDKDIR=/path/to/gbdk/`（**末尾の `/` を忘れずに**）と設定してください。`build.sh` は `/opt/gbdk`、`~/gbdk` なども自動で探し、`make` がなくてもビルドできます。

## サンプルゲーム — TILE HOP

空の雛形ではなく、タイトル → プレイ → スコア → クリアまで通しで動くゲームが 1 本入っています。コピーして書き換えるところから始められます。

| | |
| --- | --- |
| 操作 | 十字キーで移動、`START` で開始、`SELECT` でタイトルへ |
| 目標 | 星を 6 個すべて取ると `CLEAR!`、星が配置し直されてスコアもリセット（エンドレス） |
| 実装済み | カラーパレット 5 種、BG/OBJ パレット分離、タイル衝突、スプライトアニメーション、サウンド、HUD |
| サイズ | ROM 32 KiB · タイル 182 / VRAM 384 |

| タイトル | プレイ | クリア |
| --- | --- | --- |
| ![title](images/title-screen.png) | ![strip](images/playtest-strip.png) | ![clear](images/clear-screen.png) |

右のストリップは `tools/playtest.py` が実際に ROM を動かしながら撮ったフレームです —
タイトル → スタート → 右へ歩いて星を取得（SCORE 00→01、STAR 6→5） → 移動 → タイトルへ戻る。
**「ビルドできた」ではなく「画面で確認した」** がこのキットの基準です。

## どこでも動かす

`.gbc` は標準のゲームボーイカラー ROM なので、同じファイルが下のどこでもそのまま動きます。

| 端末 | 方法 |
| --- | --- |
| **R36S（ArkOS）** | microSD の `EASYROMS` パーティションにある GBC フォルダへコピー → Gambatte または SameBoy コア（下記） |
| **Miyoo Mini（Onion）、Anbernic RG35XX など** | 同じ要領 — 本体の GBC ROM フォルダに入れるだけ |
| **iPhone / iPad** | Delta アプリで `.gbc` を開く |
| **PC / Mac** | SameBoy、mGBA |
| **実機** | ゲームボーイカラー + フラッシュカート |

### R36S に入れる

1. microSD を PC に挿し、**EASYROMS** パーティションを開きます（`BOOT` ではありません）。
2. GBC フォルダに `.gbc` をコピーします — 通常は `EASYROMS/roms/gbc/`（イメージによっては `EASYROMS/gbc/`）。
   フォルダ名は大文字・小文字を区別します。ゲームが表示されないときは、ROM ではなくフォルダが違います。
3. 起動します。コアは **Gambatte**（既定・無難）または **SameBoy**（最も正確）。
4. 画面設定: GBC は 160×144 = ちょうど **10:9**、R36S のパネルは 640×480（4:3）です。
   `設定 → ビデオ → スケーリング` で **Aspect Ratio: Core Provided + Integer Scale: ON → 480×432（3 倍）**。
   ピクセルが正方形にきれいに並びます。4 倍（640×576）は縦 480 に入らないので、結局 3 倍になります。
   「画面いっぱいに広げる」は 10:9 を 4:3 に押し込んで約 20% 横に伸びるので、ピクセルアートにはおすすめしません。

## リポジトリの中身

```
SKILL.md                  エージェント向けの本文 — ハードウェア制約、GBDK API、制作・検証ループ
AGENTS.md / CLAUDE.md     Codex・Claude Code がリポジトリ直下で読む要約ルール
tools/
  png2gbc.py              PNG → 8×8 2bpp タイル + BGR555 パレットの C コード（+ タイルグリッドのプレビュー）
  artfont.py              5×7 ピクセルフォントでロゴや文字を PNG に描く
  playtest.py             PyBoy のヘッドレス実行 + キー入力シーケンス + スクリーンショットのストリップ
  check_env.sh            GBDK / python / pillow / pyboy の確認
templates/minimal-gbc/    実際に動くサンプルゲーム "TILE HOP"（タイトル → プレイ → スコア → クリア）
docs/images/              検証用スクリーンショット（上の GIF を含む）
docs/ci.md                CI ワークフロー全文 + 1 回だけの登録方法（まだリポジトリに未登録）
```

## エージェントにつなぐ

| ツール | 読み込まれ方 |
| --- | --- |
| **Claude Code** | リポジトリを開くと `CLAUDE.md` を読みます。「TILE HOP をコピーしてシューティングに変えて」のように頼むと、`SKILL.md` のルールに従って進めます。 |
| **Codex / その他のエージェント** | `AGENTS.md` を読みます。どちらも読まないツールなら、会話の最初に `SKILL.md` を読むよう 1 行添えてください。 |
| **Claude Skill 形式** | `SKILL.md` は frontmatter（`name`、`description`）付きの標準スキル文書なので、そのままスキルフォルダに入れて使えます。 |

スキルが強制するもの: 384 タイルの VRAM 予算、1 タイル 4 色、8×8 整列、OAM 40 個・1 スキャンライン 10 個、
`vsync()` ループ、CGB レジスタのガード、そして**ビルド後は必ずプレイテストのストリップを目で見ること**。

## 作る順番（スキルに書かれたループ）

1. **企画 1 段落 + 合否ライン 1 行** — 「右へ 36 フレーム歩くと星を取ってスコアが 0→1 になる」
2. **PNG アート** → `tools/png2gbc.py` でタイル・パレットに変換し、プレビューを目で確認
3. **C コード** — `templates/minimal-gbc/src/main.c` をコピーして書き換える
4. **ビルド** — `./build.sh`（lcc）
5. **プレイテスト** — キー入力スクリプトを実行 → ストリップ PNG を生成
6. **ストリップを自分で開いて検証** → 直して繰り返す
7. **証拠を残す** — ストリップやスクリーンショットを `docs/images/` に置き、README からリンク

## ツール 3 つ

```bash
# 1) アート: sprite は 3 色 + 透明、bg は 4 色。--dedup で重複タイルを統合、--palette でパレットを固定
python3 tools/png2gbc.py assets/player.png --mode sprite --name player -o src/gen/player
python3 tools/png2gbc.py assets/level.png  --mode bg --map --dedup --name level -o src/gen/level

# 2) 文字: ロゴやフレーズを 5×7 フォントで PNG に描く（整数倍）
python3 tools/artfont.py "PRESS START" --scale 2 --color "#FFEBC2" --out press.png

# 3) プレイテスト: wait / press / hold / release / snap
python3 tools/playtest.py --rom build/tile-hop.gbc \
  --script "wait:40,press:start:4,wait:20,snap:play,hold:right:40,release:right,snap:score" \
  --out build/strip.png
```

`playtest.py` は「全フレームが同じ（= 入力が届いていない）」「色が 2 色以下（= パレット/表示の問題）」
「空のフレーム」といった典型的な失敗を警告で指摘します。警告が出たらバグとして直してください。

## ハードウェア早見表（詳しくは `SKILL.md`）

| 項目 | 値 |
| --- | --- |
| 画面 | 160×144（20×18 タイル） |
| タイル | 8×8、2bpp = 1 タイル 4 色、16 バイト |
| VRAM | 384 タイル（8 KiB）— BG とスプライトが**同じ場所**を使う |
| パレット | BG 8 + OBJ 8 × 4 色、BGR555 15bit |
| スプライト | OAM 40 個、**1 スキャンライン 10 個** |
| フレーム | 59.7 fps、約 70,224 サイクル |
| サウンド | 4 チャンネル（矩形波 2・波形・ノイズ） |

## CI

[`docs/ci.md`](ci.md) にワークフロー全文があります — Ubuntu ランナーで GBDK-2020 4.5.0 を取得して
`templates/minimal-gbc` をビルドし、ROM ヘッダー（サイズ・タイトル・カートタイプ `0x1B`・CGB フラグ `0x80`）を検査し、
PyBoy のプレイテスト（`--strict`）まで実行して、`.gbc` とスクリーンショットのストリップをアーティファクトとしてアップロードします。

> このリポジトリにはまだ `.github/workflows/build-rom.yml` が**登録されていません。**
> 最初のプッシュに使った GitHub トークンに `workflows` 権限がなく、GitHub がそのファイルを拒否したためです。
> `docs/ci.md` のファイルを Web UI で一度貼り付ければ、以降は毎プッシュで実行されます。

## クレジット

- コンパイラー: [GBDK-2020](https://github.com/gbdk-2020/gbdk-2020)（SDCC ベース）
- エミュレーター: [PyBoy](https://github.com/Baekalfen/PyBoy) — ヘッドレス検証用
- リファレンス: Pan Docs（ゲームボーイのハードウェア文書）、GBDK 2020 Docs
- インスピレーション: OpenAI × ModRetro **Chromatic: Codex Edition**

MIT License — [LICENSE](../LICENSE) を参照。ゲームを作って、直して、売ってもかまいません。
質問やバグは [Issues](https://github.com/dong3789/retro-game-creator/issues) へ。このキットで作ったゲームの自慢もいつでも歓迎です。
