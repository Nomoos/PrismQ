# Kontrola běhu modulu: PrismQ.V.Video

## 🎯 Účel modulu
Assembly finálního video z audio, keyframes a transitions. Modul kombinuje všechny assets (voiceover, keyframes, text overlays, transitions) do finálního video souboru ready for publishing.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Audio z modulu 25, keyframes z modulu 27
- **Typ dat:** Audio files, image files, scene data
- **Povinné hodnoty:**
  - Enhanced audio voiceover
  - Keyframe images pro všechny scény
  - Scene timing data
- **Nepovinné hodnoty:**
  - `--preview`, `--debug` flags
  - Intro/outro templates
  - Logo/brand elements
  - Background music
- **Očekávané předpoklady:**
  - Audio a keyframes ready
  - Video editing software/library (FFmpeg, MoviePy)
  - Video storage
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Load assets:**
   - Audio voiceover
   - Keyframe images (ordered by scene)
   - Scene timing data
   - Intro/outro clips (optional)
2. **Video composition:**
   - **Intro sequence** (5-10s):
     - Brand logo animation
     - Title card s episode title
   - **Main content**:
     - Pro každou scénu:
       - Display keyframe image
       - Sync s audio timing
       - Add Ken Burns effect (zoom/pan) pro movement
       - Add text overlays (key points)
       - Transitions between scenes (dissolve, fade)
   - **Outro sequence** (5-10s):
     - CTA (call-to-action)
     - Subscribe prompt
     - Social media handles
     - Logo
3. **Effects a enhancements:**
   - Color grading (consistent look)
   - Add subtle animations
   - Text overlays s key points
   - Lower thirds (captions, names)
   - Background blur effects (pokud needed)
4. **Audio finalization:**
   - Sync audio perfectly s video
   - Add background music (low volume)
   - Fade in/out music
   - Audio ducking (lower music when voiceover)
5. **Subtitles/captions:**
   - Generate subtitles from audio transcript
   - Sync subtitles s audio
   - Style subtitles (font, color, position)
6. **Export:**
   - Render video multiple resolutions:
     - 4K (3840x2160) pro YouTube
     - 1080p (1920x1080) universal
     - 720p (1280x720) pro slower connections
   - Optimize pro streaming (H.264/H.265)
   - Generate thumbnail image
7. **Quality check:**
   - Audio-video sync verification
   - Visual quality check
   - Subtitle accuracy check
8. **Update Story:**
   - Uložení video paths/URLs
   - State změna na "VideoReady" nebo "PrismQ.P.Publishing"

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** Finální video soubor ready for publishing
- **Formát výstupu:** 
  - MP4 (H.264/H.265) multiple resolutions
  - Thumbnail image
  - Subtitle files (SRT, VTT)
- **Vedlejší efekty:** 
  - Render logs
  - Quality metrics
  - Preview video (lower resolution)
- **Chování při chybě:** 
  - Render error: Retry s different parameters
  - Quality issues: Re-render s adjustments

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 25 (PrismQ.A.Publishing) - enhanced audio
- Modul 27 (PrismQ.V.Keyframe) - keyframe images
- Modul 26 (PrismQ.V.Scene) - scene timing data
- Video editing tools (FFmpeg, MoviePy, Premiere Pro API)
- Video storage
- Databáze

**Výstupní závislosti:**
- Modul 29 (PrismQ.P.Publishing) - multi-platform publishing
- Direct YouTube/video platform upload

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Video rendering je computationally expensive
- Multiple resolutions maximize platform compatibility
- Subtitles critical pro accessibility a engagement
- Ken Burns effects add visual interest na static images
- Background music enhances production value
- Audio-video sync critical pro quality
- Thumbnail může significantly affect click-through rate

**Rizika:**
- **Render time**: 4K video rendering velmi slow (minutes to hours)
- **File size**: 4K videos jsou large (storage a bandwidth)
- **Audio-video desync**: Timing issues mohou occur
- **Quality loss**: Compression může degrade quality
- **Subtitle errors**: Auto-generated subtitles mohou mít chyby
- **Memory consumption**: Rendering může require significant RAM
- **CPU/GPU requirements**: Hardware intensive process

**Doporučení:**
- Cloud rendering services pro heavy workloads
- Preview renders (lower quality) pro rychlé feedback
- Quality templates pro consistent output
- Automated sync verification
- Human review subtitle accuracy
- Multiple resolution export pro different platforms
- Optimize file sizes pro faster uploads
- Generate engaging thumbnails (A/B test)
- Version control video projects
- Backup raw assets long-term
- Monitor render queue a failures
- Hardware acceleration (GPU rendering)
