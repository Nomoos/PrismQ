# Kompletní MVP Workflow - Všechny Stavy a Zpětnovazební Smyčky

**Vytvořeno**: 2025-11-22  
**Stav**: Všechny MVPs dokončeny (24/24) ✅  
**Účel**: Detailní popis všech 24 MVP stavů s čísly, podmínkami a zpětnými vazbami

---

## Přehled

Tento dokument popisuje **kompletní iterativní workflow MVP** s 24 stavy včetně všech zpětnovazebních smyček a podmínek pro přechody mezi stavy.

**Klíčové vlastnosti:**
- ✅ 24 stavů rozdělených do 3 sprintů
- ✅ Dynamické verzování - každý nový titulek nebo skript zvýší číslo verze o 1
- ✅ Křížová validace titulku a skriptu
- ✅ Více kvalitních kontrol (Grammar, Tone, Content, Consistency, Editing)
- ✅ Kontroly čitelnosti pro voiceover
- ✅ Expertní revize a vybrušování
- ✅ Export a reportování publikování

**DŮLEŽITÉ - Verzování:**
- ⚠️ Čísla verzí (v1, v2, v3...) v tomto dokumentu jsou **pouze ilustrativní příklady**
- ⚠️ Ve skutečnosti se verze **inkrementují dynamicky** - při každé změně titulku nebo skriptu se číslo verze zvýší o 1
- ⚠️ Workflow **není fixované na konkrétní čísla verzí** - MVP-002 nevytváří vždy "v1", může vytvořit jakoukoliv verzi podle historie
- ⚠️ Například: Pokud titulek prošel 10 iteracemi, aktuální verze může být v11, v12, atd.

---

## Sprint 1: Základ & Křížové Revize (MVP-001 až MVP-005)

### ✅ MVP-001: T.Idea.Creation
**Modul**: `PrismQ.T.Idea.Creation`  
**Účel**: Vytvoření a zachycení původního nápadu na obsah

**Vstupy:**
- Text popisující nápad (od uživatele)

**Výstupy:**
- Objekt Idea s unikátním ID
- Uloženo v databázi s časovým razítkem

**Podmínky přechodu:**
- ✅ ÚSPĚCH → Pokračuje na **MVP-002** (Title v1)
- ❌ Pokud prázdné nebo neplatné → Zůstává ve stavu Creation

---

### ✅ MVP-002: T.Title.FromIdea
**Modul**: `PrismQ.T.Title.FromIdea`  
**Účel**: Generování prvního titulku z nápadu

**Vstupy:**
- Objekt Idea (z MVP-001)

**Výstupy:**
- 3-5 variant titulku (první verze)
- Jeden vybraný titulek pro pokračování
- 💡 Číslo verze závisí na historii (může být v1, v5, v10...)

**Podmínky přechodu:**
- ✅ ÚSPĚCH → Pokračuje na **MVP-003** (Script - první verze)

---

### ✅ MVP-003: T.Script.FromIdeaAndTitle
**Modul**: `PrismQ.T.Script.FromIdeaAndTitle`  
**Účel**: Generování prvního skriptu z nápadu a titulku

**Vstupy:**
- Objekt Idea (z MVP-001)
- Titulek (z MVP-002)

**Výstupy:**
- Kompletní skript - první verze
- Strukturovaný text připravený k revizi
- 💡 Číslo verze závisí na historii (může být v1, v5, v10...)

**Podmínky přechodu:**
- ✅ ÚSPĚCH → Pokračuje na **MVP-004** (Revize titulku)

---

### ✅ MVP-004: T.Review.Title.ByScript
**Modul**: `PrismQ.T.Review.Title.ByScript`  
**Účel**: Revize aktuálního titulku v kontextu aktuálního skriptu

**Vstupy:**
- Titulek (z MVP-002)
- Skript (z MVP-003)
- Původní Idea (z MVP-001)

