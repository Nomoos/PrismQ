# Kontrola běhu modulu: PrismQ.T.Content.From.Idea.Title

## 🎯 Účel modulu
Generování textového obsahu (Content v1 / Script) pro Story objekty na základě titulku a původního nápadu. Modul vytváří strukturovaný skript vhodný pro 120-sekundové video (~300 slov, max 175s) s AI pomocí, optimalizovaný pro cílové publikum.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Story s title a idea_id referencí)
- **Typ dat:** Story objekty ve stavu "PrismQ.T.Content.From.Idea.Title"
- **Povinné hodnoty:**
  - Story s platným title fieldem (vygenerovaný v modulu 03)
  - Platná idea_id reference s existujícím Idea záznamem
  - Text obsah z Idea záznamu (pro kontext)
- **Nepovinné hodnoty:**
  - `--preview` flag - režim bez uložení do databáze
  - `--debug` flag - detailní logování
  - Target audience parametry (věk, pohlaví, lokace)
  - Seed words pro kreativní inspiraci (504 slov)
- **Očekávané předpoklady:**
  - Story s titulkem vytvořeným modulem 03
  - Běžící Ollama server (localhost:11434)
  - Dostupný AI model (např. Qwen3:30b)
  - Aktivní Python virtual environment
  - Přístup k databázi (read + write)

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Inicializace prostředí:**
   - Kontrola Python instalace
   - Vytvoření/aktivace virtual environment
   - Instalace dependencies (requests, pytest, pytest-cov)
   - Spuštění Ollama serveru
   - Kontrola dostupnosti AI modelu

2. **Načtení Stories k zpracování:**
   - Připojení k databázi
   - Dotaz na Stories ve stavu "PrismQ.T.Content.From.Idea.Title"
   - Pro každou Story načtení:
     - title (vygenerovaný titulek)
     - idea_id a idea text (pro kontext)

3. **Příprava generování (pro každou Story):**
   - Načtení kompletního Idea textu z databáze
   - Extrakce klíčových bodů z Idea
   - Definování target audience:
     - Věk: 13-23 (default)
     - Pohlaví: Ženy (default)
     - Lokace: USA (default)
   - Výběr seed word pro kreativní inspiraci (z 504 slov)

4. **Generování obsahu pomocí AI:**
   - Sestavení AI promptu kombinující:
     - Titulek (title)
     - Kontext z Idea (description, key points)
     - Target audience specifikaci
     - Seed word pro inspiraci
     - Požadavky na délku (~300 slov)
     - Požadavky na strukturu (intro, body, conclusion)
     - Požadavky na tón a styl
   - Odeslání requestu na Ollama API
   - AI generuje strukturovaný skript
   - Parsing AI odpovědi

5. **Strukturování Content objektu:**
   - Vytvoření ContentV1 objektu s fieldy:
     - `text` - Hlavní text skriptu
     - `introduction` - Úvodní sekce
     - `body` - Hlavní tělo obsahu
     - `conclusion` - Závěrečná sekce
     - `word_count` - Počet slov (cílově ~300)
     - `estimated_duration` - Odhad délky (sekund)
     - `target_audience` - Specifikace publika
     - `seed_word` - Použité seed slovo
     - `created_at` - Timestamp

6. **Validace vygenerovaného obsahu:**
   - Kontrola délky (max 175s / ~300 slov)
   - Kontrola struktury (všechny sekce přítomny)
   - Kontrola kvality textu
   - Validace word count

7. **Uložení Content do databáze:**
   - Insert do tabulky Content (pokud existuje) nebo
   - Uložení jako structured text v Story objektu
   - Získání content_id

8. **Update Story objektu:**
   - Nastavení content_id nebo content fieldu
   - Změna stavu na "PrismQ.T.Review.Title.From.Content.Idea"
   - Uložení metadata (word_count, duration, audience)

9. **Uložení do databáze (production režim):**
   - Update Story záznamu
   - Commit transakce
   - Zalogování úspěšného update

10. **Reportování:**
    - Zobrazení vygenerovaného obsahu (zkrácená verze)
    - Zobrazení word count a estimated duration
    - Progress indikace
    - Statistiky zpracování

