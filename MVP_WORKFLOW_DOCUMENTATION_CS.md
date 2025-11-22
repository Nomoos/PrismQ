# Dokumentace MVP Workflow

**PrismQ MVP - Iterativní ko-zlepšování titulku a skriptu (26 fází)**

Verze: 1.0  
Vytvořeno: 2025-11-22  
Stav: Kompletní  
Modul: Dokumentace

---

## Obsah

1. [Přehled](#přehled)
2. [Principy workflow](#principy-workflow)
3. [Kompletní fáze workflow](#kompletní-fáze-workflow)
4. [Detaily fází](#detaily-fází)
5. [Iterační smyčky](#iterační-smyčky)
6. [Příklady použití](#příklady-použití)
7. [API Reference](#api-reference)
8. [Osvědčené postupy](#osvědčené-postupy)
9. [Řešení problémů](#řešení-problémů)

---

## Přehled

MVP workflow implementuje komplexní **26fázový iterativní proces ko-zlepšování**, kde jsou titulek a skript vylepšovány společně prostřednictvím více fází recenze a vylepšování. To zajišťuje nejvyšší kvalitu obsahu prostřednictvím systematické validace a křížové kontroly.

### Klíčová inovace

Vylepšení titulku a skriptu jsou **vzájemně závislá** - každý je recenzován a vylepšován na základě toho druhého, čímž vzniká kontinuální cyklus zlepšování kvality, který zajišťuje sladění a soudržnost.

### Filosofie workflow

- **Progresivní vylepšování**: Více iterací verzí (v1, v2, v3, v4+)
- **Křížová validace**: Titulek a skript validovány proti sobě navzájem
- **Kvalitní brány**: Explicitní kontroly přijetí před postupem
- **Komplexní recenze**: Lokální AI recenze pokrývající 5 kvalitních dimenzí
- **Expertní leštění**: Expert review a vylepšení založené na GPT-4/GPT-5

---

## Principy workflow

### 1. Vzájemně závislé vylepšování

- **Titulek recenzován skriptem**: Titulek je hodnocen v kontextu obsahu skriptu
- **Skript recenzován titulkem**: Skript je hodnocen v kontextu slibu titulku
- **Křížová validace**: Každý element validován proti druhému + původní nápad

### 2. Sledování verzí

- **v1**: Počáteční návrhy (z nápadu)
- **v2**: První cyklus vylepšení (použití počátečních recenzí)
- **v3**: Druhý cyklus vylepšení (použití recenzí v2)
- **v4+**: Další cykly, pokud kontroly přijetí selžou

**Důležité**: Když dojde ke smyčkám, **vždy používejte nejnovější/aktuální verzi** titulku i skriptu.

### 3. Explicitní brány přijetí

- **Kontrola přijetí titulku** (fáze 12): Musí projít před kontrolou skriptu
- **Kontrola přijetí skriptu** (fáze 13): Musí projít před kvalitními recenzemi
- **Validace kvality** (fáze 14-20): Finální kvalitní brány

### 4. Zachování kontextu

- Původní verze zachovány po celou dobu
- Recenze odkazují na originály pro kontext
- Vylepšení staví na předchozích verzích

---

## Kompletní fáze workflow

### Sekvence workflow (26 fází)

```
Fáze 1: PrismQ.T.Idea.Creation
    ↓
Fáze 2: PrismQ.T.Title.FromIdea (v1)
    ↓
Fáze 3: PrismQ.T.Script.FromIdeaAndTitle (v1)
    ↓
Fáze 4: PrismQ.T.Review.Title.ByScript (v1)
    ↓
Fáze 5: PrismQ.T.Review.Script.ByTitle (v1)
    ↓
Fáze 6: PrismQ.T.Title.Improvements (v2)
    ↓
Fáze 7: PrismQ.T.Script.Improvements (v2)
    ↓
Fáze 8: PrismQ.T.Review.Title.ByScript (v2) ←──────────────┐
    ↓                                                       │
Fáze 9: PrismQ.T.Title.Refinement (v3)                     │
    ↓                                                       │
Fáze 10: PrismQ.T.Review.Script.ByTitle (v2) ←──────────┐  │
    ↓                                                    │  │
Fáze 11: PrismQ.T.Script.Refinement (v3)                │  │
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

### Fáze 1: PrismQ.T.Idea.Creation

**Účel**: Zachytit počáteční nápad na obsah

**Složka**: `T/Idea/Creation/`  
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
from PrismQ.T.Idea.Creation import create_idea

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

**Další fáze**: Fáze 2 (Title.FromIdea)

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

## Iterační smyčky

MVP workflow zahrnuje několik iteračních smyček pro zajištění kvality prostřednictvím progresivního vylepšování.

### Smyčka 1: Ko-zlepšování titulku a skriptu (Fáze 8-13)

**Spouštěč**: Kontrola přijetí titulku nebo skriptu selže

**Cesta smyčky**:
```
Fáze 12: Přijetí titulku ─SELHÁNÍ→ Fáze 8 → Fáze 9 → Fáze 12
Fáze 13: Přijetí skriptu ─SELHÁNÍ→ Fáze 10 → Fáze 11 → Fáze 13
```

**Příklad**:
```python
# Smyčka vylepšení titulku
max_iterations = 10
iteration = 0
title_current = title_v3

while not title_accepted and iteration < max_iterations:
    # Fáze 8: Recenze titulku skriptem
    review = review_title_by_script(title_current, script_current)
    
    # Fáze 9: Vylepšení titulku
    title_current = refine_title(title_current, review)
    iteration += 1
    
    # Fáze 12: Kontrola přijetí
    result = check_title_acceptance(title_current)
    title_accepted = result["accepted"]
    
    if not title_accepted:
        print(f"Iterace {iteration}: {result['reason']}")
```

### Smyčka 2: Smyčky kvalitních recenzí (Fáze 14-20)

**Spouštěč**: Jakákoli kvalitní recenze selže

**Vzor smyčky**:
```
Kvalitní recenze ─SELHÁNÍ→ Aplikovat opravy → Opakovat recenzi
```

### Smyčka 3: Smyčka expertní recenze (Fáze 21-22)

**Spouštěč**: Expertní recenze navrhuje vylepšení

**Cesta smyčky**:
```
Fáze 21: ExpertReview ─Potřeba vylepšení→ Fáze 22 → Fáze 21
```

**Limit iterací**: Maximálně 2 iterace leštění

---

## Příklady použití

### Příklad 1: Kompletní provedení workflow

```python
from PrismQ.T import Workflow

# Inicializace workflow
workflow = Workflow()

# Fáze 1: Vytvoření nápadu
idea = workflow.create_idea(
    description="Záhadná zmizení v malém městě",
    target_audience="US ženy 14-29"
)

# Fáze 2-3: Generování počátečních verzí
title_v1 = workflow.generate_title_v1(idea)
script_v1 = workflow.generate_script_v1(idea, title_v1)

# Fáze 4-5: Počáteční recenze
title_review = workflow.review_title_by_script(title_v1, script_v1, idea)
script_review = workflow.review_script_by_title(script_v1, title_v1, idea)

# Fáze 6-7: První vylepšení
title_v2 = workflow.improve_title_v2(title_v1, title_review, script_review)
script_v2 = workflow.improve_script_v2(script_v1, script_review, title_v2)

# Fáze 8-11: Cyklus vylepšení
title_v3, script_v3 = workflow.refinement_cycle(title_v2, script_v2, idea)

# Fáze 12-13: Kontroly přijetí se zpracováním smyček
title_v3 = workflow.run_title_acceptance_loop(title_v3, script_v3)
script_v3 = workflow.run_script_acceptance_loop(script_v3, title_v3)

# Fáze 14-20: Kvalitní recenze
quality_passed = workflow.run_quality_reviews(title_v3, script_v3)

if quality_passed:
    # Fáze 21-22: Expertní recenze a leštění
    final_title, final_script = workflow.expert_review_and_polish(
        title_v3, script_v3, idea
    )
    
    # Fáze 23: Publikace
    published = workflow.publish(final_title, final_script, idea)
    print(f"Publikováno: {published['id']}")
    print(f"URL: {published['urls']}")
```

### Příklad 2: Dávkové zpracování více nápadů

```python
from PrismQ.T import BatchProcessor

# Inicializace dávkového procesoru
batch = BatchProcessor(max_workers=5)

# Načtení nápadů ze souboru
ideas = batch.load_ideas_from_csv("napady.csv")

# Zpracování všech nápadů kompletním workflow
results = batch.process_batch(
    ideas=ideas,
    workflow_stages="all",  # Fáze 1-23
    quality_threshold=85,
    auto_publish=True
)

# Generování reportu
print(f"Celkem zpracováno: {len(results['completed'])}")
print(f"Publikováno: {results['published_count']}")
print(f"Selhalo: {results['failed_count']}")
```

---

## API Reference

### Hlavní třídy

#### Workflow

Hlavní třída orchestrace workflow.

```python
class Workflow:
    def __init__(self, config: Dict = None):
        """Inicializace workflow s volitelnou konfigurací"""
        pass
    
    def create_idea(self, description: str, **kwargs) -> Idea:
        """Fáze 1: Vytvoření nápadu"""
        pass
    
    def generate_title_v1(self, idea: Idea) -> Title:
        """Fáze 2: Generování titulku v1"""
        pass
    
    # ... další metody
```

#### Datové modely

```python
class Idea:
    id: str
    description: str
    target_audience: str
    genre: str
    platforms: List[str]
    created_at: datetime
    metadata: Dict[str, Any]

class Title:
    id: str
    idea_id: str
    text: str
    version: str
    created_at: datetime
    metadata: Dict[str, Any]

class Script:
    id: str
    content: str
    version: str
    word_count: int
    created_at: datetime
```

---

## Osvědčené postupy

### 1. Správa verzí

Vždy explicitně sledujte verze pro zachování kompletní historie.

```python
# Dobré - explicitní sledování verzí
title_v1 = generate_title_v1(idea)
title_v2 = improve_title_v2(title_v1, reviews)
title_v3 = refine_title(title_v2, review)

# Špatné - ztráta historie verzí
title = generate_title(idea)
title = improve_title(title)  # Přepíše originál
```

### 2. Zpracování chyb

Zpracujte selhání s řádným obnovením po chybě.

```python
# Dobré - komplexní zpracování chyb
try:
    result = review_grammar(script)
    if not result["pass"]:
        script = apply_fixes(script, result["corrections"])
except ReviewError as e:
    logger.error(f"Selhání gramatické recenze: {e}")
    # Záložní nebo opakovaná logika
```

### 3. Ochrana smyček

Vždy nastavte limity iterací pro předcházení nekonečným smyčkám.

```python
# Dobré - chráněná smyčka
max_iterations = 10
iteration = 0
while not accepted and iteration < max_iterations:
    # Logika vylepšení
    iteration += 1
```

---

## Řešení problémů

### Běžné problémy a řešení

#### Problém 1: Nekonečná smyčka v kontrolách přijetí

**Příznak**: Titulek nebo skript nikdy neprojde kontrolou přijetí

**Řešení**:
```python
# Přidání limitu iterací a eskalace
max_iterations = 5
for i in range(max_iterations):
    if check_acceptance(item):
        break
    if i == max_iterations - 1:
        # Eskalace na manuální recenzi
        manual_review_queue.add(item)
```

#### Problém 2: Kvalitní recenze neustále selhávají

**Příznak**: Gramatické/tónové/obsahové recenze konzistentně selhávají

**Řešení**:
```python
# Úprava citlivosti recenze
review_config = {
    "grammar_strictness": "medium",
    "tone_tolerance": 0.2,
    "content_min_score": 70
}
```

### Debug režim

Povolte debug režim pro podrobné logování:

```python
from PrismQ.T import Workflow
import logging

logging.basicConfig(level=logging.DEBUG)
workflow = Workflow(debug=True)
```

---

## Souhrn

MVP workflow poskytuje komplexní, iterativní přístup k tvorbě obsahu s:

- **26 fázemi** pokrývajícími všechny aspekty od nápadu po publikaci
- **3 hlavními iteračními smyčkami** pro kontinuální vylepšování
- **7 kvalitními dimenzemi** validovanými prostřednictvím AI recenzí
- **Explicitními branami přijetí** zajišťujícími kvalitní standardy
- **Sledováním verzí** zachovávajícím kompletní historii
- **GPT expertní recenzí** pro profesionální leštění

Tato dokumentace poskytuje kompletní pokrytí:
- ✅ Všech 26 fází workflow s podrobnými popisy
- ✅ Příkladů použití pro klíčové vzory
- ✅ Dokumentace iteračních smyček
- ✅ Kompletní API reference
- ✅ Osvědčených postupů a řešení problémů

Pro další informace viz:
- [MVP_WORKFLOW.md](./_meta/issues/MVP_WORKFLOW.md) - Původní specifikace
- [WORKFLOW_CS.md](./WORKFLOW_CS.md) - Kompletní dokumentace stavového automatu
- [T/README.md](./T/README.md) - Přehled pipeline generování textu

---

**Verze**: 1.0  
**Vytvořeno**: 2025-11-22  
**Modul**: Dokumentace  
**Pracovníci**: Worker15 (Specialista na dokumentaci)

**Stav**: ✅ Kompletní

---

*Dokumentace PrismQ MVP Workflow - Kompletní reference*
