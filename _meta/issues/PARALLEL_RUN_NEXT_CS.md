# PARALLEL_RUN_NEXT - Provádění MVP sprintu (Iterativní společné vylepšování)

**Sprint**: Sprint 1-3 (6 týdnů) - MVP iterativní workflow  
**Datum**: 2025-11-21  
**Stav**: Plánování  
**Cíl**: Vybudovat MVP s **iterativním cyklem společného vylepšování titulku a skriptu** následující: **Nápad → Titulek v1 → Skript v1 → Křížové revize → Titulek v2 ← Skript v2 → Revize v2 → Vylepšení v3 → Brány přijetí → Kontroly čitelnosti → Publikovat**

---

## Vylepšený přístup MVP

### Proč iterativní společné vylepšování?
- **Vyšší kvalita**: Titulek a skript validovány proti sobě navzájem
- **Koherentní výstup**: Změny jednoho elementu spouštějí re-validaci druhého
- **Explicitní brány**: Kontroly přijetí před pokračováním
- **Finální validace**: Kontroly čitelnosti zajišťují kvalitu publikování
- **Kompromis**: +2 týdny (6 vs 4) pro výrazně lepší kvalitu

### Iterativní workflow společného vylepšování (16 fází)

**Reference**: Viz `T/TITLE_SCRIPT_WORKFLOW.md` a `MVP_WORKFLOW.md` pro kompletní dokumentaci.

**Iterativní cesta** (16 fází s cykly vzájemně závislého vylepšování):

```
1. PrismQ.T.Idea.Creation
       ↓
2. PrismQ.T.Title.Draft (v1) ← z Nápadu
       ↓
3. PrismQ.T.Script.Draft (v1) ← z Nápadu + Titulku v1
       ↓
4. PrismQ.T.Rewiew.Title.ByScript ← Revize Titulku v1 podle Skriptu v1 + Nápadu
       ↓
5. PrismQ.T.Rewiew.Script.ByTitle ← Revize Skriptu v1 podle Titulku v1 + Nápadu
       ↓
6. PrismQ.T.Title.Improvements (v2) ← Použití revizí + titulek v1, skript v1
       ↓
7. PrismQ.T.Script.Improvements (v2) ← Použití revizí + nový titulek v2, skript v1
       ↓
8. PrismQ.T.Rewiew.Title.ByScript (v2) ←──────────┐
       ↓                                           │
9. PrismQ.T.Title.Refinement (v3)                 │
       ↓                                           │
10. PrismQ.T.Rewiew.Script.ByTitle (v2) ←─────┐   │
        ↓                                      │   │
11. PrismQ.T.Script.Refinement (v3)            │   │
        ↓                                      │   │
12. Kontrola přijetí titulku ─NE─────────────────┘   │
        ↓ ANO                                      │
13. Kontrola přijetí skriptu ─NE────────────────────┘
        ↓ ANO
14. PrismQ.T.Rewiew.Title.Readability (Voiceover) ←──────┐
        ↓                                                │
        ├─SELHÁNÍ─→ Návrat ke kroku 9 ──────────────────────┘
        ↓ ÚSPĚCH
15. PrismQ.T.Rewiew.Script.Readability (Voiceover) ←─────┐
        ↓                                                 │
        ├─SELHÁNÍ─→ Návrat ke kroku 11 ─────────────────────┘
        ↓ ÚSPĚCH
16. PrismQ.T.Publishing.Finalization
```

**Klíčové inovace**:
- **Vzájemně závislé vylepšování**: Titulek revidován podle kontextu skriptu, skript podle titulku
- **Sledování verzí**: v1 (počáteční), v2 (první vylepšení), v3+ (vybrušování - může dosáhnout v4, v5, v6, v7, atd.)
- **Explicitní brány přijetí**: Musí projít kontrolami před pokračováním (kroky 12-13)
- **Finální validace čitelnosti**: Zajišťuje kvalitu publikování (kroky 14-15)
- **Zachování kontextu**: Původní verze uchovány pro referenci po celou dobu
- **Princip nejnovější verze**: Všechny smyčky používají nejnovější/poslední verzi titulku a skriptu, ne pevně zakódované verze