**Výstupy:**
- Review JSON se zpětnou vazbou na titulek
- Skóre alignment (0-100)
- Návrhy na vylepšení

**Podmínky přechodu:**
- ✅ VŽDY → Pokračuje na **MVP-005** (Revize skriptu)
- 📝 Zpětná vazba se používá později v MVP-006

---

### ✅ MVP-005: T.Review.Script.ByTitle
**Modul**: `PrismQ.T.Review.Script.ByTitle`  
**Účel**: Revize aktuálního skriptu v kontextu aktuálního titulku

**Vstupy:**
- Skript v1 (z MVP-003)
- Titulek v1 (z MVP-002)
- Původní Idea (z MVP-001)

**Výstupy:**
- Review JSON se zpětnou vazbou na skript
- Skóre coherence (0-100)
- Návrhy na vylepšení

**Podmínky přechodu:**
- ✅ VŽDY → Pokračuje na **MVP-006** (Title Improvements)
- 📝 Zpětná vazba se používá v MVP-007

---

## Sprint 2: Cyklus Vylepšování (MVP-006 až MVP-011)

### ✅ MVP-006: T.Title.Improvements
**Modul**: `PrismQ.T.Title.FromOriginalTitleAndReviewAndScript`  
**Účel**: Vylepšení titulku pomocí zpětné vazby (verze +1)

**Vstupy:**
- Aktuální titulek (z MVP-002)
- Review titulku (z MVP-004)
- Aktuální skript (z MVP-003)

**Výstupy:**
- Vylepšený titulek (nová verze = aktuální +1)
- Reference na předchozí verzi pro sledování změn
- 💡 Např: pokud vstupní titulek byl v3, výstup bude v4

**Podmínky přechodu:**
- ✅ ÚSPĚCH → Pokračuje na **MVP-007** (Script Improvements)

---

### ✅ MVP-007: T.Script.Improvements
**Modul**: `PrismQ.T.Script.FromOriginalScriptAndReviewAndTitle`  
**Účel**: Vylepšení skriptu pomocí zpětné vazby (verze +1)

**Vstupy:**
- Aktuální skript (z MVP-003)
- Review skriptu (z MVP-005)
- Nejnovější titulek (z MVP-006) - POUŽÍVÁ NOVÝ TITULEK!

**Výstupy:**
- Vylepšený skript (nová verze = aktuální +1)
- Reference na předchozí verzi pro sledování změn
- 💡 Např: pokud vstupní skript byl v5, výstup bude v6

**Podmínky přechodu:**
- ✅ ÚSPĚCH → Pokračuje na **MVP-008** (Revize titulku)

---

### ✅ MVP-008: T.Review.Title.ByScript
**Modul**: `PrismQ.T.Review.Title.ByScript`  
**Účel**: Revize aktuálního titulku proti aktuálnímu skriptu

**Vstupy:**
- Aktuální titulek (z MVP-006)
- Aktuální skript (z MVP-007)
- Původní Idea (z MVP-001)

**Výstupy:**
- Review JSON s novou zpětnou vazbou
- Porovnání vylepšení oproti předchozí verzi

**Podmínky přechodu:**
- ✅ VŽDY → Pokračuje na **MVP-009** (Title Refinement)
- 📝 Zpětná vazba se používá pro další vybrušování

---

### ✅ MVP-009: T.Title.Refinement
**Modul**: `PrismQ.T.Title.FromOriginalTitleAndReviewAndScript`  
**Účel**: Vybrušování titulku pomocí zpětné vazby (verze +1)

**Vstupy:**
- Aktuální titulek (z MVP-006)
- Review titulku (z MVP-008)
- Aktuální skript (z MVP-007)

**Výstupy:**
- Vybroušený titulek (nová verze = aktuální +1)
- Podporuje neomezené verze - vždy jen +1 od aktuální
- 💡 Např: pokud vstupní titulek byl v7, výstup bude v8

