# API Reference MVP workflow

**Použití API, příklady a průvodce integrací**

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