**Cesty ke složkám:**
- `T/Idea/Creation/` - Vytváření nápadu
- `T/Title/Draft/` - Návrh titulku v1
- `T/Script/Draft/` - Návrh skriptu v1
- `T/Rewiew/Idea/` - Revize titulku (kroky 4, 8, 12, 14)
- `T/Rewiew/Script/` - Revize skriptu (kroky 5, 10, 13, 15)
- `T/Title/Improvements/` - Vylepšení titulku v2 (krok 6)
- `T/Script/Improvements/` - Vylepšení skriptu v2 + vybrušování v3 (kroky 7, 11)
- `T/Title/Refinement/` - Vybrušování titulku v3+ (krok 9)
- `T/Rewiew/Readability/` - Validace čitelnosti (kroky 14-15)
- `T/Publishing/Finalization/` - Publikování (krok 16)

---

## Sprint 1: Počáteční návrhy + křížové revize (Týdny 1-2)

### Týden 1: Základy - Počáteční návrhy

**Cíl**: Nápad → Titulek v1 → Skript v1 vytvořen  
**Aktivní workeři**: 3

| Worker | Issue | Úsilí | Popis |
|--------|-------|--------|-------------|
| **Worker02** | #MVP-001 | 2d | Vytváření nápadu |
| **Worker13** | #MVP-002 | 2d | Návrh titulku v1 (z Nápadu) |
| **Worker02** | #MVP-003 | 3d | Návrh skriptu v1 (z Nápadu + Titulku v1) |
| **Worker15** | Dokumentace | 2d | Dokumentace MVP workflow |
| **Worker04** | Nastavení testů | 2d | Testovací framework pro iterativní workflow |

**Příkazy**:
```
Worker02: Implementovat #MVP-001 v T/Idea/Creation/
- Modul: PrismQ.T.Idea.Creation
- Závislosti: Žádné
- Priorita: Kritická
- Úsilí: 2 dny
- Výstup: Základní zachycení a uložení nápadu

Worker13: Implementovat #MVP-002 v T/Title/Draft/
- Modul: PrismQ.T.Title.Draft
- Závislosti: #MVP-001 (může začít paralelně)
- Priorita: Kritická
- Úsilí: 2 dny
- Výstup: Generovat 3-5 variant titulku (v1) pouze z nápadu

Worker02: Implementovat #MVP-003 v T/Script/Draft/
- Modul: PrismQ.T.Script.Draft
- Závislosti: #MVP-002
- Priorita: Kritická
- Úsilí: 3 dny
- Výstup: Generovat počáteční skript (v1) z nápadu + titulku v1
```

**Výstup týdne 1**: ✅ Pipeline Nápad → Titulek v1 → Skript v1 funguje

---

### Týden 2: Cyklus křížové revize

**Cíl**: Titulek a skript revidovány v kontextu toho druhého  
**Aktivní workeři**: 2

| Worker | Issue | Úsilí | Popis |
|--------|-------|--------|-------------|
| **Worker10** | #MVP-004 | 1d | Revize titulku podle skriptu a nápadu |
| **Worker10** | #MVP-005 | 1d | Revize skriptu podle titulku a nápadu |

**Příkazy**:
```
Worker10: Implementovat #MVP-004 v T/Rewiew/Idea/
- Modul: PrismQ.T.Rewiew.Title.ByScript
- Závislosti: #MVP-003 (potřeba titulku v1 i skriptu v1)
- Priorita: Kritická
- Úsilí: 1 den
- Výstup: Revidovat titulek v1 proti skriptu v1 a nápadu - generovat zpětnou vazbu

Worker10: Implementovat #MVP-005 v T/Rewiew/Script/
- Modul: PrismQ.T.Rewiew.Script.ByTitle
- Závislosti: #MVP-003
- Priorita: Kritická
- Úsilí: 1 den
- Výstup: Revidovat skript v1 proti titulku v1 a nápadu - generovat zpětnou vazbu
```