**Podmínky přechodu:**
- ✅ ÚSPĚCH → Pokračuje na **MVP-010** (Revize skriptu)

---

### ✅ MVP-010: T.Review.Script.ByTitle
**Modul**: `PrismQ.T.Review.Script.ByTitle`  
**Účel**: Revize aktuálního skriptu proti nejnovějšímu titulku

**Vstupy:**
- Aktuální skript (z MVP-007)
- Nejnovější titulek (z MVP-009) - POUŽÍVÁ NEJNOVĚJŠÍ TITULEK!
- Původní Idea (z MVP-001)

**Výstupy:**
- Review JSON s novou zpětnou vazbou
- Porovnání s předchozí verzí skriptu

**Podmínky přechodu:**
- ✅ VŽDY → Pokračuje na **MVP-011** (Script Refinement)
- 📝 Zpětná vazba se používá pro vybrušování

---

### ✅ MVP-011: T.Script.Refinement
**Modul**: `PrismQ.T.Script.FromOriginalScriptAndReviewAndTitle`  
**Účel**: Vybrušování skriptu pomocí zpětné vazby (verze +1)

**Vstupy:**
- Aktuální skript (z MVP-007)
- Review skriptu (z MVP-010)
- Nejnovější titulek (z MVP-009)

**Výstupy:**
- Vybroušený skript (nová verze = aktuální +1)
- Podporuje neomezené verze - vždy jen +1 od aktuální
- Zajišťuje sladění s nejnovější verzí titulku
- 💡 Např: pokud vstupní skript byl v12, výstup bude v13

**Podmínky přechodu:**
- ✅ ÚSPĚCH → Pokračuje na **MVP-012** (Akceptace titulku)

---

## Sprint 3: Validace & Kvalita (MVP-012 až MVP-024)

### ✅ MVP-012: T.Review.Title.Acceptance
**Modul**: `PrismQ.T.Review.Title.Acceptance`  
**Účel**: Brána akceptace - Je titulek připraven?

**Vstupy:**
- Nejnovější titulek (aktuální verze)
- Historie všech revizí

**Výstupy:**
- Rozhodnutí: PASS nebo FAIL
- Skóre akceptace (0-100)
- Důvody pokud FAIL

**Podmínky přechodu:**
- ✅ PASS (skóre ≥85) → Pokračuje na **MVP-013** (Akceptace skriptu)
- ❌ FAIL (skóre <85) → Smyčka zpět na **MVP-009** (Title Refinement)
  - Vytvoří novou verzi (aktuální +1) dokud neprojde
  - POUŽÍVÁ vždy nejnovější verze

---

### ✅ MVP-013: T.Review.Script.Acceptance
**Modul**: `PrismQ.T.Review.Script.Acceptance`  
**Účel**: Brána akceptace - Je skript připraven?

**Vstupy:**
- Nejnovější skript (aktuální verze)
- Akceptovaný titulek (z MVP-012)
- Historie všech revizí

**Výstupy:**
- Rozhodnutí: PASS nebo FAIL
- Skóre akceptace (0-100)
- Důvody pokud FAIL

**Podmínky přechodu:**
- ✅ PASS (skóre ≥85) → Pokračuje na **MVP-014** (Grammar Review)
- ❌ FAIL (skóre <85) → Smyčka zpět na **MVP-011** (Script Refinement)
  - Vytvoří novou verzi (aktuální +1) dokud neprojde
  - Pokud titulek také potřebuje změny → zpět na MVP-009

---

### ✅ MVP-014: T.Review.Script.Grammar
**Modul**: `PrismQ.T.Review.Script.Grammar`  
**Účel**: Kontrola gramatiky, pravopisu, interpunkce

**Vstupy:**
- Nejnovější skript (akceptovaný z MVP-013)

**Výstupy:**
- Grammar Review JSON
- Skóre (0-100)
- Seznam problémů podle závažnosti (critical, high, medium, low)
- Návrhy oprav

