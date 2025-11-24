# MVP Workflow - Plán minimálního životaschopného produktu

> **⚠️ UPOZORNĚNÍ**: Pro aktuální a kompletní specifikaci viz:
> - **PARALLEL_RUN_NEXT_CS.md** - Aktuální dokument se všemi 22 MVP issues
> - **PARALLEL_RUN_NEXT.md** - Anglická verze
> - **MVP_WORKFLOW_SIMPLE.md** - Anglická verze zjednodušeného workflow
>
> Tento dokument popisuje základní zjednodušené workflow. Pro rozšířené workflow s 22 fázemi včetně AI kontrol kvality a finální revize viz výše uvedené dokumenty.

**Vytvořeno**: 2025-11-21  
**Aktualizováno**: 2025-11-22  
**Stav**: Základní workflow - Pro úplnou specifikaci viz PARALLEL_RUN_NEXT_CS.md  
**Přístup**: Vylepšený iterativní vývoj MVP s kontrolami kvality

**Aktuální stav projektu**:
- Sprint 1: DOKONČENO ✅ (7/7 issues)
- Sprint 2: DOKONČENO ✅ (6/6 issues) 
- Sprint 3: PROBÍHÁ ⚠️ (5/11 issues dokončeno)
- Celkem: 16/22 MVP issues dokončeno (73%)

---

## Přehled MVP workflow

Tento dokument definuje **Minimální životaschopný produkt (MVP)** workflow pro Text (T) pipeline, se zaměřením na zjednodušený, iterativní přístup k tvorbě obsahu.

**Reference**: Viz `T/TITLE_SCRIPT_WORKFLOW.md` pro kompletní detailní dokumentaci workflow.

### Sekvence MVP workflow

**Používání skutečných názvů složek se zpětnovazebními smyčkami:**

```
PrismQ.T.Idea.Creation (Vytváření nápadu)
    ↓
PrismQ.T.Title.FromIdea (Návrh titulku)
    ↓
PrismQ.T.Review.Title (Revize titulku) ←────┐
    ↓                                         │
    ├─→ Pokud jsou potřeba změny ────────────┘
    ↓ (Označit jako připraveno)
PrismQ.T.Script.FromIdeaAndTitle (Návrh skriptu)
    ↓
PrismQ.T.Review.Script (Revize skriptu) ←──┐
    ↓                                       │
    ├─→ Pokud jsou potřeba změny → T.Script.Improvements ─┘
    ↓ (Označit jako připraveno)
PrismQ.T.Review.Content (Finální revize obsahu) ←─┐
    ↓                                              │
    ├─→ Pokud jsou potřeba změny → T.Script.Improvements ─┘
    │   (nebo zpět na T.Title.Refinement pokud titulek potřebuje aktualizaci)
    ↓ (Označit jako připraveno)
PrismQ.T.Publishing.Finalization (Finalizace publikování)
```

**Detaily zpětnovazebních smyček:**

1. **Smyčka revize titulku**: 
   - Title.Draft → Review.Title
   - Pokud jsou potřeba změny: návrat na Title.Draft
   - Pokud připraveno: pokračovat na Script.Draft

2. **Smyčka revize skriptu**:
   - Script.Draft → Review.Script
   - Pokud jsou potřeba změny: Script.Improvements → Review.Script (smyčka)
   - Pokud připraveno: pokračovat na Review.Content

3. **Smyčka finální revize obsahu**:
   - Review.Content reviduje skript i titulek společně
   - Pokud jsou potřeba změny skriptu: Script.Improvements → Review.Content (smyčka)
   - Pokud jsou potřeba změny titulku: Title.Refinement → Review.Content (smyčka)
   - Pokud připraveno: pokračovat na Publishing.Finalization

**Vztah k plnému workflow:**

MVP zjednodušuje plné workflow dokumentované v `T/TITLE_SCRIPT_WORKFLOW.md`:
- **Složený stav Idea** (Creation → Outline → Skeleton → Title) je zjednodušen na:
  - MVP: Přímá cesta Creation → Title.Draft (přeskočení Outline & Skeleton pro MVP)
  - Po-MVP: Přidat fáze Idea.Outline a Idea.Skeleton
