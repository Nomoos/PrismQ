# Rychlý Průvodce - Research_Layers

**Vítejte!** Tento průvodce vám pomůže začít s Research_Layers zdroji během 5 minut.

---

## 🚀 5minutový Rychlý Start

### 1. Začněte Zde (1 minuta)
Přečtěte si: **[RESEARCH_QUESTIONS_ANSWERED_CS.md](./RESEARCH_QUESTIONS_ANSWERED_CS.md)**
- Rychlý přehled všeho v Research_Layers
- Odpovědi na běžné otázky
- Odkazy na podrobné zdroje

### 2. Spusťte Příklad (2 minuty)
```bash
cd Research_Layers/02_Design_Patterns/examples

# Spusťte váš první příklad
python solid_single_responsibility.py

# Nebo rozšířené design patterns v češtině
python design_patterns_extended.py
```

### 3. Prohlédněte Clean Code Checklist (2 minuty)
Prolistujte: **[CLEAN_CODE_CHECKLIST.md](./CLEAN_CODE_CHECKLIST.md)**
- Zaměřte se na "Quick Reference Card" na konci
- Uložte si do záložek pro pozdější použití
- Používejte během code review

---

## 📚 Co Číst podle Vaší Role

### Jsem Nový Vývojář
**Cesta**: Učení základů
1. **[RESEARCH_QUESTIONS_ANSWERED_CS.md](./RESEARCH_QUESTIONS_ANSWERED_CS.md)** (30 min) - Přehled
2. **Spusťte všechny příklady** (30 min):
   ```bash
   cd 02_Design_Patterns/examples
   python solid_single_responsibility.py
   python solid_open_closed.py
   python design_patterns.py
   python design_patterns_extended.py  # Nové!
   ```
3. **[CLEAN_CODE_CHECKLIST.md](./CLEAN_CODE_CHECKLIST.md)** (20 min) - Praktický průvodce
4. **[02_Design_Patterns/01_SOLID_PRINCIPLES_GUIDE.md](./02_Design_Patterns/01_SOLID_PRINCIPLES_GUIDE.md)** (30 min) - Hloubkové ponory

**Celkový Čas**: ~2 hodiny  
**Výsledek**: Připraven psát dobrý kód

### Právě Píšu Kód
**Cesta**: Rychlá reference
1. **[CLEAN_CODE_CHECKLIST.md](./CLEAN_CODE_CHECKLIST.md)** - Než začnete
2. **[05_Templates/](./05_Templates/)** - Zkopírujte šablonu pro váš kód
3. **[PEP8_STANDARDS.md](./PEP8_STANDARDS.md)** - Otázky stylu
4. **[02_Design_Patterns/examples/](./02_Design_Patterns/examples/)** - Reference vzorů

**Celkový Čas**: Podle potřeby  
**Výsledek**: Psát čistý, konzistentní kód

### Nastavuji Své Prostředí
**Cesta**: Nastavení prostředí
1. **[VIRTUAL_ENVIRONMENT_GUIDE.md](./VIRTUAL_ENVIRONMENT_GUIDE.md)** (15 min)
2. Následujte instrukce nastavení pro váš modul
3. Nakonfigurujte své IDE

**Celkový Čas**: 30 minut (nastavení) + 15 minut (čtení)  
**Výsledek**: Funkční vývojové prostředí

### Recenzuji Kód
**Cesta**: Průvodce code review
1. **[CLEAN_CODE_CHECKLIST.md](./CLEAN_CODE_CHECKLIST.md)** - Sekce kontrolního seznamu review
2. **[02_Design_Patterns/04_CODE_REVIEW_GUIDELINES.md](./02_Design_Patterns/04_CODE_REVIEW_GUIDELINES.md)**
3. Kontrola příkladů pro referenci vzorů

**Celkový Čas**: 10 minut  
**Výsledek**: Efektivní code reviews

---

## 🎯 Běžné Úkoly

### "Potřebuji porozumět SOLID principům"
```bash
# Přečíst
→ 02_Design_Patterns/01_SOLID_PRINCIPLES_GUIDE.md

# Spustit příklady
→ cd 02_Design_Patterns/examples
→ python solid_single_responsibility.py
→ python solid_open_closed.py
→ python solid_dependency_inversion.py
```

