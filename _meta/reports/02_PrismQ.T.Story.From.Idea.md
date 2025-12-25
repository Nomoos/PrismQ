# Kontrola běhu modulu: PrismQ.T.Story.From.Idea

## 🎯 Účel modulu
Vytváření Story objektů z existujících Idea objektů. Modul slouží jako most mezi fází nápadů a fází generování titulků - pro každý nezpracovaný nápad vytvoří 10 Story záznamů, které jsou připravené pro další zpracování v pipeline.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Idea)
- **Typ dat:** SimpleIdea objekty načtené z DB
- **Povinné hodnoty:**
  - Idea záznamy, které ještě nemají reference ve Story tabulce
  - Platné idea_id (integer ID z tabulky Idea)
- **Nepovinné hodnoty:**
  - `--preview` flag - režim bez uložení do databáze
  - `--debug` flag - detailní logování
  - Limit počtu zpracovávaných Ideas (pro batch processing)
- **Očekávané předpoklady:**
  - Existující záznamy v tabulce Idea (vytvořené modulem 01)
  - Připravená Story databázová struktura
  - Aktivní Python virtual environment
  - Přístup k databázi (read + write)

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Inicializace prostředí:**
   - Kontrola Python instalace
   - Vytvoření/aktivace virtual environment
   - Instalace dependencies
   - Kontrola dostupnosti databází

2. **Načtení nezpracovaných Ideas:**
   - Připojení k SimpleIdeaDatabase
   - Dotaz na Ideas bez reference ve Story tabulce
   - Načtení Idea objektů s ID a text obsahem

3. **Identifikace zpracovatelných Ideas:**
   - Pro každou Idea kontrola, zda už není referována v Story tabulce
   - Filtrování pouze Ideas bez Story záznamů
   - Příprava listu Ideas k zpracování

4. **Vytváření Story objektů:**
   - Pro každou nezpracovanou Idea (iterace):
     - Vytvoření 10 Story objektů
     - Každý Story obsahuje:
       - idea_id - reference na původní Idea
       - state = "PrismQ.T.Title.From.Idea" (připraveno pro modul 03)
       - created_at timestamp
       - Zatím bez title, content nebo jiných atributů
   - Progress indikace během tvorby

5. **Uložení do databáze (production režim):**
   - Pro každý vytvořený Story objekt:
     - Insert do tabulky Story
     - Získání story_id (auto-increment)
     - Zalogování úspěšného vytvoření
   - Commit transakce

6. **Reportování výsledků:**
   - Zobrazení počtu zpracovaných Ideas
   - Zobrazení počtu vytvořených Stories
   - Seznam story_id pro každou Idea
   - Barevný formátovaný výstup

7. **Loop pro continuous processing:**
   - Možnost opakovaného spuštění
   - Automatické zpracování nových Ideas

8. **Ošetření chybových stavů:**
   - Prázdná Idea tabulka - informační zpráva, ukončení
   - Všechny Ideas už mají Stories - informační zpráva, ukončení
   - Databázové chyby - rollback, logování, zobrazení chyby
   - Import errors - graceful degradation
   - Ctrl+C handling - čisté ukončení s uzavřením DB

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:**
  - 10 Story objektů pro každou zpracovanou Idea
  - Story objekty ve stavu "PrismQ.T.Title.From.Idea"
  - Story objekty obsahují pouze idea_id referenci (žádný title ani content)
  
- **Formát výstupu:**
  - Konzolový výstup: Statistiky zpracování, barevně formátované
  - Databáze (production): Nové záznamy v tabulce `Story`
  - Log soubor (debug): Detailní log všech DB operací
  
- **Vedlejší efekty:**
  - Vytvoření virtual environment (.venv)
  - Instalace Python packages
  - Vytvoření Story tabulky (pokud neexistuje)
  - Log soubory v debug režimu
  - Update statistik zpracovaných Ideas
  
- **Chování při chybě:**
  - Import error: Zobrazení chybové zprávy, ukončení
  - Databázová chyba: Rollback transakce, logování, zobrazení chyby
  - Žádné Ideas k zpracování: Informační zpráva, čisté ukončení
  - Partial failure: Zpracované Stories se commitnou, chyba se zaloguje

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 01 (PrismQ.T.Idea.From.User) - musí být spuštěn první, vytváří Ideas
- SQLite databáze s tabulkou Idea
- Python 3.x + virtual environment
- Moduly:
  - `T/Story/From/Idea/src/story_from_idea_service.py` - Servisní logika
  - `T/Story/From/Idea/src/story_from_idea_interactive.py` - Interaktivní rozhraní
  - `T/Idea/Model/src/simple_idea.py` - Idea model
  - `T/Idea/Model/src/simple_idea_db.py` - Idea databáze
  - `Model/Database/models/story.py` - Story model
  - `Model/Database/repositories/story_repository.py` - Story repository

**Výstupní závislosti:**
- Modul 03 (PrismQ.T.Title.From.Idea) - čte Stories ve stavu "PrismQ.T.Title.From.Idea"
- Tabulka `Story` v databázi - obsahuje Stories s idea_id referencemi

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Modul pouze vytváří Story záznamy, negeneruje žádný obsah (title, content)
- Každá Idea vytváří přesně 10 Story objektů (hardcoded konstanta)
- Story objekty jsou vytvářeny ve stavu připraveném pro modul 03
- Modul podporuje idempotentní zpracování - už zpracované Ideas přeskakuje
- Preview režim umožňuje testování bez změny databáze
- Modul může běžet v continuous mode pro automatické zpracování

**Rizika:**
- **Databázová konzistence**: Pokud modul selže uprostřed, některé Ideas mohou mít pouze částečné Stories (ošetřeno transakcemi)
- **Concurrent execution**: Více instancí může vytvořit duplicitní Stories (SQLite write locking)
- **Škálovatelnost**: Při velkém počtu Ideas (10k+) může být paměť nedostatečná
- **Orphaned Stories**: Pokud se Idea smaže, Stories zůstanou (bez CASCADE DELETE)
- **Fixed multiplier**: 10 Stories na Idea je hardcoded - změna vyžaduje úpravu kódu

**Doporučení:**
- Implementovat batch processing s limitováním paměti
- Přidat konfigurační parametr pro počet Stories na Idea
- Zvážit implementaci CASCADE DELETE pro data integrity
- Monitorovat velikost Story tabulky
- Implementovat cleaning mechanismus pro orphaned Stories
- Přidat progress bar pro dlouhé běhy