11. **Ošetření chybových stavů:**
    - Žádné Stories k zpracování - informační zpráva
    - Ollama nedostupný - chybová zpráva, ukončení
    - AI generování selhalo - retry (3x), pak skip
    - Content příliš dlouhý - re-generování s přísnějšími omezeními
    - Databázové chyby - rollback, logování
    - Invalid structure - re-generování (max 3 pokusy)

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:**
  - ContentV1 objekty s vygenerovaným strukturovaným skriptem
  - Story objekty ve stavu "PrismQ.T.Review.Title.From.Content.Idea"
  - Content s introduction, body, conclusion sekcemi
  
- **Formát výstupu:**
  - Konzolový výstup: 
    - Vygenerovaný obsah (intro + závěr, body zkrácený)
    - Word count, estimated duration
    - Progress indikace
  - Databáze (production): 
    - Nové záznamy v tabulce Content (nebo embedded v Story)
    - Updated Story záznamy (content_id, state)
  - Log soubor (debug): 
    - Kompletní vygenerovaný text
    - AI prompts a odpovědi
    - Validation metriky
  
- **Vedlejší efekty:**
  - Vytvoření virtual environment (.venv)
  - Instalace Python packages
  - Spuštění Ollama serveru
  - AI model cache
  - Log soubory v debug režimu
  
- **Chování při chybě:**
  - Ollama error: Chybová zpráva, ukončení
  - AI generování selhalo: Retry 3x, pak skip Story
  - Content příliš dlouhý/krátký: Re-generování s adjustovanými parametry (max 3x)
  - Databázová chyba: Rollback, logování, ukončení
  - Structure validation failed: Re-generování (max 3x), pak použití unstructured fallback

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 03 (PrismQ.T.Title.From.Idea) - vytváří Stories s titulky
- Modul 01 (PrismQ.T.Idea.Creation) - source Idea textu pro kontext
- Ollama server (AI model hosting)
- AI model pro generování obsahu (např. Qwen3:30b)
- SQLite databáze s tabulkami Story, Content, Idea
- Python 3.x + virtual environment
- Moduly:
  - `T/Content/From/Idea/Title/src/` - Implementace modulu
  - Seed words databáze (504 jednoduchých slov)
  - Target audience konfigurace

**Výstupní závislosti:**
- Modul 05 (PrismQ.T.Review.Title.From.Content.Idea) - review titulku proti obsahu
- Tabulka Content v databázi - obsahuje vygenerované skripty
- Tabulka Story - obsahuje odkazy na Content

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Target duration: 120s video (~300 slov), max 175s
- Seed words poskytují 504 jednoduchých slov pro kreativní inspiraci
- Content je strukturovaný: introduction, body, conclusion
- Default target audience: Věk 13-23, Ženy, USA
- Modul podporuje různé audience profiles
- Word count a duration jsou estimované, ne přesné
- AI model musí být dostatečně velký pro kvalitní generování (30B+ parametrů)

**Rizika:**
- **AI nedostupnost**: Pokud Ollama není spuštěn, běh selže
- **Content quality variance**: AI může generovat různě kvalitní obsah
- **Duration accuracy**: Odhad délky závisí na rychlosti čtení, není přesný
- **Structure inconsistency**: AI nemusí vždy dodržet strukturu (intro/body/conclusion)
- **Performance**: Generování je pomalé (30B model, ~10-20s per content)
- **Token limits**: Velmi dlouhé Ideas mohou překročit context window AI modelu
- **Memory consumption**: Generování content pro mnoho Stories může konzumovat hodně RAM
- **Inappropriate content**: AI může občas generovat nevhodný obsah (částečně ošetřeno filtry)

**Doporučení:**
- Implementovat content moderation pro nevhodný obsah
- Přidat real-time duration estimation během psaní
- Zvážit human review pro quality assurance
- Implementovat content templates pro konzistenci
- Přidat A/B testing pro různé audience profiles
- Monitorovat AI output quality metriky
- Implementovat fallback pro structure failures
- Pravidelně review seed words pro relevanci