**Výstup týdne 2**: ✅ Křížově validační revize pro titulek i skript dokončeny

---

## Sprint 2: Cyklus vylepšování v2 + vybrušování v3 (Týdny 3-4)

### Týden 3: Generování verzí v2 s křížovým kontextem

**Cíl**: Vytvořit vylepšené verze v2 pomocí křížových revizí  
**Aktivní workeři**: 3

| Worker | Issue | Úsilí | Popis |
|--------|-------|--------|-------------|
| **Worker13** | #MVP-006 | 2d | Vylepšení titulku v2 (použití obou revizí + titulek v1, skript v1) |
| **Worker02** | #MVP-007 | 2d | Vylepšení skriptu v2 (použití obou revizí + nový titulek v2, skript v1) |
| **Worker10** | #MVP-008 | 1d | Revize titulku v2 (revize titulku v2 podle skriptu v2) |

**Příkazy**:
```
Worker13: Implementovat #MVP-006 v T/Title/Improvements/
- Modul: PrismQ.T.Title.Improvements
- Závislosti: #MVP-004, #MVP-005 (potřeba obou revizí)
- Priorita: Kritická
- Úsilí: 2 dny
- Výstup: Generovat titulek v2 pomocí:
  - Zpětná vazba revize titulku (krok 4)
  - Zpětná vazba revize skriptu (krok 5)
  - Titulek v1
  - Skript v1

Worker02: Implementovat #MVP-007 v T/Script/Improvements/
- Modul: PrismQ.T.Script.Improvements
- Závislosti: #MVP-006 (potřebuje nový titulek v2)
- Priorita: Kritická
- Úsilí: 2 dny
- Výstup: Generovat skript v2 pomocí:
  - Zpětná vazba revize skriptu (krok 5)
  - Zpětná vazba revize titulku (krok 4)
  - Skript v1
  - **Nový titulek v2** (z kroku 6)

Worker10: Implementovat #MVP-008 v T/Rewiew/Idea/
- Modul: PrismQ.T.Rewiew.Title.ByScript (v2)
- Závislosti: #MVP-007 (potřeba obou verzí v2)
- Priorita: Kritická
- Úsilí: 1 den
- Výstup: Revidovat titulek v2 proti skriptu v2 - generovat zpětnou vazbu
```

**Výstup týdne 3**: ✅ Titulek v2 a skript v2 generovány s křížovým kontextem, titulek v2 revidován

---

### Týden 4: Vybrušování na v3

**Cíl**: Vybrousit titulek i skript na v3 na základě revizí v2  
**Aktivní workeři**: 3

| Worker | Issue | Úsilí | Popis |
|--------|-------|--------|-------------|
| **Worker13** | #MVP-009 | 1d | Vybrušování titulku v3 (na základě revize v2) |
| **Worker10** | #MVP-010 | 1d | Revize skriptu v2 podle titulku v3 |
| **Worker02** | #MVP-011 | 2d | Vybrušování skriptu v3 (na základě revize + titulku v3) |