### "Potřebuji nastavit virtuální prostředí"
```bash
# Přečíst průvodce
→ VIRTUAL_ENVIRONMENT_GUIDE.md

# Následovat nastavení pro váš modul
→ cd Source/VášModul
→ python -m venv venv
→ source venv/bin/activate  # nebo venv\Scripts\activate na Windows
→ pip install -e .
```

### "Potřebuji porozumět design patterns"
```bash
# Spustit komplexní příklad
→ cd 02_Design_Patterns/examples
→ python design_patterns.py

# Spustit rozšířené vzory (Decorator, Chain, Command, State, Builder)
→ python design_patterns_extended.py

# Vidět vzory v akci:
# Základní: Strategy, Factory, Observer, Adapter, Repository
# Rozšířené: Decorator, Chain of Responsibility, Command, State, Builder
```

### "Potřebuji zkontrolovat styl kódu"
```bash
# Přečíst průvodce stylu
→ PEP8_STANDARDS.md

# Použít nástroje
→ black .           # Auto-formátování
→ flake8 .          # Linting
→ mypy .            # Kontrola typů
```

### "Potřebuji šablonu kódu"
```bash
# Přejít na šablony
→ cd 05_Templates

# Zkopírovat vhodnou šablonu
→ TEMPLATE_SOURCE_PLUGIN.py
→ TEMPLATE_PROCESSING_MODULE.py
→ example_worker.py
```

### "Potřebuji porozumět architektuře vrstev"
```bash
# Přečíst architektonické dokumenty
→ 01_Architecture/README.md

# Spustit příklad
→ python 01_Architecture/examples/layer_separation.py

# Vidět 5 vrstev v akci:
# Application → Processing → Collection → Model → Infrastructure
```

---

## 📖 Všechny Zdroje na První Pohled

### Hlavní Průvodci (Začněte Zde) ⭐
| Soubor | Velikost | Účel | Čas |
|--------|----------|------|-----|
| [RESEARCH_QUESTIONS_ANSWERED_CS.md](./RESEARCH_QUESTIONS_ANSWERED_CS.md) | 13KB | Kompletní přehled (česky) | 30 min |
| [CLEAN_CODE_CHECKLIST.md](./CLEAN_CODE_CHECKLIST.md) | 10KB | Praktický checklist | 20 min |
| [PEP8_STANDARDS.md](./PEP8_STANDARDS.md) | 11KB | Průvodce stylu | 20 min |
| [VIRTUAL_ENVIRONMENT_GUIDE.md](./VIRTUAL_ENVIRONMENT_GUIDE.md) | 7KB | Průvodce nastavením | 15 min |

### Python Příklady (Spusťte Tyto!) 🐍
| Soubor | Řádků | Demonstruje | Funkční |
|--------|-------|-------------|---------|
| solid_single_responsibility.py | 172 | SRP | ✅ |
| solid_open_closed.py | 254 | OCP | ✅ |
| solid_dependency_inversion.py | 226 | DIP | ✅ |
| design_patterns.py | 343 | 5 vzorů | ✅ |
| design_patterns_extended.py | 🆕 | 5 dalších vzorů | ✅ |
| layer_separation.py | ~50 | Architektura | ✅ |

### Podrobná Dokumentace
- **[01_Architecture/](./01_Architecture/)** - Systémová architektura
- **[02_Design_Patterns/](./02_Design_Patterns/)** - SOLID & vzory
- **[03_Testing/](./03_Testing/)** - Testovací strategie
- **[04_WorkerHost/](./04_WorkerHost/)** - Worker dokumentace
- **[05_Templates/](./05_Templates/)** - Šablony kódu

---

## 💡 Tipy pro Úspěch

### Dělat ✅
- ✅ Spusťte Python příklady - jsou tam, aby byly spuštěny!
- ✅ Použijte checklisty během kódování a reviews
- ✅ Odkazujte na průvodce, když máte otázky
- ✅ Kopírujte šablony jako výchozí body
- ✅ Sdílejte užitečné zdroje s kolegy

### Nedělat ❌
- ❌ Nepokoušejte se přečíst vše najednou
- ❌ Nepřeskakujte příklady - jsou nejlepšími učiteli
- ❌ Neignorujte checklisty - šetří čas
- ❌ Nevynalézejte vzory - používejte co je dokumentováno

---

## 🎓 Vzdělávací Cesty

