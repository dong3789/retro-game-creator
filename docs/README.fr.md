# Retro Game Creator

[English](../README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh.md) · [Português](README.pt.md) · **Français** · [العربية](README.ar.md) · [हिन्दी](README.hi.md)

**Demandez à un agent de codage IA de créer un jeu et vous obtenez une vraie ROM Game Boy Color (`.gbc`).**

<p align="center">
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/output-.gbc-8b6b2e.svg" alt="Output: .gbc ROM">
  <img src="https://img.shields.io/badge/compiler-GBDK--2020%204.5.0-2f9e44.svg" alt="Compiler: GBDK-2020 4.5.0">
  <img src="https://img.shields.io/badge/agents-Claude%20Code%20%2B%20Codex-6e56cf.svg" alt="Agents: Claude Code and Codex">
</p>

<p align="center">
  <img src="images/gameplay.gif" width="480" alt="TILE HOP, le jeu d'exemple, en cours d'exécution dans un émulateur">
</p>

Un document de skill (`SKILL.md`), trois outils d'automatisation, et un jeu d'exemple réellement compilé et validé par un playtest.

Il reprend la méthode montrée par le [Chromatic](https://openai.com/fr-FR/supply/co-lab/chromatic/) d'OpenAI × ModRetro (une console portable compatible avec le matériel Game Boy) — l'IA écrit du C, GBDK grave une ROM, puis les images de l'émulateur sont vérifiées à l'œil — pour la faire tourner sur du matériel que vous possédez déjà, plutôt que sur un appareil à 200 $.

`R36S · Miyoo Mini · Anbernic · iPhone (Delta) · émulateurs PC et web · matériel d'origine` — un seul fichier `.gbc` tourne partout.

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

Ouvrez `build/strip.png`. C'est ça, le jeu.

Récupérez GBDK-2020 sur la [page des releases](https://github.com/gbdk-2020/gbdk-2020/releases), décompressez-le n'importe où et
`export GBDKDIR=/chemin/gbdk/` (**gardez le `/` final**). `build.sh` cherche aussi dans `/opt/gbdk`, `~/gbdk` et quelques autres endroits, et compile sans `make`.

## Le jeu d'exemple — TILE HOP

Pas une coquille vide : un jeu qui va de l'écran-titre au jeu, au score et à la fin de manche. Copiez-le et commencez à le modifier.

| | |
| --- | --- |
| Commandes | D-pad pour se déplacer, `START` pour commencer, `SELECT` pour revenir au titre |
| But | Mangez les 6 étoiles pour voir `CLEAR!`, puis les étoiles sont replacées et le score repart à zéro (sans fin) |
| Ce qu'il contient | 5 palettes de couleurs, palettes BG/OBJ séparées, collisions par tuiles, animation de sprites, son, HUD |
| Taille | ROM 32 KiB · 182 tuiles sur 384 de VRAM |

| Titre | Jeu | Manche terminée |
| --- | --- | --- |
| ![title](images/title-screen.png) | ![strip](images/playtest-strip.png) | ![clear](images/clear-screen.png) |

La bande de droite, ce sont des images capturées par `tools/playtest.py` en faisant vraiment tourner la ROM —
titre → start → marcher à droite et prendre une étoile (SCORE 00→01, STAR 6→5) → déplacement → retour au titre.
**Le critère, c'est « ça s'affiche à l'écran », pas « ça compile ».**

## Lancez-le n'importe où

`.gbc` est une ROM Game Boy Color standard : le même fichier tourne partout ci-dessous.

| Appareil | Comment |
| --- | --- |
| **R36S (ArkOS)** | Copiez dans le dossier GBC de la partition `EASYROMS` de la microSD → cœur Gambatte ou SameBoy (détails plus bas) |
| **Miyoo Mini (Onion), Anbernic RG35XX, …** | Même principe — déposez le fichier dans le dossier de ROM GBC de la console |
| **iPhone / iPad** | Ouvrez le `.gbc` dans l'app Delta |
| **PC / Mac** | SameBoy, mGBA |
| **Matériel d'origine** | Game Boy Color + linker (flash cart) |

### Mettre le jeu sur une R36S

1. Mettez la microSD dans le PC et ouvrez la partition **EASYROMS** (pas `BOOT`).
2. Copiez le `.gbc` dans le dossier GBC — en général `EASYROMS/roms/gbc/`, parfois `EASYROMS/gbc/` selon l'image.
   Les noms de dossiers respectent la casse. Si le jeu n'apparaît pas, c'est le dossier qui est faux, pas la ROM.
3. Lancez. Cœur **Gambatte** (par défaut, très bien) ou **SameBoy** (le plus précis).
4. Affichage : la GBC est en 160×144, exactement **10:9**, alors que l'écran de la R36S est en 640×480 (4:3).
   Dans `Réglages → Vidéo → Mise à l'échelle`, mettez **Aspect Ratio: Core Provided** et **Integer Scale: ON → 480×432 (×3)**.
   Les pixels tombent sur une grille carrée nette. Le ×4 (640×576) ne tient pas dans 480 lignes, il retombe donc sur ×3 de toute façon.
   « Remplir l'écran » étire le 10:9 en 4:3, environ 20 % plus large — déconseillé pour le pixel art.

## Ce qu'il y a dans le dépôt

```
SKILL.md                  le guide pour l'agent — limites matérielles, API GBDK, boucle build/playtest
AGENTS.md / CLAUDE.md     règles résumées que Codex et Claude Code lisent à la racine du dépôt
tools/
  png2gbc.py              PNG → tuiles 8×8 2bpp + code C de palette BGR555 (+ aperçu de la grille de tuiles)
  artfont.py              dessine logos et textes dans un PNG avec une police 5×7 pixels
  playtest.py             exécution headless de PyBoy + séquence de touches + bande de captures
  check_env.sh            vérifie GBDK / python / pillow / pyboy
templates/minimal-gbc/    le jeu d'exemple qui fonctionne : "TILE HOP" (titre → jeu → score → manche terminée)
docs/images/              captures de vérification (dont le GIF ci-dessus)
docs/ci.md                le workflow CI complet + comment l'enregistrer une fois (pas encore dans le dépôt)
```

## Branchez votre agent

| Outil | Comment il est lu |
| --- | --- |
| **Claude Code** | Ouvrez le dépôt, il lit `CLAUDE.md`. Demandez « copie TILE HOP et transforme-le en shoot'em up » et il suit les règles de `SKILL.md`. |
| **Codex / autres agents** | Ils lisent `AGENTS.md`. Si le vôtre ne lit ni l'un ni l'autre, ajoutez une ligne au début de la conversation pour lui dire de lire `SKILL.md`. |
| **Format Claude Skill** | `SKILL.md` a un frontmatter (`name`, `description`) : c'est un document de skill standard, déposez-le tel quel dans un dossier de skills. |

Ce que le skill impose : un budget de 384 tuiles de VRAM, 4 couleurs par tuile, un alignement sur 8×8, 40 entrées OAM dont 10 par ligne de balayage,
une boucle avec `vsync()`, des gardes sur les registres CGB, et **toujours regarder la bande de playtest après une compilation**.

## La boucle (telle qu'écrite dans le skill)

1. **Un paragraphe de design + une ligne de critère** — « marcher 36 frames à droite, manger une étoile, le score passe de 0 à 1 »
2. **Art en PNG** → convertir tuiles et palettes avec `tools/png2gbc.py`, vérifier l'aperçu à l'œil
3. **Code C** — copier `templates/minimal-gbc/src/main.c` et le modifier
4. **Compiler** — `./build.sh` (lcc)
5. **Playtest** — lancer un script de touches → obtenir une bande PNG
6. **Ouvrir la bande soi-même** → corriger et recommencer
7. **Garder la preuve** — bandes et captures dans `docs/images/`, liées depuis le README

## Trois outils

```bash
# 1) art : les sprites ont 3 couleurs + transparence, les fonds 4 couleurs.
#    --dedup fusionne les tuiles identiques, --palette fixe la palette
python3 tools/png2gbc.py assets/player.png --mode sprite --name player -o src/gen/player
python3 tools/png2gbc.py assets/level.png  --mode bg --map --dedup --name level -o src/gen/level

# 2) texte : dessine logos et phrases dans un PNG avec une police 5×7 (échelle entière)
python3 tools/artfont.py "PRESS START" --scale 2 --color "#FFEBC2" --out press.png

# 3) playtest : wait / press / hold / release / snap
python3 tools/playtest.py --rom build/tile-hop.gbc \
  --script "wait:40,press:start:4,wait:20,snap:play,hold:right:40,release:right,snap:score" \
  --out build/strip.png
```

`playtest.py` signale aussi les échecs classiques : « toutes les images sont identiques (= l'entrée n'arrive pas au jeu) »,
« deux couleurs ou moins (= problème de palette/affichage) », « image vide ». Traitez l'avertissement comme un bug et corrigez-le.

## Aide-mémoire matériel (plus dans `SKILL.md`)

| Élément | Valeur |
| --- | --- |
| Écran | 160×144 (20×18 tuiles) |
| Tuile | 8×8, 2bpp = 4 couleurs par tuile, 16 octets |
| VRAM | 384 tuiles (8 Kio) — décor et sprites partagent **le même espace** |
| Palettes | 8 BG + 8 OBJ × 4 couleurs, BGR555 15 bits |
| Sprites | 40 entrées OAM, **10 par ligne de balayage** |
| Image | 59,7 fps, ~70 224 cycles |
| Son | 4 canaux (2 ondes carrées, 1 onde, 1 bruit) |

## CI

[`docs/ci.md`](ci.md) contient le workflow complet — un runner Ubuntu récupère GBDK-2020 4.5.0, compile
`templates/minimal-gbc`, vérifie l'en-tête de la ROM (taille, titre, type de cartouche `0x1B`, drapeau CGB `0x80`), lance le
playtest PyBoy avec `--strict`, puis envoie le `.gbc` et la bande de captures en artefacts.

> Ce dépôt n'a **pas encore** de `.github/workflows/build-rom.yml` enregistré. Le token GitHub utilisé pour le
> premier push n'avait pas la permission `workflows`, donc GitHub a refusé ce fichier. Collez le fichier de `docs/ci.md`
> une fois dans l'interface web, et il tournera à chaque push ensuite.

## Crédits

- Compilateur : [GBDK-2020](https://github.com/gbdk-2020/gbdk-2020) (basé sur SDCC)
- Émulateur : [PyBoy](https://github.com/Baekalfen/PyBoy) — pour la vérification headless
- Références : Pan Docs (matériel Game Boy), GBDK 2020 Docs
- Inspiration : OpenAI × ModRetro **Chromatic: Codex Edition**

MIT License — voir [LICENSE](../LICENSE). Créez des jeux, modifiez-les, vendez-les.
Questions et bugs : [Issues](https://github.com/dong3789/retro-game-creator/issues) ; les jeux faits avec ce kit sont toujours les bienvenus.
