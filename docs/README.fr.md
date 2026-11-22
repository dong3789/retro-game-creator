# Retro Game Creator

[English](../README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh.md) · [Português](README.pt.md) · **Français** · [العربية](README.ar.md) · [हिन्दी](README.hi.md)

**Demandez un jeu à un agent de code IA, et vous obtenez une vraie ROM Game Boy Color (`.gbc`).**

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/output-.gbc-8b6b2e.svg" alt="Output: .gbc ROM">
  <img src="https://img.shields.io/badge/compiler-GBDK--2020%204.5.0-2f9e44.svg" alt="Compiler: GBDK-2020 4.5.0">
  <img src="https://img.shields.io/badge/games_shipped-2-ff6b6b.svg" alt="Games shipped: 2">
  <img src="https://img.shields.io/badge/agents-Claude%20Code%20%2B%20Codex-6e56cf.svg" alt="Agents: Claude Code and Codex">
</p>

<p align="center">
  <img src="images/bungeoppang-plus-gameplay.gif" width="320" alt="Bungeoppang Tycoon Plus en jeu : un stand de marché de nuit, quatre moules sur la plaque, une commande et une vente">
</p>
<p align="center">
  <em>Bungeoppang Tycoon Plus — construit avec ce kit, capturé depuis la ROM publiée.
  <a href="https://github.com/dong3789/bungeoppang-tycoon-plus-gbc">dépôt</a> ·
  <a href="https://github.com/dong3789/bungeoppang-tycoon-plus-gbc/releases/tag/v1.0">jouer</a></em>
</p>

Un document de skill (`SKILL.md`), trois outils d'automatisation, un modèle de départ — et **deux jeux complets bel et bien sortis**, jouables sur la console qui est déjà dans votre sac.

C'est le flux que la [Chromatic](https://openai.com/en-US/supply/co-lab/chromatic/) d'OpenAI × ModRetro (une console compatible Game Boy) a montré — l'IA écrit du C, GBDK grave une ROM, et les images de l'émulateur se vérifient à l'œil — ramené sur du matériel que vous possédez déjà, au lieu d'un appareil à 200 $.

`R36S · Miyoo Mini · Anbernic · iPhone (Delta) · émulateurs bureau et web · matériel réel` — un seul fichier `.gbc` tourne partout.

---

## Vitrine — fait avec ce kit

Deux jeux, tous deux publiés en `.gbc`. Ils sortent de la même boucle que ce dépôt impose : écrire du C d'après `SKILL.md`, compiler avec GBDK-2020, rejouer la ROM en aveugle avec `tools/playtest.py`, regarder les images, corriger, recommencer. Chaque animation et bande ci-dessous vient de la **ROM publiée** — pas d'illustration.

### 1. Bungeoppang Tycoon Plus

> Un stand de gâteaux-poissons au marché de nuit, 90 secondes au compteur.