### Cesta 1: Rychlý Start (30 minut)
1. RESEARCH_QUESTIONS_ANSWERED_CS.md (přehled)
2. Spustit solid_single_responsibility.py
3. Prolistovat CLEAN_CODE_CHECKLIST.md

**Výsledek**: Základní porozumění, připraven kódovat

### Cesta 2: Hloubkové Ponory (4 hodiny)
1. RESEARCH_QUESTIONS_ANSWERED_CS.md
2. Spustit všechny Python příklady
3. Přečíst SOLID_PRINCIPLES_GUIDE.md
4. Přečíst TESTING_STRATEGY.md
5. Studovat architekturu vrstev

**Výsledek**: Komplexní porozumění

### Cesta 3: Reference (průběžně)
- Mít CLEAN_CODE_CHECKLIST.md otevřený během kódování
- Odkazovat na PEP8_STANDARDS.md pro otázky stylu
- Kontrolovat příklady při implementaci vzorů
- Používat šablony pro nový kód

**Výsledek**: Konzistentní, vysoce kvalitní kód

---

## ❓ Často Kladené Otázky

### O: Kde mám začít?
**A**: [RESEARCH_QUESTIONS_ANSWERED_CS.md](./RESEARCH_QUESTIONS_ANSWERED_CS.md) - Je to váš vstupní bod.

### O: Musím přečíst vše?
**A**: Ne! Používejte to, co potřebujete, když to potřebujete. Ale určitě spusťte příklady.

### O: Jsou Python příklady důležité?
**A**: Ano! Jsou nejlepší způsob, jak porozumět konceptům. Všechny jsou testované a funkční.

### O: Jak poznám, který vzor použít?
**A**: Zkontrolujte [design_patterns.py](./02_Design_Patterns/examples/design_patterns.py) a [design_patterns_extended.py](./02_Design_Patterns/examples/design_patterns_extended.py) pro příklady, nebo RESEARCH_QUESTIONS_ANSWERED_CS.md pro návod.

### O: Co když mám otázky?
**A**: 
1. Zkontrolujte relevantní dokumentaci
2. Podívejte se na příklady
3. Zeptejte se členů týmu
4. Prohlédněte kód v existujících modulech

---

## 🎯 Další Kroky

Po tomto rychlém startu:

1. **Uložte do záložek** důležité soubory ve vašem prohlížeči/IDE
2. **Spusťte** Python příklady
3. **Aplikujte** vzory ve vašem kódu
4. **Sdílejte** co se naučíte s týmem

---

**Pamatujte**: Tyto zdroje jsou zde, aby vám pomohly psát lepší kód rychleji. Používejte je!

**Poslední Aktualizace**: 2025-11-15  
**Stav**: Připraveno k použití ✅

---

Připraveni jít hlouběji? Začněte s [RESEARCH_QUESTIONS_ANSWERED_CS.md](./RESEARCH_QUESTIONS_ANSWERED_CS.md)!

## 🆕 Co je Nového

### Nedávné Přidání
- **design_patterns_extended.py** - 5 nových design patterns:
  - Decorator Pattern - Dynamické přidání funkcionalit
  - Chain of Responsibility - Řetězec zpracovatelů
  - Command Pattern - Zapouzdření požadavků (s undo/redo)
  - State Pattern - Změna chování podle stavu
  - Builder Pattern - Krok za krokem konstrukce objektů

- **České Překlady** - Klíčová dokumentace nyní dostupná v češtině:
  - RESEARCH_QUESTIONS_ANSWERED_CS.md
  - QUICK_START_CS.md (tento soubor)

### Celkový Počet Design Patterns
Nyní máme **10 plně funkčních design patterns** s příklady:
1. Strategy Pattern ⭐⭐⭐⭐⭐
2. Factory Pattern ⭐⭐⭐⭐⭐
3. Repository Pattern ⭐⭐⭐⭐⭐
4. Observer Pattern ⭐⭐⭐⭐
5. Adapter Pattern ⭐⭐⭐⭐
6. Decorator Pattern ⭐⭐⭐⭐
7. Chain of Responsibility ⭐⭐⭐⭐
8. Command Pattern ⭐⭐⭐⭐
9. State Pattern ⭐⭐⭐⭐
10. Builder Pattern ⭐⭐⭐⭐