- **Fáze revizí** nyní zahrnují explicitní zpětnovazební smyčky:
  - Revize titulku (nová explicitní fáze)
  - Revize skriptu se zpětnovazební smyčkou
  - Revize obsahu se zpětnovazebními smyčkami pro skript i titulek
- **Vylepšení skriptu** odpovídá iterativnímu cyklu Script.Draft → Revize
- **Publikování** používá `T/Publishing/Finalization` s SEO moduly

**Struktura složek:**
- `T/Idea/Creation/` - Vytváření a zachycení nápadu
- `T/Title/FromIdea/` - Generování titulku
- `T/Review/Idea/` - Revize titulku (reviduje kvalitu titulku)
- `T/Script/FromIdeaAndTitle/` - Tvorba návrhu skriptu
- `T/Review/Script/` - Revize skriptu (reviduje kvalitu skriptu)
- `T/Script/Improvements/` - Vylepšení skriptu
- `T/Title/Refinement/` - Vybrušování titulku
- `T/Review/Content/` - Finální revize obsahu (skript + titulek společně)
- `T/Publishing/Finalization/` - Publikování

---

## Filosofie MVP

### Klíčové principy
1. **Začít jednoduše**: Vybudovat nejprve minimální funkční vlastnosti
2. **Iterativní vylepšování**: Více cyklů revizí a vylepšení
3. **Sekvenční tok**: Jasný postup přes stavy
4. **Rychlá zpětná vazba**: Rychlé iterační smyčky
5. **Inkrementální hodnota**: Každá fáze přidává hodnotu

### MVP vs plná sada vlastností
- **MVP**: Základní workflow, které produkuje publikovatelný obsah
- **Plné vlastnosti**: Pokročilé vlastnosti přidány po validaci workflow MVP
- **Zaměření**: Rychlost k prvnímu publikovanému obsahu

### Zjednodušení MVP z plného workflow

Na základě `T/TITLE_SCRIPT_WORKFLOW.md`, MVP zjednodušuje:

1. **Složený stav Idea**:
   - Plné: Idea.Creation → Idea.Outline → Idea.Skeleton → Idea.Title
   - MVP: Idea.Creation → Title.Draft (přímá cesta)
   - Odloženo: Fáze Idea.Outline a Idea.Skeleton

2. **Fáze revizí**:
   - Plné: Více revizních modulů (Gramatika, Čitelnost, Tón, Obsah, Konzistence, Editace)
   - MVP: ✅ **NYNÍ ZAHRNUTO** - Granulární dimenze revize po akceptačních branách (Fáze 14-20)
   - Revize kvality skriptu (Gramatika, Tón, Obsah, Konzistence, Editace) + Finální čitelnost

3. **Schválení skriptu**:
   - Plné: ScriptDraft → ScriptReview → ScriptApproved → TextPublishing
   - MVP: ScriptDraft → Revize → Vylepšení → Revize → Publikování
   - Odloženo: Formální stav "schváleno" s uzamčením verze

4. **Proces publikování**:
   - Plné: SEO (Klíčová slova, Tagy, Kategorie) + Finalizace
   - MVP: Pouze základní finalizace
   - Odloženo: Komplexní moduly SEO optimalizace

**Cesta vylepšení po MVP**:
Po validaci základního workflow MVP, rozšířit o:
- Vytváření Idea.Outline pro lepší strukturu
- Vývoj frameworku Idea.Skeleton
- Formální stavy schválení a uzamčení verzí
- Komplexní SEO optimalizace (T/Publishing/SEO s Keywords, Tags, Categories)
- Automatizované kontroly kvality
- Pokročilé analytiky revizí

---

## Fáze 1: MVP základní workflow (Sprint 1-2)

### Fáze 1: PrismQ.T.Idea.Creation
**Cíl**: Vytvořit základní nápad z inspirace  
**Složka**: `T/Idea/Creation/`  
**Vlastník**: Worker02, Worker12  
**Priorita**: Kritická  
**Časový horizont**: Sprint 1, Týden 1