[Dépôt](https://github.com/dong3789/bungeoppang-tycoon-plus-gbc) · [Version v1.0 · `bungeoppang-plus.gbc` (32 Kio)](https://github.com/dong3789/bungeoppang-tycoon-plus-gbc/releases/tag/v1.0)

| | |
| --- | --- |
| Genre | Jeu de cuisine en 90 secondes, course au score |
| La boucle | Quatre moules sur la plaque, quatre garnitures — BEAN / CREAM / CHEESE / PIZZA. Verser la pâte, attendre le doré, vendre la garniture que le client a demandée |
| Commandes | Croix : choisir un moule · **A** : verser / servir / gratter un brûlé · **B** : changer de garniture (maintenir pour répéter) · **SELECT** : sens inverse · **START** : démarrer, recommencer |
| Profondeur | Le client arrive avec une garniture et une barre de patience, le combo monte à chaque vente correcte, et le service se termine par une note S/A/B/C sur la recette (S = 6000 pièces) |
| Budget matériel | 246 des 256 indices de tuiles de fond, 28 des 40 sprites OAM. Les quatre garnitures partagent les mêmes tuiles et ne diffèrent que par la palette — changer ne coûte aucune VRAM |
| ROM | CGB uniquement (`0xC0`), 32 Kio, MBC5+RAM+pile (`0x1B`) |

<p align="center"><img src="images/bungeoppang-plus-strip.png" width="848" alt="Cinq images de Bungeoppang Tycoon Plus : titre, un client qui demande une garniture, la pâte dans le premier moule, le doré, une vente à 100 pièces"></p>

La bande, ce sont cinq images tirées de la ROM publiée : l'écran-titre, un client qui demande CREAM, la pâte dans le premier moule, le doré, et la vente (`GOLD 100 · COMBO 1`).

### 2. Ramen Time

> Trois manches, cinq étapes, un bouton — et un curseur plus rapide que vous.

[Dépôt](https://github.com/dong3789/ramen-time-gbc) · [Version v1.0 · `ramen-time.gbc` (32 Kio)](https://github.com/dong3789/ramen-time-gbc/releases/tag/v1.0)

| | |
| --- | --- |
| Genre | Jeu de cuisine rythmé, tout en timing |
| La boucle | **BOIL → NOODLES → SOUP → TOPPING → STOP**, cinq fois par manche, trois manches. Appuyer quand le curseur est dans la fenêtre verte |
| Commandes | **A** : le timing (et l'œuf en TOPPING) · **B** : la cébette · **START** : démarrer / rejouer · **SELECT** : retour au titre |
| Profondeur | PERFECT, ce sont les 16 px du centre d'une jauge de 112 px (100 pts), GOOD vaut 60, un raté vaut 0 ; le curseur avance de 1 px toutes les 2 images en manche 1, 1 px par image en manche 2, 2 px par image en manche 3 ; arrêter trop tôt donne des nouilles HARD, trop tard SOGGY. 1260 est une partie parfaite |
| Budget matériel | 215 tuiles de fond + 3 de sprite sur les 384 emplacements VRAM, 3 des 40 sprites OAM — la casserole change en échangeant une ligne de tuiles par étape |
| ROM | Compatible CGB (`0x80`), 32 Kio, MBC5+RAM+pile (`0x1B`) |

<p align="center"><img src="images/ramen-time-gameplay.gif" width="320" alt="Ramen Time en jeu : la casserole bout, le curseur balaie la jauge, PERFECT à 100 points, puis les nouilles tombent"></p>

<p align="center"><img src="images/ramen-time-strip.png" width="848" alt="Cinq images de Ramen Time : titre, BOIL avec le curseur en mouvement, PERFECT +100, NOODLES et la carte de résultat avec note S et 1260 points"></p>

La carte de résultat à droite vient d'une vraie partie de 15 phases, menée en lisant le sprite du curseur dans la mémoire de l'émulateur : note **S**, score **1260**, *PERFECT NOODLES*.

**Ce que les deux jeux ont en commun, c'est justement le point :** une boucle entrée → score → note qui va au bout, une variation graphique par la seule palette, et une bande de playtest qu'un humain peut réellement lire. C'est la barre que ce kit exige.

---

## Démarrage en 30 secondes

```bash
git clone https://github.com/dong3789/retro-game-creator.git
cd retro-game-creator

./tools/check_env.sh                 # GBDK, python, pillow, pyboy
./templates/minimal-gbc/build.sh     # compile la ROM d'exemple → build/tile-hop.gbc

python3 tools/playtest.py --rom templates/minimal-gbc/build/tile-hop.gbc \
  --script "wait:8,press:start:4,wait:16,hold:right:36,snap:score" \
  --out build/strip.png
```

Ouvrez `build/strip.png`. C'est le jeu.

Récupérez GBDK-2020 sur la [page des versions](https://github.com/gbdk-2020/gbdk-2020/releases), décompressez-le où vous voulez, puis
`export GBDKDIR=/chemin/vers/gbdk/` (**gardez le `/` final**). `build.sh` cherche aussi dans `/opt/gbdk`, `~/gbdk` et quelques autres endroits, et compile sans `make`.

## Modèle de départ — TILE HOP

`templates/minimal-gbc/` est la base que vous copiez. Pas une coquille vide : elle va de l'écran-titre au jeu, au score et au clear, donc chaque pièce à conserver (boucle `vsync()`, détection de front sur le joypad, tilemap, sprite, son, HUD) est déjà câblée.

| | |
| --- | --- |
| Commandes | Croix pour se déplacer, `START` pour commencer, `SELECT` pour revenir au titre |
| Objectif | Manger les 6 étoiles pour `CLEAR!`, puis les étoiles sont redistribuées et le score repart à zéro (infini) |
| Ce qu'il contient | 5 palettes de couleurs, palettes BG/OBJ séparées, collisions par tuiles, animation de sprite, son, HUD |
| Taille | ROM 32 Kio · 182 tuiles sur 384 de VRAM |

| Titre | Jeu | Clear |
| --- | --- | --- |
| ![title](images/title-screen.png) | ![strip](images/playtest-strip.png) | ![clear](images/clear-screen.png) |

La bande du milieu, ce sont les images capturées par `tools/playtest.py` en faisant tourner la ROM pour de vrai —
titre → start → marcher à droite et prendre une étoile (SCORE 00→01, STAR 6→5) → se déplacer → retour au titre.
**La barre, c'est « ça s'affiche à l'écran », pas « ça compile ».**

## Lancer partout

`.gbc` est une ROM Game Boy Color standard, donc le même fichier tourne partout ci-dessous — y compris les deux jeux de la vitrine.

| Appareil | Comment |
| --- | --- |
| **R36S (ArkOS)** | Copier dans le dossier GBC de la partition `EASYROMS` de la microSD → cœur Gambatte ou SameBoy (détails plus bas) |
| **Miyoo Mini (Onion), Anbernic RG35XX, …** | Même principe — déposez-la dans le dossier de ROM GBC de la console |
| **iPhone / iPad** | Ouvrir le `.gbc` dans l'app Delta |
| **PC / Mac** | SameBoy, mGBA |
| **Matériel réel** | Game Boy Color + un linker |

### Sur une R36S

1. Mettez la microSD dans le PC et ouvrez la partition **EASYROMS** (pas `BOOT`).
2. Copiez le `.gbc` dans le dossier GBC — en général `EASYROMS/roms/gbc/`, parfois `EASYROMS/gbc/` selon l'image.
   Les noms de dossier sont sensibles à la casse. Si le jeu n'apparaît pas, c'est le dossier qui est faux, pas la ROM.
3. Lancez. Prenez le cœur **Gambatte** (par défaut, très bien) ou **SameBoy** (le plus fidèle).
4. Affichage : le GBC est en 160×144, exactement **10:9**, alors que la dalle de la R36S est en 640×480 (4:3).
   Dans `Settings → Video → Scaling`, mettez **Aspect Ratio: Core Provided** et **Integer Scale: ON → 480×432 (3×)**.
   Les pixels tombent sur une grille carrée nette. Le 4× (640×576) ne tient pas dans 480 lignes, il retombe donc sur 3× de toute façon.
   « Remplir l'écran » étire le 10:9 en 4:3, environ 20 % plus large — déconseillé pour le pixel art.

## Contenu du dépôt

```
SKILL.md                  le guide destiné à l'agent — limites matérielles, API GBDK, boucle build/playtest
AGENTS.md / CLAUDE.md     règles résumées que Codex et Claude Code lisent à la racine
tools/
  png2gbc.py              PNG → tuiles 8×8 2bpp + code C de palette BGR555 (+ aperçu de la grille de tuiles)
  artfont.py                dessine logos et textes dans un PNG avec une police 5×7
  playtest.py             exécution PyBoy sans fenêtre + script de touches + bande de captures
  check_env.sh            vérifie GBDK / python / pillow / pyboy
templates/minimal-gbc/    le jeu de départ « TILE HOP » (titre → jeu → score → clear)
docs/images/              captures et GIF tirés de vraies ROM (les deux jeux de la vitrine + TILE HOP)
docs/ci.md                le workflow CI complet + comment l'enregistrer une fois (pas encore dans le dépôt)
```

Les deux jeux de la vitrine vivent dans leurs propres dépôts —
[`bungeoppang-tycoon-plus-gbc`](https://github.com/dong3789/bungeoppang-tycoon-plus-gbc) et
[`ramen-time-gbc`](https://github.com/dong3789/ramen-time-gbc) — avec tout le code, les scripts de build et les captures dans `docs/`.

## Brancher votre agent

| Outil | Comment il est lu |
| --- | --- |
| **Claude Code** | Ouvrez le dépôt et il lit `CLAUDE.md`. Demandez « copie TILE HOP et transforme-le en shoot'em up » et il suit les règles de `SKILL.md`. |
| **Codex / autres agents** | Ils lisent `AGENTS.md`. Si le vôtre ne lit ni l'un ni l'autre, collez une ligne au début de la conversation pour lui dire de lire `SKILL.md`. |
| **Format Claude Skill** | `SKILL.md` a son frontmatter (`name`, `description`), il se dépose donc tel quel dans un dossier de skills. |

Ce que le skill impose : un budget de 384 tuiles de VRAM, 4 couleurs par tuile, un alignement 8×8, 40 entrées OAM dont 10 par ligne de balayage,
une boucle `vsync()`, des gardes sur les registres CGB, et **toujours regarder la bande de playtest après un build**.

## La boucle (telle qu'écrite dans le skill)

1. **Un paragraphe de design + une ligne réussite/échec** — « marcher 36 images vers la droite, manger une étoile, et le score passe de 0 à 1 »
2. **Art PNG** → convertir tuiles et palettes avec `tools/png2gbc.py`, vérifier l'aperçu à l'œil
3. **Code C** — copier `templates/minimal-gbc/src/main.c` et le modifier
4. **Build** — `./build.sh` (lcc)
5. **Playtest** — lancer un script de touches → obtenir une bande PNG
6. **Ouvrir la bande vous-même** → corriger et recommencer
7. **Garder la preuve** — bandes et captures dans `docs/images/`, liées depuis le README

Les deux jeux de la vitrine ont tourné dans cette boucle jusqu'à ce que la bande vaille le coup d'œil. Quand l'automatisation vaut mieux qu'une capture, lisez l'état du jeu en cours d'exécution plutôt que de deviner : le GIF de Ramen Time a été piloté en lisant le curseur dans la table d'attributs de sprites et en appuyant sur `A` dans la fenêtre parfaite, et celui de Bungeoppang en échantillonnant la commande du client dans le framebuffer pour choisir la garniture avec `B`.

## Trois outils

```bash
# 1) art : les sprites ont 3 couleurs + transparence, les fonds 4 couleurs.
#    --dedup fusionne les tuiles identiques, --palette fixe la palette
python3 tools/png2gbc.py assets/player.png --mode sprite --name player -o src/gen/player
python3 tools/png2gbc.py assets/level.png  --mode bg --map --dedup --name level -o src/gen/level

# 2) texte : dessiner logos et chaînes dans un PNG avec une police 5×7 (échelle entière)
python3 tools/artfont.py "PRESS START" --scale 2 --color "#FFEBC2" --out press.png

# 3) playtest : wait / press / hold / release / snap
python3 tools/playtest.py --rom build/tile-hop.gbc \
  --script "wait:40,press:start:4,wait:20,snap:play,hold:right:40,release:right,snap:score" \
  --out build/strip.png
```

`playtest.py` signale aussi les échecs classiques : « toutes les images sont identiques (= l'entrée n'arrive pas au jeu) »,
« deux couleurs ou moins (= problème de palette/affichage) », « image blanche ». Traitez l'avertissement comme un bug et corrigez.

## Aide-mémoire matériel (plus dans `SKILL.md`)

| Élément | Valeur |
| --- | --- |
| Écran | 160×144 (20×18 tuiles) |
| Tuile | 8×8, 2bpp = 4 couleurs par tuile, 16 octets |
| VRAM | 384 tuiles (8 Kio) — fond et sprites partagent **le même espace** |
| Palettes | 8 BG + 8 OBJ × 4 couleurs, BGR555 15 bits |
| Sprites | 40 entrées OAM, **10 par ligne de balayage** |
| Image | 59,7 fps, ~70 224 cycles |
| Son | 4 canaux (2 carrés, 1 onde, 1 bruit) |

## CI

[`docs/ci.md`](ci.md) contient le workflow complet — un runner Ubuntu récupère GBDK-2020 4.5.0, compile
`templates/minimal-gbc`, vérifie l'en-tête de la ROM (taille, titre, type de cartouche `0x1B`, drapeau CGB `0x80`), lance le
playtest PyBoy avec `--strict`, puis publie la `.gbc` et la bande de captures en artefacts.

> Ce dépôt n'a **pas encore** de `.github/workflows/build-rom.yml` enregistré. Le jeton GitHub utilisé pour le
> premier push n'avait pas la permission `workflows`, donc GitHub a refusé le fichier. Collez le fichier de `docs/ci.md`
> une fois dans l'interface web, et il tournera à chaque push ensuite.

## Crédits

- Compilateur : [GBDK-2020](https://github.com/gbdk-2020/gbdk-2020) (au-dessus de SDCC)
- Émulateur : [PyBoy](https://github.com/Baekalfen/PyBoy) — pour la revue sans fenêtre
- Références : Pan Docs (matériel Game Boy), GBDK 2020 Docs
- Inspiration : OpenAI × ModRetro **Chromatic: Codex Edition**

MIT License — voir [LICENSE](../LICENSE). Créez des jeux, modifiez-les, vendez-les.
Questions et bugs vont aux [Issues](https://github.com/dong3789/retro-game-creator/issues) ; les jeux faits avec ce kit sont toujours bienvenus.
