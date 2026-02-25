# Dokumentace PrismQ Workflow

**Kompletní stavový automat pro tvorbu obsahu od inspirace po archivaci**

> 📚 **Toto je indexový dokument.** Dokumentace workflow byla organizována do zaměřených, modulárních souborů pro lepší údržbu a čitelnost.

## Report přechodů stavů

📊 **Nový report!** Pro komplexní přehled přechodů stavů pro každý modul viz:
- **[Report přechodů stavů (CS)](../STATE_TRANSITIONS_REPORT_CS.md)** - Kompletní dokumentace přechodů stavů pro všechny moduly (česky)
- **[State Transitions Report](../STATE_TRANSITIONS_REPORT.md)** - Complete state transitions report for all modules (English)

## Kompletní dokumentace

Veškerá dokumentace workflow je nyní organizována v adresáři [`docs/workflow/`](./):

### Základní workflow
- **[Stavový automat](./state-machine_CS.md)** - Kompletní diagram stavů a přehled
- **[Fáze workflow](./phases_CS.md)** - 9 hlavních fází tvorby obsahu
- **[Přechody stavů](./transitions_CS.md)** - Pravidla pro přechody mezi stavy
- **[Charakteristiky stavů](./states_CS.md)** - Různé typy stavů
- **[Strategie publikace](./publishing-strategy_CS.md)** - Postupný víceformátový přístup
- **[Správa workflow](./management_CS.md)** - Operace, kvalitní kontrolní body a osvědčené postupy
- **[Ultra-Clean Pipeline](./ultra-clean-pipeline_CS.md)** - Zjednodušená reprezentace běhu

### Implementace MVP (26fázová tvorba textu)
- **[Přehled MVP](./mvp-overview_CS.md)** - Principy a filosofie workflow
- **[Fáze MVP](./mvp-stages_CS.md)** - Všech 26 fází podrobně
- **[API Reference MVP](./mvp-api_CS.md)** - Použití API a příklady
- **[Osvědčené postupy MVP](./mvp-best-practices_CS.md)** - Osvědčené postupy a řešení problémů

## Rychlý start

1. **Pochopte celkový obraz**: Začněte se [Stavovým automatem](./state-machine_CS.md)
2. **Naučte se fáze**: Přečtěte si [Fáze workflow](./phases_CS.md)
3. **Implementace MVP**: Zkontrolujte [Přehled MVP](./mvp-overview_CS.md)
4. **Integrace**: Použijte [API Reference MVP](./mvp-api_CS.md)

## Navigace

Pro kompletní index a průvodce navigací viz [Index dokumentace workflow](./README.md).

## Související dokumentace

- [ARCHITECTURE.md](../ARCHITECTURE.md) - Celková architektura platformy
- [PROGRESSIVE_ENRICHMENT.md](../PROGRESSIVE_ENRICHMENT.md) - Strategie víceformátového obsahu
- [QUALITY_GATES.md](../QUALITY_GATES.md) - Rámec zajištění kvality

---

*Tato modulární organizace dodržuje principy SOLID se zaměřenými dokumenty s jednou odpovědností.*