**Podmínky přechodu:**
- ✅ PASS (skóre ≥85 a žádné critical issues) → Pokračuje na **MVP-015** (Tone Review)
- ❌ FAIL → Smyčka zpět na **MVP-011** (Script Refinement)
  - Opraví gramatické problémy
  - Poté znovu projde MVP-013 a MVP-014

---

### ✅ MVP-015: T.Review.Script.Tone
**Modul**: `PrismQ.T.Review.Script.Tone`  
**Účel**: Kontrola tónu, stylu, audience

**Vstupy:**
- Nejnovější skript (prošel Grammar)

**Výstupy:**
- Tone Review JSON
- Skóre (0-100)
- Analýza tónu (formal, casual, professional, etc.)
- Problémy s konzistencí tónu

**Podmínky přechodu:**
- ✅ PASS (skóre ≥80) → Pokračuje na **MVP-016** (Content Review)
- ❌ FAIL → Smyčka zpět na **MVP-011** (Script Refinement)
  - Upraví tón pro cílové publikum
  - Poté znovu projde MVP-013, MVP-014, MVP-015

---

### ✅ MVP-016: T.Review.Script.Content
**Modul**: `PrismQ.T.Review.Script.Content`  
**Účel**: Kontrola logiky, zápletky, motivace postav, tempa

**Vstupy:**
- Nejnovější skript (prošel Grammar a Tone)

**Výstupy:**
- Content Review JSON
- Skóre (0-100)
- Logic score, plot score, character score, pacing score
- Problémy s narativem

**Podmínky přechodu:**
- ✅ PASS (skóre ≥75 a <3 high issues) → Pokračuje na **MVP-017** (Consistency Review)
- ❌ FAIL → Smyčka zpět na **MVP-011** (Script Refinement)
  - Opraví narativní problémy
  - Poté znovu projde MVP-013, MVP-014, MVP-015, MVP-016

---

### ✅ MVP-017: T.Review.Script.Consistency
**Modul**: `PrismQ.T.Review.Script.Consistency`  
**Účel**: Kontrola konzistence jmen postav, časové osy, lokací

**Vstupy:**
- Nejnovější skript (prošel Content)

**Výstupy:**
- Consistency Review JSON
- Skóre (0-100)
- Character score, timeline score, location score, logic score
- Rozpory a nesrovnalosti

**Podmínky přechodu:**
- ✅ PASS (skóre ≥80 a <2 high issues) → Pokračuje na **MVP-018** (Editing Review)
- ❌ FAIL → Smyčka zpět na **MVP-011** (Script Refinement)
  - Opraví nesrovnalosti
  - Poté znovu projde MVP-013 až MVP-017

---

### ✅ MVP-018: T.Review.Script.Editing
**Modul**: `PrismQ.T.Review.Script.Editing`  
**Účel**: Kontrola jasnosti vět, struktur, redundance

**Vstupy:**
- Nejnovější skript (prošel Consistency)

**Výstupy:**
- Editing Review JSON
- Skóre (0-100)
- Problémy: clarity, redundancy, flow, structure, wordiness
- Návrhy přepisů

**Podmínky přechodu:**
- ✅ PASS (skóre ≥85) → Pokračuje na **MVP-019** (Title Readability)
- ❌ FAIL → Smyčka zpět na **MVP-011** (Script Refinement)
  - Přepíše nejasné věty
  - Odstraní redundanci
  - Poté znovu projde MVP-013 až MVP-018

---

### ✅ MVP-019: T.Review.Title.Readability
**Modul**: `PrismQ.T.Review.Title.Readability`  
**Účel**: Kontrola čitelnosti titulku pro voiceover

**Vstupy:**
- Nejnovější titulek (akceptovaný z MVP-012)

**Výstupy:**
- Readability Review JSON
- Skóre (0-100)
- Pronunciation score, length score, engagement score
- Problémy s výslovností