#### MVP Issue: #MVP-001 - Základní vytváření nápadu
- **Worker**: Worker02 (Python)
- **Úsilí**: 2 dny
- **Modul**: PrismQ.T.Idea.Creation
- **Popis**: Vytvořit jednoduché zachycení a uložení nápadu
- **Akceptační kritéria**:
  - Vstup: Textový popis nápadu
  - Uložit nápad do databáze
  - Přiřadit unikátní ID
  - Základní validace (není prázdné)
  - CLI rozhraní pro testování

**Odloženo na po-MVP**:
- AI-poháněné rozšíření
- Inspirace z více zdrojů
- Hodnocení kvality
- Dávkové zpracování

---

### Fáze 2: PrismQ.T.Title.FromIdea
**Cíl**: Generovat počáteční varianty titulku  
**Složka**: `T/Title/FromIdea/`  
**Vlastník**: Worker12, Worker13  
**Priorita**: Kritická  
**Časový horizont**: Sprint 1, Týden 1

#### MVP Issue: #MVP-002 - Základní generátor titulků
- **Worker**: Worker13 (Mistr promptů)
- **Úsilí**: 2 dny
- **Modul**: PrismQ.T.Title.FromIdea
- **Popis**: Jednoduché generování titulků pomocí AI
- **Akceptační kritéria**:
  - Vstup: Objekt nápadu
  - Generovat 3-5 variant titulku
  - Základní šablona promptu
  - Uložit do databáze
  - Vrátit titulky jako seznam

**Odloženo na po-MVP**:
- SEO optimalizace
- A/B testování
- Varianty specifické pro platformy
- Sledování výkonu
- Pokročilé hodnocení

---

## MVP Issues souhrn

### Sprint 1 - Týden 1-2
| Issue | Modul | Fáze | Worker | Úsilí | Popis |
|-------|--------|-------|--------|--------|-------------|
| #MVP-001 | PrismQ.T.Idea.Creation | Nápad | Worker02 | 2d | Základní zachycení nápadu |
| #MVP-002 | PrismQ.T.Title.FromIdea | Titulek | Worker13 | 2d | Generování titulku |
| #MVP-003 | PrismQ.T.Review.Idea | Revize titulku | Worker10 | 1d | Revize titulku se zpětnou vazbou |
| #MVP-004 | PrismQ.T.Script.FromIdeaAndTitle | Skript | Worker02 | 3d | Generování skriptu |
| #MVP-005 | PrismQ.T.Review.Script | Revize skriptu | Worker10 | 1d | Revize skriptu se zpětnou vazbou |
| #MVP-006 | PrismQ.T.Script.Improvements | Vylepšení | Worker02 | 2d | Vylepšení skriptu |
| #MVP-007 | PrismQ.T.Review.Content | Finální revize | Worker10 | 1d | Finální revize obsahu |
| #MVP-008 | PrismQ.T.Publishing.Finalization | Publikování | Worker02 | 2d | Publikování obsahu |
| #MVP-009A | PrismQ.T.Review.Script.Grammar | Revize gramatiky | Worker10 | 0.5d | Kontrola gramatiky skriptu |
| #MVP-009B | PrismQ.T.Review.Script.Tone | Revize tónu | Worker10 | 0.5d | Kontrola tónu skriptu |
| #MVP-009C | PrismQ.T.Review.Script.Content | Revize obsahu | Worker10 | 0.5d | Kontrola logiky obsahu |
| #MVP-009D | PrismQ.T.Review.Script.Consistency | Revize konzistence | Worker10 | 0.5d | Kontrola konzistence skriptu |
| #MVP-009E | PrismQ.T.Review.Script.Editing | Revize editace | Worker10 | 0.5d | Kontrola jasnosti a plynulosti |
| #MVP-009F | PrismQ.T.Review.Title.Readability | Revize čitelnosti titulku | Worker10 | 0.5d | Kontrola čitelnosti titulku |
| #MVP-009G | PrismQ.T.Review.Script.Readability | Revize čitelnosti skriptu | Worker10 | 0.5d | Kontrola voiceover čitelnosti |
| #MVP-010A | PrismQ.T.Story.ExpertReview | GPT expertní revize | Worker10 | 0.5d | GPT-based expertní revize příběhu |
| #MVP-010B | PrismQ.T.Story.ExpertPolish | GPT expertní leštění | Worker10 | 0.5d | GPT-based expertní vylepšení |
| #MVP-011 | PrismQ.T.Publishing.Finalization | Publikování | Worker02 | 2d | Publikování obsahu |