**Příkazy**:
```
Worker13: Implementovat #MVP-009 v T/Title/Refinement/
- Modul: PrismQ.T.Title.Refinement
- Závislosti: #MVP-008 (potřeba zpětné vazby revize v2)
- Priorita: Kritická
- Úsilí: 1 den
- Výstup: Vybrousit titulek z v2 na v3 pomocí zpětné vazby z kroku 8

Worker10: Implementovat #MVP-010 v T/Rewiew/Script/
- Modul: PrismQ.T.Rewiew.Script.ByTitle (v2)
- Závislosti: #MVP-009 (potřeba titulku v3)
- Priorita: Kritická
- Úsilí: 1 den
- Výstup: Revidovat skript v2 proti nejnovějšímu titulku v3 - generovat zpětnou vazbu

Worker02: Implementovat #MVP-011 v T/Script/Improvements/
- Modul: PrismQ.T.Script.Refinement
- Závislosti: #MVP-010
- Priorita: Kritická
- Úsilí: 2 dny
- Výstup: Vybrousit skript z v2 na v3 pomocí zpětné vazby + zajistit sladění s titulkem v3
```

**Výstup týdne 4**: ✅ Titulek v3 a skript v3 vybroušeny a připraveny pro brány přijetí

---

## Sprint 3: Validace a publikování (Týdny 5-6)

### Týden 5: Brány přijetí + kontroly čitelnosti

**Cíl**: Validovat kvalitu prostřednictvím bran přijetí a kontrol čitelnosti  
**Aktivní workeři**: 2-3

| Worker | Issue | Úsilí | Popis |
|--------|-------|--------|-------------|
| **Worker10** | #MVP-012 | 0.5d | Brána přijetí titulku |
| **Worker10** | #MVP-013 | 0.5d | Brána přijetí skriptu |
| **Worker10** | #MVP-014 | 0.5d | Revize čitelnosti titulku |
| **Worker10** | #MVP-015 | 0.5d | Revize čitelnosti/hlasu skriptu |
| **Worker04** | E2E testy | 3d | Test všech cest včetně smyček |

**Příkazy**:
```
Worker10: Implementovat #MVP-012 v T/Rewiew/Idea/
- Modul: PrismQ.T.Rewiew.Title.Acceptance
- Závislosti: #MVP-011 (potřeba nejnovější verze titulku)
- Priorita: Kritická
- Úsilí: 0.5 dne
- Výstup: Kontrola přijetí titulku (nejnovější verze - v3, v4, v5, v6, v7, atd.)
  - Pokud PŘIJATO: pokračovat na #MVP-013
  - Pokud NEPŘIJATO: smyčka zpět na #MVP-008 (revize nejnovější verze → vybrousit na další verzi)
  - **Vždy používá nejnovější verzi titulku**

Worker10: Implementovat #MVP-013 v T/Rewiew/Script/
- Modul: PrismQ.T.Rewiew.Script.Acceptance
- Závislosti: #MVP-012 (titulek musí být přijat jako první)
- Priorita: Kritická
- Úsilí: 0.5 dne
- Výstup: Kontrola přijetí skriptu (nejnovější verze - v3, v4, v5, v6, v7, atd.)
  - Pokud PŘIJATO: pokračovat na #MVP-014
  - Pokud NEPŘIJATO: smyčka zpět na #MVP-010 (revize nejnovější verze → vybrousit na další verzi)
  - **Vždy používá nejnovější verzi skriptu**

Worker10: Implementovat #MVP-014 v T/Rewiew/Readability/
- Modul: PrismQ.T.Rewiew.Title.Readability
- Závislosti: #MVP-013 (oba musí být přijaty)
- Priorita: Kritická
- Úsilí: 0.5 dne
- Výstup: Kontrola čitelnosti titulku (přijatá verze - nejnovější)
  - Pokud PROJDE: pokračovat na #MVP-015
  - Pokud SELŽE: návrat na #MVP-009 (vybrousit se zpětnou vazbou čitelnosti - vytvoří další verzi)
  - **Používá nejnovější přijatý titulek**

Worker10: Implementovat #MVP-015 v T/Rewiew/Readability/
- Modul: PrismQ.T.Rewiew.Script.Readability
- Závislosti: #MVP-014 (čitelnost titulku prošla)
- Priorita: Kritická
- Úsilí: 0.5 dne
- Výstup: Kontrola čitelnosti/hlasu skriptu (přijatá verze - nejnovější)
  - Pokud PROJDE: pokračovat na #MVP-016
  - Pokud SELŽE: návrat na #MVP-011 (vybrousit se zpětnou vazbou čitelnosti - vytvoří další verzi)
  - **Používá nejnovější přijatý skript**

Worker04: Dokončit E2E testování se všemi iteračními cestami
- Závislosti: Všechny MVP vlastnosti
- Priorita: Vysoká
- Úsilí: 3 dny
- Výstup: Plná sada testů pokrývající:
  - Šťastnou cestu (vše projde napoprvé)
  - Smyčku přijetí titulku (selže jednou, pak projde)
  - Smyčku přijetí skriptu (selže jednou, pak projde)
  - Smyčky čitelnosti (titulek selže, skript selže)
  - Více iterací (v4, v5, v6, v7, v8, atd. - test že číslování verzí funguje správně)
  - **Ověřit, že ve smyčkách se vždy používají nejnovější verze**
```