**Podmínky přechodu:**
- ✅ PASS (skóre ≥85) → Pokračuje na **MVP-020** (Script Readability)
- ❌ FAIL → Smyčka zpět na **MVP-009** (Title Refinement)
  - Upraví pro lepší čitelnost
  - Poté znovu projde MVP-012 a MVP-019

---

### ✅ MVP-020: T.Review.Script.Readability
**Modul**: `PrismQ.T.Review.Script.Readability`  
**Účel**: Kontrola čitelnosti skriptu pro voiceover

**Vstupy:**
- Nejnovější skript (prošel všechny předchozí kontroly)
- Nejnovější titulek (prošel Title Readability)

**Výstupy:**
- Readability Review JSON
- Skóre (0-100)
- Pronunciation score, flow score, pacing score
- Jazykolamy, složitá slova, problémy s tempem

**Podmínky přechodu:**
- ✅ PASS (skóre ≥85) → Pokračuje na **MVP-021** (Expert Review)
- ❌ FAIL → Smyčka zpět na **MVP-011** (Script Refinement)
  - Upraví pro lepší voiceover
  - Poté znovu projde MVP-013 až MVP-020

---

### ✅ MVP-021: T.Story.ExpertReview
**Modul**: `PrismQ.T.Story.ExpertReview`  
**Účel**: GPT-based expertní revize celého příběhu

**Vstupy:**
- Nejnovější titulek (prošel všechny kontroly)
- Nejnovější skript (prošel všechny kontroly)
- Původní Idea (z MVP-001)

**Výstupy:**
- Expert Review JSON
- Celkové skóre (0-100)
- Analýza: strengths, weaknesses, engagement, clarity
- Rozhodnutí: Ready nebo Needs Improvement

**Podmínky přechodu:**
- ✅ READY → Pokračuje na **MVP-023** (Content Export)
  - Přeskočí Polish, protože není potřeba
- 🔄 NEEDS IMPROVEMENT → Pokračuje na **MVP-022** (Expert Polish)
  - Budou aplikovány expertní návrhy

---

### ✅ MVP-022: T.Story.Polish
**Modul**: `PrismQ.T.Story.Polish`  
**Účel**: Aplikace expertních návrhů a finální vybrušování

**Vstupy:**
- Titulek v3+ (z MVP-021)
- Skript v3+ (z MVP-021)
- Expert Review feedback (z MVP-021)

**Výstupy:**
- Vybroušený titulek (může být v4, v5...)
- Vybroušený skript (může být v4, v5...)
- Polish report s aplikovanými změnami

**Podmínky přechodu:**
- ✅ VŽDY → Smyčka zpět na **MVP-021** (Expert Review)
  - Znovu zkontroluje vybroušenou verzi
  - Cyklus pokračuje dokud není Ready
- ℹ️ Když Expert Review řekne Ready → pokračuje na MVP-023

---

### ✅ MVP-023: T.Publishing.ContentExport
**Modul**: `PrismQ.T.Publishing.ContentExport`  
**Účel**: Export finálního obsahu do více formátů

**Vstupy:**
- Finální titulek (prošel všemi kontrolami)
- Finální skript (prošel všemi kontrolami)
- Metadata (author, date, version, atd.)

**Výstupy:**
- JSON soubor (strukturovaná data)
- Markdown soubor (dokumentace)
- HTML soubor (webové zobrazení)
- ContentExportResult s cestami k souborům

**Validace:**
- ✅ Všechny soubory vytvořeny
- ✅ Soubory jsou čitelné
- ✅ HTML má správné escapování (XSS prevence)

**Podmínky přechodu:**
- ✅ ÚSPĚCH → Pokračuje na **MVP-024** (Report Generation)
- ❌ SELHÁNÍ → Chyba, musí se opravit export

---

### ✅ MVP-024: T.Publishing.ReportGeneration
**Modul**: `PrismQ.T.Publishing.ReportGeneration`  
**Účel**: Generování komplexního reportu o publikování

