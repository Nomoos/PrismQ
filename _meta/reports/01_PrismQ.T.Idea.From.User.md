# Kontrola běhu modulu: PrismQ.T.Idea.From.User

## 🎯 Účel modulu
Vytváření nápadů (Idea objektů) z textového vstupu pomocí AI. Modul slouží jako vstupní bod celého workflow PrismQ - transformuje inspiraci uživatele na strukturované nápady s různými variantami, které lze dále zpracovávat v pipeline.

**Klíčové**: Vstupní text je předán přímo do AI promptu bez jakéhokoliv parsování, extrakce, validace nebo čištění.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Uživatel (interaktivní terminálový vstup nebo API volání)
- **Typ dat:** Text (libovolný formát - plain text, JSON, víceřádkový text)
- **Povinné hodnoty:**
  - `input_text` - Textový vstup od uživatele (předán do AI bez úprav)
- **Nepovinné hodnoty:**
  - `--preview` flag - režim bez uložení do databáze
  - `--debug` flag - detailní logování
  - `count` - počet variant k vygenerování (výchozí: 10)
  - `flavor_name` - specifický flavor (jinak weighted random selection)
- **Očekávané předpoklady:**
  - Běžící Ollama server (localhost:11434)
  - Dostupný AI model (qwen3:32b nebo jiný)
  - Aktivní Python virtual environment
  - Přístup k databázi (v production režimu)

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Inicializace prostředí:**
   - Kontrola Python instalace
   - Vytvoření/aktivace virtual environment
   - Instalace dependencies (pytest, requests)
   - Spuštění Ollama serveru

2. **Načtení vstupů:**
   - Zobrazení uvítací obrazovky
   - Čtení vstupu od uživatele
   - **Text je předán do AI šablony přesně tak, jak byl zadán** (žádné parsování, extrakce, validace ani čištění)

3. **Výběr flavor variant:**
   - FlavorSelector vybere flavory pomocí weighted random selection
   - Výchozí počet: 10 flavors (stylů obsahu)
   - Flavory definují: typ obsahu, tón, zaměření, cílové publikum
   - 20% šance na dual-flavor kombinaci pro bohatší tematiku

4. **Generování variant pomocí AI:**
   - Pro každý vybraný flavor (výchozí: 10x iterace):
     - Načtení flavor definice z konfigurace
     - Sestavení AI promptu: `input_text` + flavor + variation index
     - Odeslání requestu na Ollama API
     - AI generuje odpověď pomocí `idea_improvement.txt` prompt template
     - Odpověď obsahuje 5-sentence paragraph jako kompletní refined idea
     - Uložení do `hook` field (ostatní fields zůstávají prázdné)
     - Vytvoření Idea objektu s metadaty:
       - variant_name (flavor nebo dual-flavor kombinace)
       - source_input (původní vstupní text)
       - flavor_name, flavor_description
       - generated_at, idea_hash
       - keywords (z flavor definice)

5. **Zobrazení výsledků:**
   - Formátování každé varianty do čitelného textu
   - Barevný výstup na terminál (ANSI colors)
   - Logování do souboru (v debug režimu)

6. **Ukládání do databáze (pouze production režim):**
   - Získání cesty k databázi (z Config nebo fallback)
   - Setup databáze pomocí setup_idea_database()
   - Pro každou variantu:
     - Převod na text pomocí format_idea_as_text()
     - Vložení do tabulky Idea (text, version=1, created_at)
     - Získání idea_id (auto-increment)
   - Zobrazení potvrzení s ID

7. **Loop pro další iterace:**
   - Návrat na začátek pro další vstup
   - Možnost ukončení příkazem "quit"

8. **Ošetření chybových stavů:**
   - Import errors - graceful degradation, zobrazení chybové zprávy
   - Ollama nedostupný - RuntimeError s instrukcemi (AI je povinné)
   - Databázové chyby - logování, zobrazení chyby uživateli
   - Ctrl+C handling - čisté ukončení aplikace
   - AI generování selhalo - skip varianty, pokračování s dalšími

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:**
  - 10 vygenerovaných Idea objektů (variant nápadů, výchozí počet)
  - Každý obsahuje kompletní 5-sentence refined idea v `hook` field
  - Ostatní fields jsou prázdné (žádné parsování výstupu)
  
