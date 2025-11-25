# Dokumentace PrismQ Workflow

**Kompletní stavový automat pro tvorbu obsahu od inspirace po archivaci**

> 📚 **Toto je indexový dokument.** Dokumentace workflow byla organizována do zaměřených, modulárních souborů pro lepší údržbu a čitelnost.

## Kompletní dokumentace

Veškerá dokumentace workflow je nyní organizována v adresáři [`docs/workflow/`](./docs/workflow/):

### Základní workflow
- **[Stavový automat](./docs/workflow/state-machine_CS.md)** - Kompletní diagram stavů a přehled
- **[Fáze workflow](./docs/workflow/phases_CS.md)** - 9 hlavních fází tvorby obsahu
- **[Přechody stavů](./docs/workflow/transitions_CS.md)** - Pravidla pro přechody mezi stavy
- **[Charakteristiky stavů](./docs/workflow/states_CS.md)** - Různé typy stavů
- **[Strategie publikace](./docs/workflow/publishing-strategy_CS.md)** - Postupný víceformátový přístup
- **[Správa workflow](./docs/workflow/management_CS.md)** - Operace, kvalitní kontrolní body a osvědčené postupy
- **[Ultra-Clean Pipeline](./docs/workflow/ultra-clean-pipeline_CS.md)** - Zjednodušená reprezentace běhu

### Implementace MVP (26fázová tvorba textu)
- **[Přehled MVP](./docs/workflow/mvp-overview_CS.md)** - Principy a filosofie workflow
- **[Fáze MVP](./docs/workflow/mvp-stages_CS.md)** - Všech 26 fází podrobně
- **[API Reference MVP](./docs/workflow/mvp-api_CS.md)** - Použití API a příklady
- **[Osvědčené postupy MVP](./docs/workflow/mvp-best-practices_CS.md)** - Osvědčené postupy a řešení problémů

## Rychlý start

1. **Pochopte celkový obraz**: Začněte se [Stavovým automatem](./docs/workflow/state-machine_CS.md)
2. **Naučte se fáze**: Přečtěte si [Fáze workflow](./docs/workflow/phases_CS.md)
3. **Implementace MVP**: Zkontrolujte [Přehled MVP](./docs/workflow/mvp-overview_CS.md)
4. **Integrace**: Použijte [API Reference MVP](./docs/workflow/mvp-api_CS.md)

## Navigace

Pro kompletní index a průvodce navigací viz [Index dokumentace workflow](./docs/workflow/README.md).

## Související dokumentace

- [ARCHITECTURE.md](./docs/ARCHITECTURE.md) - Celková architektura platformy
- [PROGRESSIVE_ENRICHMENT.md](./docs/PROGRESSIVE_ENRICHMENT.md) - Strategie víceformátového obsahu
- [QUALITY_GATES.md](./docs/QUALITY_GATES.md) - Rámec zajištění kvality

---

*Tato modulární organizace dodržuje principy SOLID se zaměřenými dokumenty s jednou odpovědností.*