**Výstup týdne 5**: ✅ Všechny brány přijetí a kontroly čitelnosti implementovány + testovány

**Rezerva**: Týden 5 umožňuje čas na iterační smyčky, pokud kontroly přijetí selžou při testování

---

### Týden 6: Publikování + finální validace

**Cíl**: End-to-end tok kompletní s publikovaným obsahem  
**Aktivní workeři**: 3

| Worker | Issue | Úsilí | Popis |
|--------|-------|--------|-------------|
| **Worker02** | #MVP-016 | 2d | Publikování |
| **Worker15** | Uživatelská příručka | 2d | Kompletní dokumentace s příklady iterací |
| **Worker04** | Finální validace | 2d | Validace všech scénářů funguje správně |

**Příkazy**:
```
Worker02: Implementovat #MVP-016 v T/Publishing/Finalization/
- Modul: PrismQ.T.Publishing.Finalization
- Závislosti: #MVP-015 (všechny kontroly prošly)
- Priorita: Kritická
- Úsilí: 2 dny
- Výstup: Publikovat schválený + validovaný obsah
  - Označit jako "publikováno"
  - Export do výstupního formátu
  - Uložit publikovanou verzi se všemi verzemi sledovanými

Worker15: Dokončit uživatelskou příručku s dokumentací iteračních smyček
- Závislosti: Všechny MVP vlastnosti
- Priorita: Vysoká
- Úsilí: 2 dny
- Výstup: Kompletní dokumentace včetně:
  - Jak pracovat se zpětnou vazbou revize
  - Jak fungují iterační smyčky
  - Příklady selhání bran přijetí
  - Jak spustit re-kontroly čitelnosti
  - Vysvětlení sledování verzí (v1, v2, v3, v4, v5, v6, v7, atd.)
  - **Důležité**: Objasnit, že smyčky vždy používají nejnovější verze, ne pevně zakódované v3

Worker04: Finální MVP validace všech cest
- Závislosti: Všechny MVP vlastnosti
- Priorita: Vysoká
- Úsilí: 2 dny
- Výstup: Validovat, že:
  - Šťastná cesta funguje (žádné smyčky)
  - Všechny smyčkové cesty fungují (brány přijetí, čitelnost)
  - Sledování verzí funguje správně
  - Publikovaný obsah obsahuje správné finální verze
```

**Výstup týdne 6**: ✅ Kompletní MVP s iterativním workflow společného vylepšování plně funkční

---

## Souhrn MVP issues

