# Fáze MVP workflow

**Kompletní implementace 26fázového workflow**

## Kompletní fáze workflow

### Sekvence workflow (26 fází)

```
Fáze 1: PrismQ.T.Idea.From.User
    ↓
Fáze 2: PrismQ.T.Title.From.Idea (v1)
    ↓
Fáze 3: PrismQ.T.Content.FromIdeaAndTitle (v1)
    ↓
Fáze 4: PrismQ.T.Review.Title.ByScript (v1)
    ↓
Fáze 5: PrismQ.T.Review.Script.ByTitle (v1)
    ↓
Fáze 6: PrismQ.T.Title.From.Title.Review.Script (v2)
    ↓
Fáze 7: PrismQ.T.Content.Improvements (v2)
    ↓
Fáze 8: PrismQ.T.Review.Title.ByScript (v2) ←──────────────┐
    ↓                                                       │
Fáze 9: PrismQ.T.Title.Refinement (v3)                     │
    ↓                                                       │
Fáze 10: PrismQ.T.Review.Script.ByTitle (v2) ←──────────┐  │
    ↓                                                    │  │
Fáze 11: PrismQ.T.Content.Refinement (v3)                │  │
    ↓                                                    │  │
Fáze 12: Kontrola přijetí titulku ─NE───────────────────┘  │
    ↓ ANO                                                   │
Fáze 13: Kontrola přijetí skriptu ─NE──────────────────────┘
    ↓ ANO

━━━━ Lokální AI recenze (Fáze 14-20) ━━━━

Fáze 14: PrismQ.T.Review.Script.Grammar ←──────────┐
    ↓                                              │
    ├─NEPROŠLO─→ Návrat do Script.Refinement ─────┘
    ↓ PROŠLO
Fáze 15: PrismQ.T.Review.Script.Tone ←────────────┐
    ↓                                             │
    ├─NEPROŠLO─→ Návrat do Script.Refinement ────┘
    ↓ PROŠLO
Fáze 16: PrismQ.T.Review.Script.Content ←─────────┐
    ↓                                             │
    ├─NEPROŠLO─→ Návrat do Script.Refinement ────┘
    ↓ PROŠLO
Fáze 17: PrismQ.T.Review.Script.Consistency ←─────┐
    ↓                                             │
    ├─NEPROŠLO─→ Návrat do Script.Refinement ────┘
    ↓ PROŠLO
Fáze 18: PrismQ.T.Review.Script.Editing ←─────────┐
    ↓                                             │
    ├─NEPROŠLO─→ Návrat do Script.Refinement ────┘
    ↓ PROŠLO
Fáze 19: PrismQ.T.Review.Title.Readability ←──────┐
    ↓                                             │
    ├─NEPROŠLO─→ Návrat do Title.Refinement ─────┘
    ↓ PROŠLO
Fáze 20: PrismQ.T.Review.Script.Readability ←─────┐
    ↓                                             │
    ├─NEPROŠLO─→ Návrat do Script.Refinement ────┘
    ↓ PROŠLO

━━━━ GPT Expertní recenze smyčka (Fáze 21-22) ━━━━

Fáze 21: PrismQ.T.Story.ExpertReview (GPT) ←──────────┐
    ↓                                                  │
    ├─ Potřeba vylepšení ─→ Fáze 22 ──────────────────┘
    ↓ Připraveno k publikaci
Fáze 23: PrismQ.T.Publishing.Finalization
```

---

## Detaily fází

Tato sekce poskytuje komplexní dokumentaci pro všech 26 fází MVP workflow. Každá fáze obsahuje účel, vstupy, výstupy, API příklady a příklady použití.

### Fáze 1-11: Počáteční vytvoření a vylepšení

Tyto fáze řeší počáteční vytváření obsahu, křížové recenze a iterativní cykly vylepšování.

---

### Fáze 1: PrismQ.T.Idea.From.User

**Účel**: Zachytit počáteční nápad na obsah

**Složka**: `T/Idea/From/User/`  
**Pracovník**: Worker02  
**Úsilí**: 2 dny

**Vstup**:
- Textový popis nápadu
- Volitelné: zdroje inspirace, cílové publikum

**Výstup**:
- Objekt nápadu s unikátním ID
- Metadata (časové razítko, autor, tagy)
- Počáteční klasifikace

**Validace**:
- Není prázdný
- Základní kontrola formátu
- Obsahuje minimální požadovaná pole

**API**:
```python
from PrismQ.T.Idea.From.User import create_idea

idea = create_idea(
    description="Příběh o záhadných událostech v malém městě",
    target_audience="US ženy 14-29",
    genre="mysteriózní/napětí"
)
# Vrací: Objekt nápadu s ID
```

**Příklad použití**:
```python
# Vytvoření nového nápadu
idea = {
    "id": "PQ001",
    "description": "Napínavý příběh o nevysvětlitelných zmizení",
    "target_audience": "Mladí dospělí",
    "genre": "Mysteriózní",
    "platforms": ["YouTube", "TikTok"],
    "created_at": "2025-01-01T10:00:00Z"
}
```

**Další fáze**: Fáze 2 (Title.From.Idea)

---

### Fáze 2-23: Další fáze workflow

Pro úplnost jsou zde shrnuty všechny zbývající fáze workflow. Každá fáze má svůj specifický účel a přispívá k celkovému procesu vytváření kvalitn obsahu.

**Fáze 2**: Generování titulku v1 z nápadu  
**Fáze 3**: Generování skriptu v1 z nápadu a titulku  
**Fáze 4-5**: Křížové recenze titulku a skriptu  
**Fáze 6-7**: První vylepšení (v2)  
**Fáze 8-11**: Cyklus vylepšení (v3)  
**Fáze 12-13**: Brány přijetí  
**Fáze 14-20**: Kvalitní recenze (Gramatika, Tón, Obsah, Konzistence, Editace, Čitelnost)  
**Fáze 21-22**: GPT expertní recenze a leštění  
**Fáze 23**: Finalizace publikace

Podrobný popis každé fáze včetně API příkladů, vstupů a výstupů je k dispozici v anglické verzi tohoto dokumentu: [MVP_WORKFLOW_DOCUMENTATION.md](./MVP_WORKFLOW_DOCUMENTATION.md), nebo v původním specifikačním dokumentu [MVP_WORKFLOW.md](./_meta/issues/MVP_WORKFLOW.md).

---

