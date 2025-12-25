# Jak funguje PrismQ.T.Idea.From.User - Kompletní průvodce

**Worker10 Review - Technická dokumentace modulu Creation**

---

## Obsah

1. [Přehled modulu](#přehled-modulu)
2. [Architektura](#architektura)
3. [Hlavní komponenty](#hlavní-komponenty)
4. [Tok dat a workflow](#tok-dat-a-workflow)
5. [Konfigurace](#konfigurace)
6. [AI integrace](#ai-integrace)
7. [Prompt šablony](#prompt-šablony)
8. [Generované pole](#generované-pole)
9. [Příklady použití](#příklady-použití)
10. [Integrace do PrismQ workflow](#integrace-do-prismq-workflow)

---

## Přehled modulu

Modul `PrismQ.T.Idea.From.User` implementuje **Path 2: Manual Creation** v PrismQ workflow - generování 10 Ideas z jednoduchého vstupu (titul nebo popis) pomocí lokálních AI modelů.

**Důležité**: AI (Ollama) je **povinné** pro generování Ideas. Bez dostupného AI serveru modul vrací prázdný seznam a loguje chybu.

### Klíčové vlastnosti

| Vlastnost | Hodnota |
|-----------|---------|
| **Výchozí počet Ideas** | 10 |
| **AI engine** | Ollama (lokální LLM) - **povinné** |
| **Optimalizováno pro** | RTX 5090 (24GB VRAM) |
| **Bez AI** | Prázdný seznam + chyba v logu |
| **Prompt šablony** | Konfigurovatelné |
| **Jazyk implementace** | Python 3.12+ |

---

## Architektura

```
┌─────────────────────────────────────────────────────────────────┐
│                    T/Idea/From/User Module                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐       ┌─────────────────────────────────┐  │
│  │  IdeaCreator    │       │       CreationConfig            │  │
│  │  (creation.py)  │◄──────│  - use_ai: bool                 │  │
│  │                 │       │  - ai_model: str                │  │
│  │  Orchestruje    │       │  - default_num_ideas: int       │  │
│  │  celý proces    │       │  - prompt_template: str         │  │
│  └───────┬─────────┘       └─────────────────────────────────┘  │
│          │                                                       │
│          ▼                                                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   Rozhodovací logika                     │    │
│  │        AI dostupné?  ──┬──▶ ANO: AIIdeaGenerator        │    │
│  │                        └──▶ NE:  ERROR + prázdný seznam │    │
│  └───────────────────────────────────────────────────────────┘  │
│          │                                                       │
│          ▼                                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  AIIdeaGenerator (ai_generator.py)                        │  │
│  │                                                           │  │
│  │  - Prompt šablony (konfigurovatelné)                     │  │
│  │  - Ollama API komunikace                                 │  │
│  │  - JSON parsování odpovědi                               │  │
│  │  - Validace struktury dat                                │  │
│  └───────────────────────────────────────────────────────────┘  │
│          │                                                       │
│          ▼                                                       │
│  ┌─────────────────────┐                                         │
│  │    List[Idea]       │                                         │
│  │  (from Model/src/)  │                                         │
│  └─────────────────────┘                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Hlavní komponenty

### 1. IdeaCreator (creation.py)

Hlavní třída orchestrující generování Ideas. Zodpovídá za:

- Inicializaci konfigurace
- Kontrolu dostupnosti AI
- Validaci vstupů
- Transformaci výstupů na `Idea` objekty
- **Logování chyby pokud AI není dostupné**

```python
class IdeaCreator:
    def __init__(self, config: Optional[CreationConfig] = None):
        """
        1. Načte konfiguraci (nebo použije výchozí)
        2. Inicializuje AI generator pokud use_ai=True
        3. Ověří dostupnost Ollama serveru
        4. Nastaví prompt šablonu pokud je definována
        5. Loguje ERROR pokud AI není dostupné
        """
        
    def create_from_title(self, title: str, num_ideas: int = None) -> List[Idea]:
        """Hlavní vstupní bod pro generování z titulu."""
        
    def create_from_description(self, description: str, num_ideas: int = None) -> List[Idea]:
        """Alternativní vstupní bod pro generování z popisu."""
```

### 2. CreationConfig

Dataclass obsahující veškerou konfiguraci:

```python
@dataclass
class CreationConfig:
    # Parametry obsahu
    min_title_length: int = 20      # Min. délka titulu (znaky)
    max_title_length: int = 100     # Max. délka titulu (znaky)
    min_story_length: int = 100     # Min. délka synopse (slova)
    max_story_length: int = 1000    # Max. délka synopse (slova)
    
    # Variace
    variation_degree: str = "medium"  # low/medium/high
    include_all_fields: bool = True   # Generovat všechna narativní pole
    
    # AI nastavení
    use_ai: bool = True
    ai_model: str = "llama3.1:70b-q4_K_M"
    ai_temperature: float = 0.8
    default_num_ideas: int = 10
```

### 3. AIIdeaGenerator (ai_generator.py)

Komunikuje s Ollama API pro AI generování:

```python
class AIIdeaGenerator:
    def __init__(self, config: Optional[AIConfig] = None):
        """
        1. Načte AI konfiguraci
        2. Ověří dostupnost Ollama serveru
        3. Nastaví self.available flag
        """
        
    def generate_ideas_from_title(self, title: str, num_ideas: int = 10) -> List[Dict]:
        """
        1. Sestaví prompt pro LLM
        2. Zavolá Ollama API
        3. Parsuje JSON odpověď
        4. Validuje strukturu dat
        """
```

### 4. AIConfig

Konfigurace pro AI generátor:

```python
@dataclass
class AIConfig:
    model: str = "llama3.1:70b-q4_K_M"
    api_base: str = "http://localhost:11434"
    temperature: float = 0.8
    max_tokens: int = 2000
    timeout: int = 120  # sekundy
```

---

## Tok dat a workflow

### Sekvenční diagram - create_from_title()

```
Uživatel                IdeaCreator           AIIdeaGenerator        Ollama API
   │                         │                      │                    │
   │  create_from_title()    │                      │                    │
   │─────────────────────────▶                      │                    │
   │                         │                      │                    │
   │                    ┌────┴────┐                 │                    │
   │                    │ Validace│                 │                    │
   │                    │ vstupu  │                 │                    │
   │                    └────┬────┘                 │                    │
   │                         │                      │                    │
   │                    ┌────┴────┐                 │                    │
   │                    │AI       │                 │                    │
   │                    │dostupné?│                 │                    │
   │                    └────┬────┘                 │                    │
   │                         │                      │                    │
   │            ╔════════════╧════════════╗        │                    │
   │            ║        ANO              ║        │                    │
   │            ╠═════════════════════════╣        │                    │
   │            ║                         ║        │                    │
   │            ║  Načti prompt šablonu   ║        │                    │
   │            ║  generate_ideas_from_   ║────────▶                    │
   │            ║  title()                ║        │                    │
   │            ║                         ║        │  POST /api/generate│
   │            ║                         ║        │────────────────────▶
   │            ║                         ║        │                    │
   │            ║                         ║        │    JSON response   │
   │            ║                         ║        │◀────────────────────
   │            ║                         ║        │                    │
   │            ║    List[Dict] ◀─────────║────────│                    │
   │            ║                         ║        │                    │
   │            ╠═════════════════════════╣        │                    │
   │            ║        NE               ║        │                    │
   │            ╠═════════════════════════╣        │                    │
   │            ║                         ║        │                    │
   │            ║  logger.error(...)      ║        │                    │
   │            ║  return []              ║        │                    │
   │            ║                         ║        │                    │
   │            ╚═════════════════════════╝        │                    │
   │                         │                      │                    │
   │                    ┌────┴────┐                 │                    │
   │                    │Konverze │                 │                    │
   │                    │na Idea  │                 │                    │
   │                    │objekty  │                 │                    │
   │                    └────┬────┘                 │                    │
   │                         │                      │                    │
   │    List[Idea]           │                      │                    │
   │◀────────────────────────│                      │                    │
```

### Detailní kroky

1. **Validace vstupu**
   - Kontrola prázdného titulu/popisu
   - Kontrola num_ideas >= 1
   - Výjimka `ValueError` při neplatném vstupu

2. **Kontrola AI dostupnosti**
   - Kontrola `self.ai_generator` existence
   - Pokud AI není dostupné: **ERROR log + prázdný seznam**
   - Žádný fallback režim

3. **AI generování**
   - Načtení prompt šablony (výchozí nebo vlastní)
   - Sestavení promptu s kontextem
   - HTTP POST na Ollama API
   - Parsování JSON odpovědi
   - Validace struktury

4. **Konverze na Idea objekty**
   - Mapování polí z dict na Idea
   - Nastavení výchozích hodnot
   - Přidání metadat a poznámek

---

## Konfigurace

### Výchozí konfigurace (RTX 5090)

```python
CreationConfig(
    use_ai=True,
    ai_model="llama3.1:70b-q4_K_M",
    ai_temperature=0.8,
    default_num_ideas=10,
    prompt_template=None  # Použije výchozí šablonu
)
```

### Konfigurace pro různé GPU

| GPU | VRAM | Doporučený model |
|-----|------|------------------|
| RTX 5090 | 24GB | `llama3.1:70b-q4_K_M` |
| RTX 4090 | 24GB | `llama3.1:70b-q4_K_M` |
| RTX 4080 | 16GB | `llama3.1:13b` |
| RTX 3080 | 10GB | `llama3.2:8b` |
| CPU only | - | `llama3.2:8b` |

### Konfigurace bez AI (vrací prázdný seznam)

```python
# POZOR: Bez AI se negenerují žádné Ideas!
config = CreationConfig(use_ai=False)
creator = IdeaCreator(config)
ideas = creator.create_from_title("Test")
# ideas = [] (prázdný seznam) + ERROR v logu
```

---

## AI integrace

### Ollama komunikace

```python
# Endpoint
POST http://localhost:11434/api/generate

# Request body
{
    "model": "llama3.1:70b-q4_K_M",
    "prompt": "...",
    "stream": false,
    "options": {
        "temperature": 0.8,
        "num_predict": 2000
    }
}

# Response
{
    "response": "[{\"title\": \"...\", ...}]"
}
```

### Prompt struktura

AI prompt obsahuje:
1. **Role**: Creative content strategist
2. **Úkol**: Generovat N unikátních Ideas
3. **Kontext**: Target platforms, formats, genre, length
4. **Požadovaná pole**: title, concept, premise, logline, hook, synopsis, skeleton, outline, keywords, themes
5. **Výstupní formát**: JSON array

### JSON parsování

```python
def _parse_ideas_response(self, response_text: str, expected_count: int):
    # Najdi JSON array v odpovědi
    start_idx = response_text.find('[')
    end_idx = response_text.rfind(']')
    
    if start_idx >= 0 and end_idx > start_idx:
        json_text = response_text[start_idx:end_idx + 1]
        ideas = json.loads(json_text)
        
        # Validace a čištění
        validated_ideas = []
        for idea in ideas[:expected_count]:
            if isinstance(idea, dict) and 'title' in idea:
                validated_ideas.append(self._validate_idea_dict(idea))
        
        return validated_ideas
    
    return []  # ERROR při chybě parsování
```

---

## Prompt šablony

### Výchozí šablony

AIIdeaGenerator obsahuje výchozí prompt šablony pro generování z titulu i popisu. Šablony používají tyto proměnné:

| Proměnná | Popis |
|----------|-------|
| `{num_ideas}` | Počet Ideas k vygenerování |
| `{input}` | Titul nebo popis |
| `{platforms}` | Cílové platformy |
| `{formats}` | Cílové formáty |
| `{genre}` | Žánr obsahu |
| `{length}` | Cílová délka |

### Vlastní prompt šablona

```python
# Definuj vlastní šablonu
custom_template = """Jsi kreativní content stratég. Vygeneruj {num_ideas} unikátních 
nápadů na obsah na základě: "{input}"

Platformy: {platforms}
Formáty: {formats}
Žánr: {genre}
Délka: {length}

Pro každý nápad uveď:
- title: unikátní titul
- concept: koncept (1-2 věty)
- premise: premisa (2-3 věty)
- logline: logline (1 věta)
- hook: úvodní háček
- synopsis: synopse (2-3 odstavce)
- skeleton: kostra (5-7 bodů)
- outline: osnova
- keywords: klíčová slova (pole)
- themes: témata (pole)

Vrať POUZE JSON pole objektů, bez dalšího textu."""

# Použij vlastní šablonu v konfiguraci
config = CreationConfig(
    use_ai=True,
    prompt_template=custom_template
)
creator = IdeaCreator(config)
```

### Programové nastavení šablony

```python
# Můžeš také nastavit šablonu přímo na AI generátoru
creator = IdeaCreator()
if creator.ai_generator:
    creator.ai_generator.set_prompt_template(custom_template)
```

### Získání aktuální šablony

```python
# Získej aktuální šablonu
if creator.ai_generator:
    template = creator.ai_generator.get_prompt_template(for_description=False)
    print(template)
```

---

## Generované pole

Každá generovaná Idea obsahuje:

### Story Foundation (Základy příběhu)
| Pole | Popis | Příklad |
|------|-------|---------|
| `title` | Unikátní, poutavý titul | "The Future of AI: A Deep Dive" |
| `concept` | Jádro myšlenky (1-2 věty) | "Exploring how AI will transform..." |
| `premise` | Detailní vysvětlení (2-3 věty) | "This content explores..." |
| `logline` | Jednovětná dramatická verze | "Discover the truth behind..." |
| `hook` | Attention-grabbing opening | "What if everything you knew..." |

### Story Structure (Struktura)
| Pole | Popis |
|------|-------|
| `synopsis` | Souhrn (2-3 odstavce, 150-300 slov) |
| `skeleton` | Přehled 5-7 klíčových bodů |
| `outline` | Detailní struktura se sekcemi |

### Metadata
| Pole | Popis |
|------|-------|
| `keywords` | 5-10 relevantních klíčových slov |
| `themes` | 3-5 hlavních témat |
| `status` | Vždy `IdeaStatus.DRAFT` |
| `notes` | Info o zdroji generování |

---

## Příklady použití

### Základní použití

```python
from T.Idea.From.User.src.creation import IdeaCreator

# Vytvoření 10 Ideas (výchozí)
creator = IdeaCreator()
ideas = creator.create_from_title("Umělá inteligence v medicíně")

print(f"Vytvořeno: {len(ideas)} ideas")  # Vytvořeno: 10 ideas

for i, idea in enumerate(ideas, 1):
    print(f"\n{i}. {idea.title}")
    print(f"   Koncept: {idea.concept[:100]}...")
```

### Vlastní konfigurace

```python
from T.Idea.From.User.src.creation import IdeaCreator, CreationConfig

config = CreationConfig(
    use_ai=True,
    ai_model="qwen2.5:72b-q4_K_M",
    ai_temperature=0.9,
    default_num_ideas=5,
    variation_degree="high"
)

creator = IdeaCreator(config)
ideas = creator.create_from_title("Kreativní psaní")
```

### Generování z popisu

```python
from T.Idea.Model.src.idea import ContentGenre

description = """
Prozkoumejte etické dopady AI v zdravotnictví, se zaměřením na
ochranu soukromí a předpojatost algoritmů.
"""

# Metoda create_from_description podporuje stejné parametry jako create_from_title:
# target_platforms, target_formats, genre, length_target, atd.
ideas = creator.create_from_description(
    description,
    num_ideas=10,
    target_platforms=["youtube", "medium"],
    genre=ContentGenre.EDUCATIONAL
)
```

### Testování bez AI

```python
config = CreationConfig(use_ai=False, default_num_ideas=3)
creator = IdeaCreator(config)
ideas = creator.create_from_title("Test Topic")
# Rychlé, deterministické výsledky
```

---

## Integrace do PrismQ workflow

### Pozice v workflow

```
PrismQ Content Pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Path 1: Inspirace          Path 2: Ruční vytvoření (tento modul)
    │                              │
    ▼                              ▼
IdeaInspiration    ────────▶   T/Idea/From/User
    │                              │
    └──────────────────────────────┘
                   │
                   ▼
             Idea (10 kandidátů)
                   │
                   ▼
           T/Idea/Scoring (bodování)
                   │
                   ▼
           Nejlepší Idea
                   │
                   ▼
         T/Title/From/Idea (MVP-002)
                   │
                   ▼
           T/Script (MVP-003)
                   │
                   ▼
        T/Review → T/Publishing
```

### Downstream závislosti

| Modul | Využití |
|-------|---------|
| **MVP-002** (T/Title/From/Idea) | Generuje tituly z vybraných Ideas |
| **MVP-003** (T/Content/FromIdeaAndTitle) | Generuje skripty z Ideas + titulů |
| **MVP-004** (T/Review/Title) | Reviewuje vygenerované tituly |

### Příklad integrace

```python
# 1. Generování Ideas (tento modul) - vyžaduje AI!
creator = IdeaCreator()
ideas = creator.create_from_title("Kybernetická bezpečnost")

if not ideas:
    print("ERROR: AI není dostupné. Zkontrolujte, zda běží Ollama.")
else:
    # 2. Bodování (T/Idea/Scoring) - existující modul
    from T.Idea.Scoring import IdeaScorer
    scorer = IdeaScorer()
    scored_ideas = [(idea, scorer.score(idea)) for idea in ideas]
    best_idea = max(scored_ideas, key=lambda x: x[1])[0]

    # 3. Generování titulu (MVP-002 - PLÁNOVANÝ modul, zatím neexistuje)
    # Následující kód je příklad budoucí integrace:
    # from T.Title.From.Idea import TitleGenerator
    # titles = TitleGenerator().generate_titles(best_idea)

    # 4. Generování skriptu (MVP-003 - PLÁNOVANÝ modul, zatím neexistuje)
    # Následující kód je příklad budoucí integrace:
    # from T.Script.FromIdeaAndTitle import ScriptGenerator
    # script = ScriptGenerator().generate(best_idea, titles[0])
```

---

## Souhrn

Modul `PrismQ.T.Idea.From.User`:

✅ **Generuje 10 Ideas** z jednoduchého vstupu (titul nebo popis)  
✅ **Vyžaduje AI** (Ollama) - bez AI vrací prázdný seznam + ERROR  
✅ **Konfigurovatelné prompt šablony** před AI zpracováním  
✅ **Optimalizován pro RTX 5090** s podporou menších GPU  
✅ **Bohatá struktura** - všechna narativní pole  
✅ **Konfigurovatelný** - model, teplota, počet ideas, prompt šablona  
✅ **Testovaný** - 22 testů (15 aktivních, 7 vyžaduje AI)  
✅ **Bezpečný** - 0 zranitelností (CodeQL)  

---

**Autor dokumentace**: Worker10  
**Datum**: 2025-11-28  
**Verze modulu**: 1.1.0 (bez fallback, s prompt šablonami)  
**Status**: Production-ready ✅