| Issue | Modul | Fáze | Worker | Úsilí | Popis |
|-------|--------|-------|--------|--------|-------------|
| #MVP-001 | PrismQ.T.Idea.Creation | Nápad | Worker02 | 2d | Základní zachycení nápadu |
| #MVP-002 | PrismQ.T.Title.Draft | Titulek v1 | Worker13 | 2d | Generování titulku z nápadu |
| #MVP-003 | PrismQ.T.Script.Draft | Skript v1 | Worker02 | 3d | Generování skriptu z nápadu + titulku v1 |
| #MVP-004 | PrismQ.T.Rewiew.Title.ByScript | **Revize titulku podle skriptu** | Worker10 | 1d | Revize titulku v1 proti skriptu v1 + nápadu |
| #MVP-005 | PrismQ.T.Rewiew.Script.ByTitle | **Revize skriptu podle titulku** | Worker10 | 1d | Revize skriptu v1 proti titulku v1 + nápadu |
| #MVP-006 | PrismQ.T.Title.Improvements | Titulek v2 | Worker13 | 2d | Titulek v2 použitím křížových revizí + titulek v1, skript v1 |
| #MVP-007 | PrismQ.T.Script.Improvements | Skript v2 | Worker02 | 2d | Skript v2 použitím křížových revizí + nový titulek v2, skript v1 |
| #MVP-008 | PrismQ.T.Rewiew.Title.ByScript | **Revize titulku v2** | Worker10 | 1d | Revize titulku v2 proti skriptu v2 |
| #MVP-009 | PrismQ.T.Title.Refinement | Titulek v3+ | Worker13 | 1d | Vybrousit titulek na v3, v4, v5, v6, v7, atd. (nejnovější verze) |
| #MVP-010 | PrismQ.T.Rewiew.Script.ByTitle | **Revize skriptu v2+** | Worker10 | 1d | Revize skriptu (nejnovější) proti titulku (nejnovější) |
| #MVP-011 | PrismQ.T.Script.Refinement | Skript v3+ | Worker02 | 2d | Vybrousit skript na v3, v4, v5, v6, v7, atd. (nejnovější verze) |
| #MVP-012 | PrismQ.T.Rewiew.Title.Acceptance | **Brána přijetí** | Worker10 | 0.5d | Zkontrolovat, zda je titulek (nejnovější verze) přijat (smyčka pokud ne) |
| #MVP-013 | PrismQ.T.Rewiew.Script.Acceptance | **Brána přijetí** | Worker10 | 0.5d | Zkontrolovat, zda je skript (nejnovější verze) přijat (smyčka pokud ne) |
| #MVP-014 | PrismQ.T.Rewiew.Title.Readability | **Kontrola čitelnosti** | Worker10 | 0.5d | Finální validace čitelnosti/hlasu titulku |
| #MVP-015 | PrismQ.T.Rewiew.Script.Readability | **Kontrola čitelnosti** | Worker10 | 0.5d | Finální validace čitelnosti/hlasu skriptu |
| #MVP-016 | PrismQ.T.Publishing.Finalization | Publikovat | Worker02 | 2d | Publikování schváleného + validovaného obsahu |

**Celkem**: 16 issues, 20 dní práce, 6 týdnů kalendářního času s 3-4 workery

**Klíčové vlastnosti**:
- **Vzájemně závislé vylepšování**: Titulek a skript revidovány proti sobě navzájem (kroky 4-5, 8, 10)
- **Sledování verzí**: v1 (počáteční), v2 (vylepšené), v3+ (vybroušené - může dosáhnout v4, v5, v6, v7, atd.)
- **Explicitní brány přijetí**: Musí projít před pokračováním (kroky 12-13)
- **Finální validace čitelnosti**: Zajišťuje kvalitu publikování (kroky 14-15)
- **Iterační smyčky**: Návrat k vybrušování pokud selže přijetí/čitelnost
- **Princip nejnovější verze**: Všechny smyčky vždy používají nejnovější/poslední verzi titulku a skriptu

**Cesty ke složkám:**
- `T/Idea/Creation/` (krok 1)
- `T/Title/Draft/` (krok 2)
- `T/Script/Draft/` (krok 3)
- `T/Rewiew/Idea/` (kroky 4, 8, 12, 14)
- `T/Rewiew/Script/` (kroky 5, 10, 13, 15)
- `T/Title/Improvements/` (krok 6)
- `T/Script/Improvements/` (kroky 7, 11)
- `T/Title/Refinement/` (krok 9)
- `T/Rewiew/Readability/` (kroky 14-15)
- `T/Publishing/Finalization/` (krok 16)

