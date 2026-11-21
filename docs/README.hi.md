# Retro Game Creator

[English](../README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh.md) · [Português](README.pt.md) · [Français](README.fr.md) · [العربية](README.ar.md) · **हिन्दी**

**किसी AI कोडिंग एजेंट से गेम बनाने को कहिए और आपको असली Game Boy Color ROM (`.gbc`) मिलती है।**

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/output-.gbc-8b6b2e.svg" alt="Output: .gbc ROM">
  <img src="https://img.shields.io/badge/compiler-GBDK--2020%204.5.0-2f9e44.svg" alt="Compiler: GBDK-2020 4.5.0">
  <img src="https://img.shields.io/badge/agents-Claude%20Code%20%2B%20Codex-6e56cf.svg" alt="Agents: Claude Code and Codex">
</p>

<p align="center">
  <img src="images/gameplay.gif" width="480" alt="नमूना गेम TILE HOP एमुलेटर में चलते हुए">
</p>

एक स्किल दस्तावेज़ (`SKILL.md`), तीन ऑटोमेशन टूल, और एक नमूना गेम जिसे सचमुच बिल्ड और प्लेटेस्ट किया गया है।

यह किट OpenAI × ModRetro के [Chromatic](https://openai.com/supply/co-lab/chromatic/) (Game Boy हार्डवेयर के साथ चलने वाला हैंडहेल्ड) में दिखाया गया तरीका अपनाती है — AI C लिखता है, GBDK ROM बनाता है, और एमुलेटर के फ्रेम आँखों से जाँचे जाते हैं — और इसे $200 का डिवाइस खरीदे बिना, आपके पास पहले से मौजूद डिवाइस पर चलाती है।

`R36S · Miyoo Mini · Anbernic · iPhone (Delta) · PC और वेब एमुलेटर · असली हार्डवेयर` — एक ही `.gbc` फ़ाइल सब पर चलती है।

---

## 30 सेकंड में शुरू करें

```bash
git clone https://github.com/dong3789/retro-game-creator.git
cd retro-game-creator

./tools/check_env.sh                 # GBDK, python, pillow, pyboy
./templates/minimal-gbc/build.sh     # नमूना ROM बनाएँ → build/tile-hop.gbc

python3 tools/playtest.py --rom templates/minimal-gbc/build/tile-hop.gbc \
  --script "wait:8,press:start:4,wait:16,hold:right:36,snap:score" \
  --out build/strip.png
```

`build/strip.png` खोलिए। वही गेम है।

GBDK-2020 को [रिलीज़ पेज](https://github.com/gbdk-2020/gbdk-2020/releases) से लेकर कहीं भी अनज़िप करें और
`export GBDKDIR=/path/to/gbdk/` (**अंत में `/` ज़रूर रखें**) सेट करें। `build.sh` खुद `/opt/gbdk`, `~/gbdk` और कुछ और जगहें भी देखता है, और `make` के बिना भी बिल्ड कर देता है।

## नमूना गेम — TILE HOP

खोखला ढाँचा नहीं: टाइटल से लेकर खेल, स्कोर और क्लियर तक पूरा चलने वाला एक गेम। कॉपी कीजिए और बदलना शुरू कीजिए।

| | |
| --- | --- |
| नियंत्रण | D-pad से चलें, `START` से शुरू, `SELECT` से टाइटल पर वापस |
| लक्ष्य | सभी 6 तारे खाएँ तो `CLEAR!`, फिर तारे दोबारा बिछते हैं और स्कोर शून्य हो जाता है (अंतहीन) |
| क्या बना है | 5 कलर पैलेट, अलग BG/OBJ पैलेट, टाइल टकराव, स्प्राइट एनिमेशन, ध्वनि, HUD |
| आकार | ROM 32 KiB · 384 में से 182 टाइल |

| टाइटल | खेल | क्लियर |
| --- | --- | --- |
| ![title](images/title-screen.png) | ![strip](images/playtest-strip.png) | ![clear](images/clear-screen.png) |

दाईं ओर की पट्टी `tools/playtest.py` द्वारा ROM को सचमुच चलाते हुए लिए गए फ्रेम हैं —
टाइटल → स्टार्ट → दाएँ चलकर तारा लेना (SCORE 00→01, STAR 6→5) → चलना → टाइटल पर वापस।
**मापदंड है "स्क्रीन पर दिखा", "बिल्ड हो गया" नहीं।**

## कहीं भी चलाएँ

`.gbc` एक मानक Game Boy Color ROM है, इसलिए वही फ़ाइल नीचे हर जगह चलती है।

| डिवाइस | तरीका |
| --- | --- |
| **R36S (ArkOS)** | microSD के `EASYROMS` पार्टिशन के GBC फ़ोल्डर में कॉपी करें → Gambatte या SameBoy कोर (नीचे विस्तार) |
| **Miyoo Mini (Onion), Anbernic RG35XX आदि** | वही तरीका — हैंडहेल्ड के GBC ROM फ़ोल्डर में डाल दें |
| **iPhone / iPad** | Delta ऐप में `.gbc` खोलें |
| **PC / Mac** | SameBoy, mGBA |
| **असली हार्डवेयर** | Game Boy Color + फ़्लैश कार्ट |

### R36S पर डालना

1. microSD को PC में लगाकर **EASYROMS** पार्टिशन खोलें (`BOOT` नहीं)।
2. `.gbc` को GBC फ़ोल्डर में कॉपी करें — आमतौर पर `EASYROMS/roms/gbc/`, इमेज के अनुसार कभी `EASYROMS/gbc/`।
   फ़ोल्डर के नाम में छोटे-बड़े अक्षर अलग मायने रखते हैं। गेम न दिखे तो गड़बड़ ROM में नहीं, फ़ोल्डर में है।
3. चलाएँ। कोर **Gambatte** (डिफ़ॉल्ट, ठीक है) या **SameBoy** (सबसे सटीक)।
4. स्क्रीन सेटिंग: GBC 160×144 है, यानी ठीक **10:9**, जबकि R36S का पैनल 640×480 (4:3) है।
   `सेटिंग → वीडियो → स्केलिंग` में **Aspect Ratio: Core Provided** और **Integer Scale: ON → 480×432 (3×)** चुनें।
   पिक्सेल साफ़ वर्गाकार ग्रिड पर बैठ जाते हैं। 4× (640×576) 480 पंक्तियों में नहीं समाता, इसलिए आख़िर में 3× ही रहता है।
   "स्क्रीन भर दें" 10:9 को 4:3 में खींचकर लगभग 20% चौड़ा कर देता है — पिक्सेल आर्ट के लिए सलाह नहीं।

## रेपो में क्या है

```
SKILL.md                  एजेंट के लिए मुख्य गाइड — हार्डवेयर सीमाएँ, GBDK API, बिल्ड/प्लेटेस्ट लूप
AGENTS.md / CLAUDE.md     संक्षिप्त नियम जो Codex और Claude Code रेपो रूट से पढ़ते हैं
tools/
  png2gbc.py              PNG → 8×8 2bpp टाइल + BGR555 पैलेट का C कोड (+ टाइल ग्रिड प्रीव्यू)
  artfont.py              5×7 पिक्सेल फ़ॉन्ट से लोगो और टेक्स्ट PNG में बनाएँ
  playtest.py             PyBoy हेडलेस रन + की-इनपुट सीक्वेंस + स्क्रीनशॉट स्ट्रिप
  check_env.sh            GBDK / python / pillow / pyboy की जाँच
templates/minimal-gbc/    चलने वाला नमूना गेम "TILE HOP" (टाइटल → खेल → स्कोर → क्लियर)
docs/images/              जाँच के स्क्रीनशॉट (ऊपर का GIF भी)
docs/ci.md                पूरा CI वर्कफ़्लो + एक बार रजिस्टर करने का तरीका (अभी रेपो में दर्ज नहीं)
```

## अपने एजेंट से जोड़ें

| टूल | कैसे पढ़ा जाता है |
| --- | --- |
| **Claude Code** | रेपो खोलते ही `CLAUDE.md` पढ़ता है। "TILE HOP की कॉपी बनाकर शूटिंग गेम में बदल दो" कहिए तो `SKILL.md` के नियमों से चलता है। |
| **Codex / दूसरे एजेंट** | वे `AGENTS.md` पढ़ते हैं। आपका टूल दोनों में से कोई न पढ़े तो बातचीत की शुरुआत में एक पंक्ति जोड़िए कि `SKILL.md` पढ़े। |
| **Claude Skill फ़ॉर्मैट** | `SKILL.md` में frontmatter (`name`, `description`) है, यह मानक स्किल दस्तावेज़ है, सीधे स्किल फ़ोल्डर में रख सकते हैं। |

स्किल जो थोपती है: 384 टाइल का VRAM बजट, हर टाइल 4 रंग, 8×8 संरेखण, 40 OAM प्रविष्टियाँ और हर स्कैनलाइन पर 10,
`vsync()` लूप, CGB रजिस्टर गार्ड, और **बिल्ड के बाद प्लेटेस्ट स्ट्रिप को आँखों से देखना ज़रूरी**।

## बनाने का क्रम (स्किल में लिखा लूप)

1. **एक पैराग्राफ़ डिज़ाइन + एक पंक्ति पास/फ़ेल मापदंड** — "दाएँ 36 फ्रेम चलें, तारा खाएँ, स्कोर 0→1 हो जाए"
2. **PNG आर्ट** → `tools/png2gbc.py` से टाइल और पैलेट बदलें, प्रीव्यू आँखों से देखें
3. **C कोड** — `templates/minimal-gbc/src/main.c` कॉपी करके बदलें
4. **बिल्ड** — `./build.sh` (lcc)
5. **प्लेटेस्ट** — की-इनपुट स्क्रिप्ट चलाएँ → स्ट्रिप PNG बनेगी
6. **स्ट्रिप खुद खोलकर जाँचें** → सुधारें और दोहराएँ
7. **सबूत रखें** — स्ट्रिप और स्क्रीनशॉट `docs/images/` में, README से लिंक

## तीन टूल

```bash
# 1) आर्ट: sprite में 3 रंग + पारदर्शिता, bg में 4 रंग। --dedup एक जैसी टाइलें मिलाता है, --palette पैलेट तय करता है
python3 tools/png2gbc.py assets/player.png --mode sprite --name player -o src/gen/player
python3 tools/png2gbc.py assets/level.png  --mode bg --map --dedup --name level -o src/gen/level

# 2) टेक्स्ट: लोगो और वाक्य 5×7 फ़ॉन्ट से PNG में बनाएँ (पूर्णांक स्केल)
python3 tools/artfont.py "PRESS START" --scale 2 --color "#FFEBC2" --out press.png

# 3) प्लेटेस्ट: wait / press / hold / release / snap
python3 tools/playtest.py --rom build/tile-hop.gbc \
  --script "wait:40,press:start:4,wait:20,snap:play,hold:right:40,release:right,snap:score" \
  --out build/strip.png
```

`playtest.py` आम गड़बड़ियों की चेतावनी भी देता है: "हर फ्रेम एक जैसा (= इनपुट गेम तक नहीं पहुँच रहा)",
"दो या कम रंग (= पैलेट/डिस्प्ले की समस्या)", "खाली फ्रेम"। चेतावनी आए तो उसे बग मानकर ठीक करें।

## हार्डवेयर एक नज़र में (विस्तार `SKILL.md` में)

| मद | मान |
| --- | --- |
| स्क्रीन | 160×144 (20×18 टाइल) |
| टाइल | 8×8, 2bpp = हर टाइल 4 रंग, 16 बाइट |
| VRAM | 384 टाइल (8 KiB) — बैकग्राउंड और स्प्राइट **एक ही जगह** साझा करते हैं |
| पैलेट | BG 8 + OBJ 8 × 4 रंग, BGR555 15-बिट |
| स्प्राइट | OAM 40, **हर स्कैनलाइन पर 10** |
| फ्रेम | 59.7 fps, लगभग 70,224 साइकिल |
| ध्वनि | 4 चैनल (2 स्क्वेयर, 1 वेव, 1 नॉइज़) |

## CI

[`docs/ci.md`](ci.md) में पूरा वर्कफ़्लो है — Ubuntu रनर GBDK-2020 4.5.0 लाता है,
`templates/minimal-gbc` बिल्ड करता है, ROM हेडर (साइज़, टाइटल, कार्ट टाइप `0x1B`, CGB फ़्लैग `0x80`) जाँचता है,
PyBoy प्लेटेस्ट `--strict` से चलाता है, और `.gbc` तथा स्क्रीनशॉट स्ट्रिप को आर्टिफ़ैक्ट के रूप में अपलोड करता है।

> इस रेपो में `.github/workflows/build-rom.yml` अभी **दर्ज नहीं है।** पहले पुश में इस्तेमाल GitHub टोकन के पास
> `workflows` अनुमति नहीं थी, इसलिए GitHub ने वह फ़ाइल ठुकरा दी। `docs/ci.md` की फ़ाइल को वेब UI में एक बार
> पेस्ट कर दें, फिर हर पुश पर वह चलेगा।

## श्रेय

- कंपाइलर: [GBDK-2020](https://github.com/gbdk-2020/gbdk-2020) (SDCC पर आधारित)
- एमुलेटर: [PyBoy](https://github.com/Baekalfen/PyBoy) — हेडलेस जाँच के लिए
- संदर्भ: Pan Docs (Game Boy हार्डवेयर), GBDK 2020 Docs
- प्रेरणा: OpenAI × ModRetro **Chromatic: Codex Edition**

MIT लाइसेंस — [LICENSE](../LICENSE) देखें। गेम बनाइए, बदलिए, बेचिए।
सवाल और बग [Issues](https://github.com/dong3789/retro-game-creator/issues) पर; इस किट से बने गेम हमेशा स्वागत योग्य हैं।
