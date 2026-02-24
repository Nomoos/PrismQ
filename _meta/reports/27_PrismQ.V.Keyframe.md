# Kontrola běhu modulu: PrismQ.V.Keyframe

**Účel:** AI generování keyframe obrázků pro video scény pomocí image generation (Stable Diffusion, DALL-E, Midjourney).

---

## 📥 Vstup
- **Zdroj:** Scene plan z modulu 26
- **Data:** Scene descriptions, visual concepts, image generation parametry (style, resolution)
- **Předpoklady:** Scene plan z modulu 26, přístup k AI image generation API, image storage

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Prompt engineering — visual concept → detailed image prompt + style parametry (cinematic/realistic/illustrated) + negative prompts
3. AI image generation — volání API (Stable Diffusion/DALL-E), 2-3 varianty per scéna
4. Image selection — quality assessment, výběr nejlepšího variantu
5. Post-processing — resize pro video (1920x1080, 3840x2160), color correction, format conversion
6. [Uložení výsledků](shared/databazova_integrace.md) — save keyframes, update Story: keyframe paths, `state="PrismQ.V.Video"`

---

## 📤 Výstup
- **Primární:** Keyframe images pro každou scénu (PNG/JPG, high-resolution)
- **DB změny:** Tabulka `Story` — keyframe paths/URLs, `state="PrismQ.V.Video"`
- **Další krok:** Modul 28 (PrismQ.V.Video)
