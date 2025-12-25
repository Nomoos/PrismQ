# Kontrola běhu modulu: PrismQ.T.Idea.From.User

## 🎯 Účel modulu
Vytváření nápadů (Idea objektů) z textového vstupu pomocí AI. Modul slouží jako vstupní bod celého workflow PrismQ - transformuje inspiraci uživatele na strukturované nápady s různými variantami, které lze dále zpracovávat v pipeline.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Uživatel (interaktivní terminálový vstup)
- **Typ dat:** Text (multi-line input)
- **Povinné hodnoty:**
  - Textový vstup od uživatele (může být libovolný obsah - inspirace, téma, koncept)
- **Nepovinné hodnoty:**
  - `--preview` flag - režim bez uložení do databáze
  - `--debug` flag - detailní logování
- **Očekávané předpoklady:**
  - Běžící Ollama server (localhost:11434)
  - Dostupný AI model (qwen3:32b)
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

2. **Načtení a validace vstupů:**
   - Zobrazení uvítací obrazovky
   - Čtení multi-line vstupu od uživatele
   - Parsování textu (extrakce title, description, metadata)
   - Validace a čištění vstupního textu

3. **Výběr flavor variant:**
   - FlavorSelector vybere 10 flavors (stylů obsahu)
   - Weighted random selection (některé flavory mají vyšší pravděpodobnost)
   - Flavory definují: typ obsahu, tón, zaměření, cílové publikum

4. **Generování variant pomocí AI:**
   - Pro každý vybraný flavor (10x iterace):
     - Načtení flavor definice (prompt template)
     - Sestavení AI promptu (user input + flavor template + variation index)
     - Odeslání requestu na Ollama API
     - AI generuje odpověď (qwen3:32b model)
     - Parsování odpovědi do struktury Idea objektu
     - Validace kvality výstupu
     - Vytvoření Idea objektu s fieldy:
       - variant_name, title, description
       - target_audience, content_type, tone
       - key_points (list), inspiration_source
       - flavor, metadata

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
   - Ollama nedostupný - chybová zpráva s instrukcemi
   - Databázové chyby - logování, zobrazení chyby uživateli
   - Ctrl+C handling - čisté ukončení aplikace
   - AI generování selhalo - skip varianty, pokračování s dalšími

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:**
  - 10 vygenerovaných Idea objektů (variant nápadů)
  - Každý s unikátním názvem, titulkem, popisem a metadaty
  
- **Formát výstupu:**
  - Konzolový výstup: Barevně formátovaný text s ASCII art
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
  - Ollama chyba: Chybová zpráva s návodem na spuštění
  - Databázová chyba: Logování, zobrazení chyby, možnost pokračovat v preview režimu
  - AI generování selhalo: Skip problematické varianty, pokračování s ostatními

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Ollama server (AI model hosting)
- qwen3:32b model (AI model pro generování)
- SQLite databáze (persistence)
- Python 3.x + virtual environment
- Moduly:
  - `T/Idea/From/User/src/idea_variants.py` - Generování variant
  - `T/Idea/From/User/src/ai_generator.py` - AI generátor
  - `T/Idea/From/User/src/flavor_loader.py` - Načítání flavors
  - `T/Idea/From/User/src/flavors.py` - Definice flavors
  - `T/Idea/Model/src/simple_idea_db.py` - Databázové operace
  - `src/config.py` - Konfigurace

**Výstupní závislosti:**
- Modul 02 (PrismQ.T.Story.From.Idea) - čte vytvořené Ideas z databáze
- Tabulka `Idea` v databázi - source of truth pro další moduly

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Modul podporuje batch processing přes `T/Idea/Batch/src/`
- Preview režim je klíčový pro testování bez ovlivnění databáze
- Flavors jsou weighted - některé se objevují častěji
- AI model může být změněn v konfiguraci
- Virtual environment je vytvořen v modulu pro izolaci dependencies

**Rizika:**
- **AI nedostupnost**: Pokud Ollama server není spuštěn nebo model není nainstalován, modul selže
- **Kvalita AI výstupu**: AI může generovat nekvalitní nebo nevalidní data (částečně ošetřeno validací)
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