**Vstupy:**
- Finální titulek a skript
- Workflow statistiky (verze, revize, iterace)
- Export result (z MVP-023)
- Všechny review scores

**Výstupy:**
- Publishing Report (JSON, TXT nebo MD)
- Obsahuje:
  - Workflow statistiky (total_versions, total_reviews, total_iterations)
  - Kvalitní brány, kterými prošlo
  - Finální skóre všech kontrol
  - Export informace (formáty, cesty)
  - Shrnutí a klíčové úspěchy
  - Časová osa workflow

**Podmínky přechodu:**
- ✅ ÚSPĚCH → **WORKFLOW DOKONČEN!** 🎉
  - Obsah je připraven k publikování
  - Všechny metriky zaznamenány
  - Report uložen pro budoucí referenci

---

## Souhrn Zpětnovazebních Smyček

### Primární Smyčky (Sprint 2)

**Smyčka 1: Křížová validace (MVP-004/005 → MVP-006/007)**
```
Title v1 + Script v1
    ↓
Review Title by Script + Review Script by Title
    ↓
Improvements → Title v2 + Script v2
```

**Smyčka 2: Vybrušování (MVP-008/010 → MVP-009/011)**
```
Title v2 + Script v2
    ↓
Review Title v2 + Review Script v2
    ↓
Refinement → Title v3 + Script v3
```

---

### Akceptační Smyčky (Sprint 3)

**Smyčka 3: Akceptace titulku (MVP-012)**
```
Title v3+ → Acceptance Check
    ↓
PASS → MVP-013
FAIL → MVP-009 (Title Refinement) → vytvoří v4, v5...
```

**Smyčka 4: Akceptace skriptu (MVP-013)**
```
Script v3+ → Acceptance Check
    ↓
PASS → MVP-014 (Grammar)
FAIL → MVP-011 (Script Refinement) → vytvoří v4, v5...
```

---

### Kontroly Kvality (Sprint 3)

**Smyčka 5: Grammar Review (MVP-014)**
```
Script → Grammar Check
    ↓
PASS → MVP-015 (Tone)
FAIL → MVP-011 (Script Refinement) → oprava → MVP-013 → MVP-014
```

**Smyčka 6: Tone Review (MVP-015)**
```
Script → Tone Check
    ↓
PASS → MVP-016 (Content)
FAIL → MVP-011 → MVP-013 → MVP-014 → MVP-015
```

**Smyčka 7: Content Review (MVP-016)**
```
Script → Content Check (logic, plot, character, pacing)
    ↓
PASS → MVP-017 (Consistency)
FAIL → MVP-011 → MVP-013 → ... → MVP-016
```

**Smyčka 8: Consistency Review (MVP-017)**
```
Script → Consistency Check (character names, timeline, locations)
    ↓
PASS → MVP-018 (Editing)
FAIL → MVP-011 → MVP-013 → ... → MVP-017
```

**Smyčka 9: Editing Review (MVP-018)**
```
Script → Editing Check (clarity, redundancy, structure)
    ↓
PASS → MVP-019 (Title Readability)
FAIL → MVP-011 → MVP-013 → ... → MVP-018
```

---

### Čitelnost (Sprint 3)

**Smyčka 10: Title Readability (MVP-019)**
```
Title → Readability Check (voiceover, pronunciation, length)
    ↓
PASS → MVP-020 (Script Readability)
FAIL → MVP-009 (Title Refinement) → MVP-012 → MVP-019
```

**Smyčka 11: Script Readability (MVP-020)**
```
Script → Readability Check (voiceover, flow, pacing)
    ↓
PASS → MVP-021 (Expert Review)
FAIL → MVP-011 → MVP-013 → ... → MVP-020
```

---

### Expertní Vybrušování (Sprint 3)

**Smyčka 12: Expert Review & Polish (MVP-021/022)**
```
Title + Script → Expert Review (GPT-based)
    ↓
READY → MVP-023 (Export)
NEEDS IMPROVEMENT → MVP-022 (Polish) → MVP-021 (cyklus)
```

