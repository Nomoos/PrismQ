# Kontrola běhu modulu: PrismQ.A.Narrator

**Účel:** Validace narratorského hlasu — hodnocení kvality, audience fit a konzistence napříč projekty.

---

## 📥 Vstup
- **Zdroj:** Audio storage + databáze
- **Data:** Voiceover audio z modulu 21, voice metadata, Story metadata (target audience)
- **Předpoklady:** Audio soubory z modulu 21, audio analysis tools, přístup k DB

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Voice quality analysis — clarity, naturalness, emotion appropriateness, pace, pronunciation accuracy
3. Audience fit validation — voice match pro target demographic, tone pro content type, accent
4. Consistency check — shoda s předchozími projekty, kvalita napříč segmenty
5. Selection decision — accept / request regeneration / flag pro human narrator
6. [Uložení výsledků](shared/databazova_integrace.md) — update Story: narrator validation, `state="PrismQ.A.Normalized"`

---

## 📤 Výstup
- **Primární:** Validated narrator choice s quality metriky
- **DB změny:** Tabulka `Story` — narrator metadata, validation results, `state="PrismQ.A.Normalized"`
- **Další krok:** Modul 23 (PrismQ.A.Normalized)