---

## Stavový automat workflow (Iterativní společné vylepšování)

```
[*] --> VytváříníNápadu
VytváříníNápadu --> NávrhTitulku_v1: Krok 1-2
NávrhTitulku_v1 --> NávrhSkriptu_v1: Krok 2-3
NávrhSkriptu_v1 --> RevizeTitulku_v1: Krok 3-4 (revize titulku podle kontextu skriptu)
RevizeTitulku_v1 --> RevizeSkriptu_v1: Krok 4-5 (revize skriptu podle kontextu titulku)
RevizeSkriptu_v1 --> VylepšeníTitulku_v2: Krok 5-6 (použít obě revize + titulek v1, skript v1)
VylepšeníTitulku_v2 --> VylepšeníSkriptu_v2: Krok 6-7 (použít revize + nový titulek v2, skript v1)
VylepšeníSkriptu_v2 --> RevizeTitulku_v2: Krok 7-8 (revize titulku v2 podle skriptu v2)
RevizeTitulku_v2 --> VybroušeníTitulku_v3: Krok 8-9
VybroušeníTitulku_v3 --> RevizeSkriptu_v2: Krok 9-10 (revize skriptu v2 podle titulku v3)
RevizeSkriptu_v2 --> VybroušeníSkriptu_v3: Krok 10-11
VybroušeníSkriptu_v3 --> PřijetíTitulku: Krok 11-12
PřijetíTitulku --> RevizeTitulku_v2: NEPŘIJATO (smyčka na krok 8)
PřijetíTitulku --> PřijetíSkriptu: PŘIJATO (krok 12-13)
PřijetíSkriptu --> RevizeSkriptu_v2: NEPŘIJATO (smyčka na krok 10)
PřijetíSkriptu --> ČitelnostTitulku: PŘIJATO (krok 13-14)
ČitelnostTitulku --> VybroušeníTitulku_v3: SELŽE (smyčka na krok 9)
ČitelnostTitulku --> ČitelnostSkriptu: PROJDE (krok 14-15)
ČitelnostSkriptu --> VybroušeníSkriptu_v3: SELŽE (smyčka na krok 11)
ČitelnostSkriptu --> Publikování: PROJDE (krok 15-16)
Publikování --> [*]
```

**Cesty smyček**:
- **Smyčka přijetí titulku**: Kroky 12 → 8 → 9 → 10 → 11 → 12 (dokud není přijato) - verze se zvyšují: v3 → v4 → v5 → v6 → v7, atd.
- **Smyčka přijetí skriptu**: Kroky 13 → 10 → 11 → 13 (dokud není přijato) - verze se zvyšují: v3 → v4 → v5 → v6 → v7, atd.
- **Smyčka čitelnosti titulku**: Kroky 14 → 9 → ... → 14 (dokud neprojde) - vytváří další verzi pokaždé
- **Smyčka čitelnosti skriptu**: Kroky 15 → 11 → ... → 15 (dokud neprojde) - vytváří další verzi pokaždé
- **Důležité**: Všechny smyčky používají nejnovější/poslední verzi titulku a skriptu, ne pevně zakódované verze

---

## Metriky úspěchu

### Kritéria dokončení MVP
- ✅ Všech 16 MVP issues implementováno
- ✅ End-to-end workflow testován se všemi iteračními cestami
- ✅ Alespoň jeden obsah publikován přes celý workflow
- ✅ Všechny smyčkové scénáře validovány (brány přijetí + čitelnost)
- ✅ Dokumentace kompletní s příklady iterací

