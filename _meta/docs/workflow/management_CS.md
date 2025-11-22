# Správa workflow

### Sledování pokroku

**Indikátory stavu**
- ⏳ Nezahájeno
- 🔄 Probíhá
- ⏸️ Blokováno/Čeká
- ✅ Dokončeno
- ⚠️ Problémy/Vyžaduje revizi
- 🗄️ Archivováno

**Sledování metadat**
```json
{
  "project_id": "PQ001",
  "current_state": "ScriptReview",
  "state_history": [
    {"state": "IdeaInspiration", "entered": "2025-01-01", "exited": "2025-01-02"},
    {"state": "Idea", "entered": "2025-01-02", "exited": "2025-01-03"},
    {"state": "ScriptDraft", "entered": "2025-01-03", "exited": "2025-01-05"},
    {"state": "ScriptReview", "entered": "2025-01-05", "exited": null}
  ],
  "revision_count": 2,
  "days_in_production": 5,
  "team_assigned": ["Autor A", "Editor B", "Recenzent C"]
}
```

### Kvalitní brány

Každý stav má definovaná kvalitní kritéria, která musí být splněna před postupem:

**Dokumentační brány**
- Všechna požadovaná pole vyplněna
- Metadata přesná a kompletní
- Verzovací kontrola aktualizována

**Revizní brány**
- Peer review dokončena
- Schválení zainteresovaných stran získáno
- Standardy kvality ověřeny

**Technické brány**
- Formáty souborů správné
- Technické specifikace splněny
- Žádné kritické chyby přítomny

### Příležitosti pro automatizaci

**Automatizované přechody**
- Nahrání souboru spouští změnu stavu
- Workflow schvalování spouští postup
- Naplánované úkoly (např. časování publikace)
- Sběr a reportování analytiky

**Manuální přechody**
- Kreativní rozhodnutí
- Hodnocení kvality
- Strategické pivoty
- Alokace zdrojů

## Osvědčené postupy

### Obecné principy

1. **Dokončete každý stav** - Nepřeskakujte kvalitní brány
2. **Dokumentujte vše** - Sledujte rozhodnutí a změny
3. **Iterujte když potřeba** - Používejte zpětné přechody pro vylepšení
4. **Archivujte rychle** - Nenechávejte mrtvé projekty viset
5. **Učte se neustále** - Vraťte poznatky zpět do vytváření nápadů

### Tipy specifické pro stavy

**Fáze nápadu**
- Investujte čas do osnovy a kostry
- Jasný titulek před přechodem na skript
- Validujte koncept se zainteresovanými stranami brzy

**Fáze skriptu**
- Více revizních průchodů předchází problémům downstream
- Uzamkněte schválené skripty pro prevenci rozšiřování rozsahu
- Udržujte historii revizí pro učení

**Produkční fáze**
- Kvalitní brány audia a videa jsou kritické
- Testujte na cílových platformách brzy
- Zabudujte čas na rezervu pro revize

**Fáze publikace**
- Plánujte časování strategicky
- Monitorujte časný výkon pozorně
- Aktivně zapojujte publikum

**Fáze analytiky**
- Sbírejte komplexní data
- Extrahujte použitelné poznatky
- Vraťte poznatky zpět do vytváření nápadů

## Metriky a monitorování

### Metriky efektivity workflow

**Časové metriky**
- Průměrný čas na stav
- Celkový čas produkce
- Identifikace úzkých hrdel
- Čas cyklu revizí

**Metriky kvality**
- Frekvence revizí na stav
- Míra úniku defektů
- Finální skóre kvality
- Spokojenost zainteresovaných stran

**Metriky zdrojů**
- Využití týmu
- Cena na stav
- Míra znovupoužití assetů
- Úspory z automatizace

### Nástěnky výkonu

Sledujte zdraví workflow pomocí klíčových indikátorů:
- Projekty podle stavu (distribuce)
- Průměrný čas v každém stavu
- Míra revizí/přepracování
- Míra dokončení
- Rozpad důvodů archivace

## Související dokumentace

- **[Dokumentace MVP Workflow](./MVP_WORKFLOW_DOCUMENTATION_CS.md)** - Kompletní 26fázové MVP workflow s příklady a API referencí
- **[Modul IdeaInspiration](./T/Idea/Inspiration/README.md)** - Inspirace a sběr
- **[Model Idea](./T/Idea/Model/README.md)** - Základní datový model
- **[Výzkum stavů workflow produkce obsahu](./_meta/research/content-production-workflow-states.md)** - Detailní výzkum
- **[Optimalizace metadat YouTube](../_meta/research/youtube-metadata-optimization-smart-strategy.md)** - Strategie platformy