**Celkem**: 18 issues (8 hlavních + 7 revizí kvality + 2 GPT expertní + publikování), přibližně 19 dní práce, 4-5 týdnů kalendářního času s 3-4 workery

**Poznámka**: Revize kvality (09A-09G) jsou lokální AI. GPT expertní revize (10A-10B) používají GPT-4/GPT-5 pro finální profesionální leštění.

---

## Metriky úspěchu

### Kritéria dokončení MVP
- ✅ Všechny MVP issues implementovány (základní + revize kvality + GPT expertní)
- ✅ End-to-end workflow testován včetně všech revizí
- ✅ Alespoň jeden obsah publikován přes celý workflow
- ✅ Všechny zpětnovazební smyčky validovány
- ✅ Všechny fáze revizí kvality (Gramatika, Tón, Obsah, Konzistence, Editace, Čitelnost) funkční
- ✅ GPT expertní revize a leštění funkční
- ✅ Dokumentace kompletní

### Standardy kvality
- **Zpětnovazební smyčky**: Jasné cesty pro revize a vylepšení
- **Iterativní vylepšování**: Více cyklů před finální publikací
- **Revize kvality (Lokální AI)**: Profesionální kontrola přes všechny dimenze (Gramatika → Tón → Obsah → Konzistence → Editace → Čitelnost)
- **GPT Expertní smyčka**: Finální profesionální leštění pomocí GPT-4/GPT-5
- **Dvoustupňová kvalita**: Efektivní lokální AI pro většinu vylepšení, prémiové GPT pro finální leštění
- **Pokrytí testy**: >80% pro MVP vlastnosti
- **Dokumentace**: Jasný průvodce pro každou fázi

---

## Cesta po MVP

Po úspěšné validaci MVP přidat:

### Fáze 2: Rozšířené vlastnosti Idea
- Idea.Outline s AI generováním struktury
- Idea.Skeleton s frameworkem obsahu
- Integrace více zdrojů (YouTube, Spotify, JustWatch)
- Hodnocení kvality nápadů

### Fáze 3: Pokročilé revize
- Granulární revizní moduly (Gramatika, Čitelnost, Tón)
- Automatizované kontroly kvality
- Formální stavy schválení
- Uzamčení verzí

### Fáze 4: SEO a publikování
- Optimalizace klíčových slov
- Generování tagů a kategorií
- Publikování na více platformách
- Integrace analytiky

---

## Související dokumenty

- **[MVP_WORKFLOW.md](./MVP_WORKFLOW.md)** - Detailní MVP workflow s kompletními specifikacemi
- **[PARALLEL_RUN_NEXT_CS.md](./PARALLEL_RUN_NEXT_CS.md)** - Plán provádění sprintu s přiřazením workerů
- **[WORKFLOW_CS.md](../WORKFLOW_CS.md)** - Kompletní dokumentace stavového automatu

---

**Stav**: Připraveno pro MVP Sprint 1  
**Další akce**: Worker01 vytvořit 8 MVP issues v GitHub  
**Časový horizont**: 4 týdny k základnímu MVP  
**Přístup**: Jednoduchý, iterativní vývoj se zpětnovazebními smyčkami

---

**Vlastník**: Worker01  
**Vytvořeno**: 2025-11-21  
**Naposledy aktualizováno**: 2025-11-21  
**Zaměření**: Jednoduché MVP workflow s jasným postupem a zpětnovazebními smyčkami pro kvalitu

---

**Poznámka**: Pro úplné detaily všech issues, akceptačních kritérií a implementačních specifikací, prosím referujte na [anglickou verzi MVP_WORKFLOW_SIMPLE.md](./MVP_WORKFLOW_SIMPLE.md).