### Standardy kvality
- **Křížová validace**: Titulek a skript revidovány proti sobě navzájem v každé fázi
- **Iterativní vybrušování**: Více cyklů vylepšení zajišťuje vysokou kvalitu
- **Explicitní brány**: Kontroly přijetí zajišťují splnění standardů před pokračováním
- **Finální validace**: Kontroly čitelnosti zajišťují kvalitu připravenou k publikování
- **Sledování verzí**: Všechny verze (v1, v2, v3+) sledovány a uchovávány
- **Pokrytí testy**: >85% pro MVP vlastnosti včetně všech smyčkových cest

---

## Porovnání: Jednoduché vs iterativní workflow

| Aspekt | Jednoduché (9 issues, 4 týdny) | **Iterativní (16 issues, 6 týdnů)** |
|--------|----------------------------|-------------------------------------|
| **Issues** | 9 | **16** |
| **Časový horizont** | 4 týdny | **6 týdnů** |
| **Workeři** | 3-4 | 3-4 |
| **Revize** | Jeden průchod na fázi | **Více průchodů křížové validace** |
| **Kvalita** | Základní | **Vysoká (společné vylepšování)** |
| **Přijetí** | Implikované | **Explicitní brány (kroky 12-13)** |
| **Čitelnost** | Žádná | **Finální validace (kroky 14-15)** |
| **Verze** | v1, v2 | **v1, v2, v3, v4+** |
| **Kontext** | Izolované revize | **Křížově validované (titulek ↔ skript)** |
| **Smyčky** | Jednoduchá zpětná vazba | **4 typy smyček (přijetí + čitelnost)** |

**Kompromis**: +2 týdny (+50%) pro výrazně vyšší kvalitu prostřednictvím iterativního společného vylepšování s explicitními validačními bránami.

---

## Roadmapa po MVP

Viz soubory `ISSUE_PLAN_T_*.md` pro kompletní plány vlastností (celkem 120 issues), které budou přidány po validaci iterativního workflow společného vylepšování MVP.

### Fáze 2 (Po MVP)
- AI-poháněné návrhy vylepšení v každé fázi
- Automatizované hodnocení kvality pro revize
- SEO optimalizace pro titulek a obsah
- Publikování na více platformách

### Fáze 3 (Budoucnost)
- A/B testovací framework
- Integrace analytiky
- Kolaborativní vlastnosti (více recenzentů)
- Dávkové zpracování se sledováním iterací

---

## Související dokumenty

- **MVP_WORKFLOW.md**: Detailní MVP plánování se všemi 16 issues specifikacemi a iteračními smyčkami
- **MVP_WORKFLOW_SIMPLE.md**: Původní jednoduché 9-issue workflow (záložní reference)
- **PARALLEL_RUN_NEXT_FULL.md**: Plný 120-issue plán pro po-MVP
- **ISSUE_PLAN_T_*.md**: Komplexní plány vlastností pro každý modul
- **Worker*/README.md**: Definice rolí workerů

---

**Stav**: Připraveno pro MVP Sprint 1  
**Další akce**: Worker01 vytvořit 16 MVP issues v GitHub s specifikacemi iteračních smyček  
**Časový horizont**: 6 týdnů k vysoce kvalitnímu MVP s iterativním společným vylepšováním  
**Přístup**: Kvalitně zaměřený iterativní vývoj s explicitními validačními bránami

**Klíčová inovace**: Vylepšení titulku a skriptu jsou vzájemně závislá a křížově validovaná v každé iteraci, zajišťující koherentní vysoce kvalitní výstup.

---

**Vlastník**: Worker01  
**Vytvořeno**: 2025-11-21  
**Naposledy aktualizováno**: 2025-11-21  
**Zaměření**: Iterativní workflow společného vylepšování: Nápad → Titulek v1 ← Skript v1 → Křížové revize → Vylepšení v2 → Vybrušování v3 → Brány přijetí → Validace čitelnosti → Publikovat
