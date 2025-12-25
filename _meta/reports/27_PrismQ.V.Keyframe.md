# Kontrola běhu modulu: PrismQ.V.Keyframe

## 🎯 Účel modulu
Generování keyframe obrázků pro video scény. Modul vytváří klíčové vizuální snímky pro každou scénu pomocí AI image generation (Stable Diffusion, DALL-E, Midjourney), připravuje visual assets pro video assembly.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Scene plan z modulu 26
- **Typ dat:** Scene descriptions, visual concepts
- **Povinné hodnoty:**
  - Scene plan s visual concepts
  - Image generation parameters (style, resolution)
- **Nepovinné hodnoty:**
  - `--preview`, `--debug` flags
  - Reference images
  - Style presets
- **Očekávané předpoklady:**
  - Scene plan z modulu 26
  - Přístup k AI image generation API
  - Image storage
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Pro každou scénu:**
   - Load scene visual concept
   - Prepare image generation prompt
2. **Prompt engineering:**
   - Convert visual concept → detailed image prompt
   - Add style parameters (cinematic, realistic, illustrated)
   - Add quality parameters (4K, detailed, sharp)
   - Add negative prompts (co NEchceme)
3. **Image generation:**
   - Call AI image API (Stable Diffusion, DALL-E)
   - Generate multiple variants (2-3 per scene)
   - Await generation completion
4. **Image selection:**
   - Quality assessment každého variantu
   - Select best image pro scénu
   - Optional: Human review pro kritické scény
5. **Image post-processing:**
   - Resize pro video resolution (1920x1080, 3840x2160)
   - Color correction/grading
   - Add brand watermark (optional)
   - Format conversion
6. **Storage:**
   - Save keyframes
   - Organize by scene
7. **Update Story:**
   - Uložení keyframe paths/URLs
   - State změna na "PrismQ.V.Video" (modul 28)

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** Keyframe images pro každou scénu
- **Formát výstupu:** High-resolution images (PNG, JPG)
- **Vedlejší efekty:** Image generation metrics, prompt library
- **Chování při chybě:** Regenerate nebo use stock images

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 26 - scene plan
- AI image generation API (Stable Diffusion, DALL-E, Midjourney)
- Image storage
- Databáze

**Výstupní závislosti:**
- Modul 28 (PrismQ.V.Video) - video assembly

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Image generation je expensive a slow
- Style consistency critical across scény
- Resolution must match target video quality
- Multiple variants umožňují selection
- Prompt engineering skills essential

**Rizika:**
- **Generation cost**: AI image generation expensive
- **Generation time**: Může trvat minutes per image
- **Quality variance**: Results mohou být unpredictable
- **Style inconsistency**: Images mohou vypadat differently
- **Inappropriate content**: AI může generate unwanted content
- **Copyright concerns**: Generated images copyright status

**Doporučení:**
- Build proven prompt library
- Style guides pro consistency
- Content moderation filters
- Human review sampling
- Cost optimization (lower quality pro previews)
- Fallback na stock images pokud generation fails
- Consider video stock footage jako alternative
