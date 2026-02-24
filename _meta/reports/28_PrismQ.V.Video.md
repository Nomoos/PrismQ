# Kontrola běhu modulu: PrismQ.V.Video

**Účel:** Assembly finálního videa z audio, keyframes a transitions — včetně titulků, efektů a multi-resolution exportu.

---

## 📥 Vstup
- **Zdroj:** Audio z modulu 25, keyframes z modulu 27, scene timing z modulu 26
- **Data:** Enhanced audio, keyframe images, scene timing data, intro/outro templates (optional)
- **Předpoklady:** Audio a keyframes ready, FFmpeg/MoviePy, video storage

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Video composition — intro (logo, title card), main content (keyframes + Ken Burns + text overlays + transitions), outro (CTA, subscribe)
3. Effects — color grading, subtle animations, lower thirds, background blur
4. Audio finalization — sync voiceover, background music (ducking), fade in/out
5. Subtitles — generate z audio transcript, sync, style (font, color, position)
6. Export — render 4K (3840x2160), 1080p, 720p; H.264/H.265; generate thumbnail
7. Quality check — audio-video sync, visual quality, subtitle accuracy
8. [Uložení výsledků](shared/databazova_integrace.md) — save video, update Story: video paths, `state="PrismQ.P.Publishing"`

---

## 📤 Výstup
- **Primární:** Finální video (MP4 H.264/H.265) ve více rozlišeních + thumbnail + subtitles (SRT/VTT)
- **DB změny:** Tabulka `Story` — video paths/URLs, subtitle paths, `state="PrismQ.P.Publishing"`
- **Další krok:** Modul 29 (PrismQ.P.Publishing)