---

## Klíčové Vlastnosti Workflow

### 1. Dynamické Verzování (DŮLEŽITÉ!)
- ⚠️ **Verze NEJSOU fixní na konkrétní MVP kroky**
- ⚠️ **Při každé změně titulku nebo skriptu se číslo verze automaticky zvýší o 1**
- ⚠️ **MVP-002 nevytváří vždy "v1"** - pokud už existují předchozí verze, vytvoří vyšší číslo
- ⚠️ **Příklady v tomto dokumentu (v1, v2, v3) jsou pouze ilustrativní**
- Podporuje neomezený počet verzí (v1, v2, v3... v50, v100...)
- Vždy používá nejnovější verze v smyčkách
- Verze nezávisí na MVP čísle, ale na historii změn

**Příklad:**
- První běh: Idea → Title (v1) → Script (v1)
- Po 5 iteracích: Title (v6), Script (v7)
- Po 15 iteracích: Title (v12), Script (v18)
- **Čísla verzí rostou podle počtu změn, ne podle MVP kroků!**

### 2. Kontext
- Všechny revize mají přístup k původnímu Idea
- Verze jsou propojeny (v2 odkazuje na v1, v3 na v2, atd.)
- Historie revizí zachována

### 3. Kvalitní Brány
- Přísné prahové hodnoty (85% pro Grammar, 80% pro Consistency, atd.)
- Critical issues způsobí automatické selhání
- Multiple high-severity issues způsobí selhání

### 4. Zpětnovazební Smyčky
- Každá brána může vrátit zpět k vybrušování
- Smyčky vždy procházejí akceptační brány znovu
- Zajišťuje kvalitu na každé úrovni

### 5. Křížová Validace
- Titulek validován proti skriptu
- Skript validován proti titulku
- Oba validovány proti původnímu nápadu

---

## Verzování - Jak Funguje

### ⚠️ DŮLEŽITÉ: Verze jsou Dynamické, Ne Fixní!

**Klíčové principy:**
1. **Každá změna titulku = verze +1** (Title v1 → v2 → v3 → v4...)
2. **Každá změna skriptu = verze +1** (Script v1 → v2 → v3 → v4...)
3. **Verze NEJSOU vázány na MVP kroky** - MVP-002 může vytvořit v1, v5 nebo v20 podle historie
4. **Čísla verzí v příkladech níže jsou pouze ilustrativní** - ukazují typ změny, ne skutečné číslo

### Příklad Scénáře s Více Iteracemi (Ilustrativní Čísla Verzí):

**POZNÁMKA:** Toto je pouze jeden možný scénář. Ve skutečnosti mohou být čísla verzí úplně jiná podle počtu iterací!