- **Formát výstupu:**
  - Konzolový výstup: Barevně formátovaný text
  - Databáze (production): 10 nových záznamů v tabulce `Idea`
  - Log soubor (debug): Detailní log všech operací
  
- **Vedlejší efekty:**
  - Vytvoření virtual environment (.venv)
  - Instalace Python packages
  - Spuštění Ollama serveru (pokud nebyl spuštěn)
  - Vytvoření databázového souboru (pokud neexistuje)
  - Log soubory v debug režimu
  
- **Chování při chybě:**
  - Import error: Zobrazení chybové zprávy, ukončení
  - Ollama chyba: RuntimeError s návodem na instalaci/spuštění (AI je povinné)
  - Databázová chyba: Logování, zobrazení chyby, možnost pokračovat v preview režimu
  - AI generování selhalo: Skip problematické varianty, pokračování s ostatními

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Ollama server (AI model hosting) - **POVINNÉ**
- AI model (qwen3:32b výchozí, konfigurovatelný)
- SQLite databáze (persistence v production režimu)
- Python 3.12+
- Hlavní moduly:
  - `T/Idea/From/User/src/idea_variants.py` - IdeaGenerator, FlavorSelector
  - `T/Idea/From/User/src/ai_generator.py` - AIIdeaGenerator
  - `T/Idea/From/User/src/flavor_loader.py` - FlavorLoader
  - `T/Idea/From/User/src/flavors.py` - Flavor utility functions
  - `T/Idea/From/User/src/idea_creation_interactive.py` - Interaktivní CLI
  - `T/Idea/Model/src/simple_idea_db.py` - Databázové operace
  - `src/config.py` - Konfigurace

**Výstupní závislosti:**
- Modul 02 (PrismQ.T.Story.From.Idea) - čte vytvořené Ideas z databáze
- Tabulka `Idea` v databázi - source of truth pro další moduly

**Dokumentace:**
- README.md - Navigace a quick start
- _meta/docs/AI_INTEGRATION_README.md - Detailní AI setup
- _meta/docs/HOW_IT_WORKS.md - Technická dokumentace (CZ)
- _meta/docs/FLAVOR_SYSTEM.md - Flavor systém
- _meta/docs/CUSTOM_PROMPTS.md - Prompt templating

---

## 📝 Poznámky / Rizika

**Klíčové změny v aktuální verzi:**
- **Vstupní text bez parsování**: Text jde přímo do AI promptu
- **Žádné legacy parametry**: Pouze `input_text` (ne title/description)
- **AI je povinné**: Žádný fallback mode - RuntimeError pokud Ollama není dostupný
- **Single paragraph output**: Vše v `hook` field, ostatní fields prázdné
- **Dual-flavor support**: 20% šance na kombinaci dvou flavors
- **SOLID architektura**: Externalised configuration, service-oriented design

**Poznámky:**
- Modul podporuje batch processing přes `T/Idea/Batch/src/`
- Preview režim je klíčový pro testování bez ovlivnění databáze
- Flavors jsou weighted - některé se objevují častěji (optimalizace pro cílové publikum)
- AI model může být změněn v konfiguraci (AIConfig)
- README.md je nyní pouze navigace - detaily v _meta/docs/

**Rizika:**
- **AI nedostupnost**: Pokud Ollama server není spuštěn nebo model není nainstalován, modul vyhodí RuntimeError (žádný fallback)
- **Kvalita AI výstupu**: AI může generovat nekvalitní data - částečně ošetřeno minimální délkou (20 znaků)
- **Databázová korrupce**: Současný zápis více instancí může způsobit problémy (SQLite je single-writer)
- **Memory consumption**: Generování 10 variant může být náročné na paměť při velkých modelech
- **API rate limiting**: Ollama může být zahlcen při batch processing
- **Dlouhé čekací doby**: Generování 10 variant může trvat několik minut (30B parameter model)

**Doporučení:**
- Monitorovat dostupnost Ollama serveru před spuštěním
- Používat preview režim pro testování nových funkcí
- Pravidelně zálohovat databázi
- Zvážit implementaci retry mechanismu pro AI volání
- Implementovat progress bar pro lepší UX
- Číst aktuální dokumentaci v _meta/docs/ pro detaily
