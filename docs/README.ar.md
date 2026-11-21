# Retro Game Creator

[English](../README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh.md) · [Português](README.pt.md) · [Français](README.fr.md) · **العربية** · [हिन्दी](README.hi.md)

**اطلب من وكيل برمجة ذكي أن يصنع لعبة، فتحصل على روم حقيقي لجهاز Game Boy Color (`.gbc`).**

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/output-.gbc-8b6b2e.svg" alt="Output: .gbc ROM">
  <img src="https://img.shields.io/badge/compiler-GBDK--2020%204.5.0-2f9e44.svg" alt="Compiler: GBDK-2020 4.5.0">
  <img src="https://img.shields.io/badge/agents-Claude%20Code%20%2B%20Codex-6e56cf.svg" alt="Agents: Claude Code and Codex">
</p>

<p align="center">
  <img src="images/gameplay.gif" width="480" alt="اللعبة النموذجية TILE HOP وهي تعمل في محاكٍ">
</p>

وثيقة مهارة واحدة (`SKILL.md`)، وثلاث أدوات أتمتة، ولعبة نموذجية **تم بناؤها واختبارها فعليًا**.

يأخذ هذا المشروع الأسلوب الذي عرضته [Chromatic](https://openai.com/supply/co-lab/chromatic/) من OpenAI × ModRetro (جهاز محمول متوافق مع عتاد Game Boy) — يكتب الذكاء الاصطناعي بلغة C، ويبني GBDK الروم، ثم تُفحص إطارات المحاكي بالعين — ويجعله يعمل على جهاز تملكه بالفعل بدلًا من شراء جهاز بـ 200 دولار.

`R36S · Miyoo Mini · Anbernic · iPhone (Delta) · محاكيات الكمبيوتر والويب · العتاد الأصلي` — ملف `.gbc` واحد يعمل على الجميع.

---

## البدء في 30 ثانية

```bash
git clone https://github.com/dong3789/retro-game-creator.git
cd retro-game-creator

./tools/check_env.sh                 # GBDK وpython وpillow وpyboy
./templates/minimal-gbc/build.sh     # بناء روم المثال → build/tile-hop.gbc

python3 tools/playtest.py --rom templates/minimal-gbc/build/tile-hop.gbc \
  --script "wait:8,press:start:4,wait:16,hold:right:36,snap:score" \
  --out build/strip.png
```

افتح `build/strip.png`. تلك هي اللعبة.

نزّل GBDK-2020 من [صفحة الإصدارات](https://github.com/gbdk-2020/gbdk-2020/releases)، وفكّ ضغطه في أي مكان، ثم
`export GBDKDIR=/path/to/gbdk/` (**أبقِ الشرطة المائلة `/` في النهاية**). يبحث `build.sh` أيضًا في `/opt/gbdk` و`~/gbdk` وأماكن أخرى، ويبني دون الحاجة إلى `make`.

## اللعبة النموذجية — TILE HOP

ليست هيكلًا فارغًا: لعبة تمشي من شاشة العنوان إلى اللعب والنقاط وإنهاء الجولة. انسخها وابدأ التعديل.

| | |
| --- | --- |
| التحكم | الأسهم للحركة، `START` للبدء، `SELECT` للعودة إلى شاشة العنوان |
| الهدف | التهام النجوم الستة كلها لإظهار `CLEAR!`، ثم تُوزَّع النجوم من جديد وتُصفَّر النقاط (بلا نهاية) |
| ما تم تنفيذه | 5 لوحات ألوان، فصل لوحات BG/OBJ، تصادم البلاطات، تحريك السبرايت، صوت، HUD |
| الحجم | الروم 32 KiB · 182 بلاطة من 384 في VRAM |

| العنوان | اللعب | إنهاء الجولة |
| --- | --- | --- |
| ![title](images/title-screen.png) | ![strip](images/playtest-strip.png) | ![clear](images/clear-screen.png) |

الشريط على اليمين إطارات التقطها `tools/playtest.py` أثناء تشغيل الروم فعليًا —
العنوان → البدء → المشي يمينًا والتقاط نجمة (SCORE 00→01، STAR 6→5) → الحركة → العودة إلى العنوان.
**المعيار هو «ظهر على الشاشة»، لا «تم البناء».**

## شغّلها في أي مكان

`.gbc` روم قياسي لجهاز Game Boy Color، لذا يعمل الملف نفسه في كل ما يلي.

| الجهاز | الطريقة |
| --- | --- |
| **R36S (ArkOS)** | انسخه إلى مجلد GBC في قسم `EASYROMS` على بطاقة microSD → نواة Gambatte أو SameBoy (التفاصيل أدناه) |
| **Miyoo Mini (Onion) وAnbernic RG35XX وغيرها** | بالطريقة نفسها — ضعه في مجلد رومات GBC على الجهاز |
| **iPhone / iPad** | افتح ملف `.gbc` في تطبيق Delta |
| **PC / Mac** | SameBoy وmGBA |
| **العتاد الأصلي** | Game Boy Color مع خرطوشة فلاش |

### وضعها على R36S

1. ضع بطاقة microSD في الكمبيوتر وافتح قسم **EASYROMS** (وليس `BOOT`).
2. انسخ ملف `.gbc` إلى مجلد GBC — عادةً `EASYROMS/roms/gbc/`، وأحيانًا `EASYROMS/gbc/` حسب الصورة.
   أسماء المجلدات حساسة لحالة الأحرف. إن لم تظهر اللعبة، فالمجلد هو الخطأ وليس الروم.
3. شغّلها. استخدم نواة **Gambatte** (الافتراضية، كافية) أو **SameBoy** (الأدق).
4. إعداد الشاشة: شاشة GBC هي 160×144، أي **10:9** تمامًا، بينما شاشة R36S هي 640×480 (4:3).
   في `الإعدادات → الفيديو → التحجيم`، اختر **Aspect Ratio: Core Provided** و**Integer Scale: ON → 480×432 (3×)**.
   تستقر البكسلات على شبكة مربعة نظيفة. التحجيم 4× (640×576) لا يتسع في 480 صفًا، فيعود إلى 3× على أي حال.
   خيار «ملء الشاشة» يمدّ 10:9 إلى 4:3، أي أوسع بنحو 20% — غير مستحسن لفن البكسل.

## ما يوجد في المستودع

```
SKILL.md                  دليل الوكيل — قيود العتاد، واجهة GBDK، حلقة البناء والاختبار
AGENTS.md / CLAUDE.md     قواعد مختصرة يقرأها Codex وClaude Code من جذر المستودع
tools/
  png2gbc.py              PNG → بلاطات 8×8 2bpp + كود C للوحة BGR555 (+ معاينة شبكة البلاطات)
  artfont.py              يرسم الشعارات والنصوص في PNG بخط 5×7 بكسل
  playtest.py             تشغيل PyBoy بلا واجهة + تسلسل مفاتيح + شريط لقطات
  check_env.sh            فحص GBDK / python / pillow / pyboy
templates/minimal-gbc/    اللعبة النموذجية العاملة "TILE HOP" (عنوان → لعب → نقاط → إنهاء)
docs/images/              لقطات الفحص (بما فيها الـ GIF أعلاه)
docs/ci.md                نص سير عمل CI الكامل + طريقة تسجيله مرة واحدة (غير مسجَّل بعد)
```

## اربطها بوكيلك

| الأداة | كيف يُقرأ |
| --- | --- |
| **Claude Code** | افتح المستودع فيقرأ `CLAUDE.md`. اطلب مثلًا «انسخ TILE HOP وحوّلها إلى لعبة إطلاق نار» فيتبع قواعد `SKILL.md`. |
| **Codex / وكلاء آخرون** | يقرؤون `AGENTS.md`. إن كانت أداتك لا تقرأ أيًّا منهما، أضف سطرًا في بداية المحادثة يطلب قراءة `SKILL.md`. |
| **صيغة Claude Skill** | يحتوي `SKILL.md` على frontmatter (`name` و`description`)، فهو وثيقة مهارة قياسية تُوضع كما هي في مجلد المهارات. |

ما تفرضه المهارة: ميزانية 384 بلاطة في VRAM، و4 ألوان لكل بلاطة، ومحاذاة 8×8، و40 مدخل OAM بعشرة لكل سطر مسح،
وحلقة `vsync()`، وحمايات سجلات CGB، و**النظر دائمًا إلى شريط الاختبار بعد البناء**.

## الحلقة (كما هي مكتوبة في المهارة)

1. **فقرة تصميم + سطر معيار نجاح** — «المشي يمينًا 36 إطارًا، والتقاط نجمة، وتحوّل النقاط من 0 إلى 1»
2. **فن PNG** → حوّل البلاطات واللوحات بـ `tools/png2gbc.py`، وافحص المعاينة بعينك
3. **كود C** — انسخ `templates/minimal-gbc/src/main.c` وعدّله
4. **البناء** — `./build.sh` (lcc)
5. **الاختبار** — شغّل سكربت مفاتيح → احصل على شريط PNG
6. **افتح الشريط بنفسك** → أصلح وكرّر
7. **احفظ الدليل** — الشرائط واللقطات في `docs/images/`، مع رابط من README

## ثلاث أدوات

```bash
# 1) الفن: السبرايت 3 ألوان + شفافية، والخلفية 4 ألوان.
#    --dedup يدمج البلاطات المتطابقة، و--palette يثبّت اللوحة
python3 tools/png2gbc.py assets/player.png --mode sprite --name player -o src/gen/player
python3 tools/png2gbc.py assets/level.png  --mode bg --map --dedup --name level -o src/gen/level

# 2) النص: ارسم الشعارات والعبارات في PNG بخط 5×7 (بمضاعفات صحيحة)
python3 tools/artfont.py "PRESS START" --scale 2 --color "#FFEBC2" --out press.png

# 3) الاختبار: wait / press / hold / release / snap
python3 tools/playtest.py --rom build/tile-hop.gbc \
  --script "wait:40,press:start:4,wait:20,snap:play,hold:right:40,release:right,snap:score" \
  --out build/strip.png
```

ينبّه `playtest.py` أيضًا إلى الأخطاء الكلاسيكية: «كل الإطارات متطابقة (= الإدخال لا يصل إلى اللعبة)»،
«لونان أو أقل (= مشكلة في اللوحة أو العرض)»، «إطار فارغ». عامل التحذير كخطأ وأصلحه.

## ملخص العتاد (المزيد في `SKILL.md`)

| العنصر | القيمة |
| --- | --- |
| الشاشة | 160×144 (20×18 بلاطة) |
| البلاطة | 8×8، 2bpp = 4 ألوان لكل بلاطة، 16 بايتًا |
| VRAM | 384 بلاطة (8 KiB) — الخلفية والسبرايت يتشاركان **المساحة نفسها** |
| اللوحات | 8 BG + 8 OBJ × 4 ألوان، BGR555 بطول 15 بت |
| السبرايت | 40 مدخل OAM، **10 لكل سطر مسح** |
| الإطار | 59.7 إطارًا/ثانية، نحو 70,224 دورة |
| الصوت | 4 قنوات (موجتان مربعتان، موجة، ضجيج) |

## CI

[`docs/ci.md`](ci.md) يحتوي سير العمل الكامل — يجلب مشغّل Ubuntu إصدار GBDK-2020 4.5.0، ويبني
`templates/minimal-gbc`، ويفحص ترويسة الروم (الحجم، العنوان، نوع الخرطوشة `0x1B`، علم CGB `0x80`)، ويشغّل
اختبار PyBoy بـ `--strict`، ثم يرفع ملف `.gbc` وشريط اللقطات كمنتجات.

> هذا المستودع **لا يحتوي بعد** على `.github/workflows/build-rom.yml` مسجَّلًا. رمز GitHub المستخدم في الدفعة الأولى
> لم يكن يملك إذن `workflows`، فرفض GitHub ذلك الملف. الصق ملف `docs/ci.md` مرة واحدة في واجهة الويب،
> وسيعمل عند كل دفعة بعد ذلك.

## الشكر

- المترجم: [GBDK-2020](https://github.com/gbdk-2020/gbdk-2020) (فوق SDCC)
- المحاكي: [PyBoy](https://github.com/Baekalfen/PyBoy) — للفحص بلا واجهة
- المراجع: Pan Docs (عتاد Game Boy)، وGBDK 2020 Docs
- الإلهام: OpenAI × ModRetro **Chromatic: Codex Edition**

رخصة MIT — انظر [LICENSE](../LICENSE). اصنع الألعاب وعدّلها وبعها.
الأسئلة والأخطاء إلى [Issues](https://github.com/dong3789/retro-game-creator/issues)؛ والألعاب التي تصنعها بهذه المجموعة مرحّب بها دائمًا.