```
START:
Idea → Title (první verze) → Script (první verze)

Sprint 1:
Review Title by Script → feedback
Review Script by Title → feedback

Sprint 2:
Title (první) + feedback → Title (druhá verze)
Script (první) + feedback + Title (druhá) → Script (druhá verze)

Review Title (druhá) by Script (druhá) → feedback
Title (druhá) + feedback → Title (třetí verze)

Review Script (druhá) by Title (třetí) → feedback
Script (druhá) + feedback + Title (třetí) → Script (třetí verze)

Sprint 3 - Akceptace:
Title (třetí) → Acceptance Check → FAIL (skóre 82, potřebuje 85)
  ↓
Title (třetí) + feedback → Title (čtvrtá verze - Refinement)
Title (čtvrtá) → Acceptance Check → PASS ✅

Script (třetí) → Acceptance Check → FAIL (skóre 83)
  ↓
Script (třetí) + feedback + Title (čtvrtá) → Script (čtvrtá verze - Refinement)
Script (čtvrtá) → Acceptance Check → PASS ✅

Sprint 3 - Kontroly Kvality:
Script (čtvrtá) → Grammar → PASS ✅
Script (čtvrtá) → Tone → PASS ✅
Script (čtvrtá) → Content → FAIL (plot issues)
  ↓
Script (čtvrtá) + feedback + Title (čtvrtá) → Script (pátá verze - Refinement)
Script (pátá) → Acceptance → PASS
Script (pátá) → Grammar → PASS
Script (pátá) → Tone → PASS
Script (pátá) → Content → PASS ✅

Script (pátá) → Consistency → PASS ✅
Script (pátá) → Editing → PASS ✅

Title (čtvrtá) → Readability → PASS ✅
Script (pátá) → Readability → PASS ✅

Sprint 3 - Expert:
Title (čtvrtá) + Script (pátá) → Expert Review → NEEDS IMPROVEMENT
  ↓
Title (čtvrtá) + Script (pátá) + expert feedback → Polish → Title (pátá verze) + Script (šestá verze)
Title (pátá) + Script (šestá) → Expert Review → READY ✅

Publikování:
Title (pátá) + Script (šestá) → Export → JSON, MD, HTML ✅
Export result → Report Generation → Complete Report ✅

FINÁLNÍ VERZE: Title (pátá verze), Script (šestá verze)

⚠️ POZNÁMKA: V reálném scénáři mohou být čísla verzí úplně jiná!
Např.: Title v23, Script v35 - závisí na počtu iterací!
```

### Další Možné Scénáře (Ilustrativní):

**Scénář A: Méně iterací**
- Finální: Title (druhá verze), Script (třetí verze)
- Workflow byl rychlejší, méně oprav

**Scénář B: Více iterací**
- Finální: Title (desátá verze), Script (patnáctá verze)
- Více zpětných vazeb, více vylepšení

**Scénář C: Velmi složitý projekt**
- Finální: Title (dvacátá verze), Script (třicátá verze)
- Mnoho iterací, komplexní obsah

**KLÍČ: Čísla verzí jsou výsledkem procesu, ne předem dané!**

---

## Statistiky Workflow

### Sprint 1: 5 stavů (MVP-001 až MVP-005)
- Vytvoření základu
- První verze titulku a skriptu (čísla závisí na historii)
- Počáteční křížové revize

### Sprint 2: 6 stavů (MVP-006 až MVP-011)
- Iterativní vylepšování
- Další verze titulku a skriptu (inkrementují se podle změn)
- Křížová validace vylepšení

### Sprint 3: 13 stavů (MVP-012 až MVP-024)
- 2 akceptační brány
- 7 kontrol kvality
- 2 kontroly čitelnosti
- 2 expertní stavy
- 2 publikační stavy

### Celkem:
- **24 MVPs**
- **12 zpětnovazebních smyček**
- **Dynamické verzování** - čísla verzí se inkrementují při každé změně
- **Neomezený počet verzí** - může být v1, v2... v50, v100, atd.
- **100% pokrytí testy** (všechny MVPs testovány)
- 2 publikační stavy

### Celkem:
- **24 MVPs**
- **12 zpětnovazebních smyček**
- **Neomezený počet verzí**
- **100% pokrytí testy** (všechny MVPs testovány)

---

## Závěr

Tento workflow zajišťuje:
- ✅ Vysoká kvalita obsahu díky více kontrolním vrstvám
- ✅ Iterativní vylepšování s verzováním
- ✅ Křížová validace titulku a skriptu
- ✅ Explicitní akceptační brány
- ✅ Komplexní kontroly kvality (Grammar, Tone, Content, Consistency, Editing)
- ✅ Kontroly čitelnosti pro voiceover
- ✅ GPT expertní revize a vybrušování
- ✅ Export do více formátů
- ✅ Detailní reportování

**Stav**: Všech 24 MVPs implementováno a otestováno ✅  
**Datum dokončení**: 2025-11-22  
**Připraveno pro**: Produkční použití a Post-MVP rozšíření
