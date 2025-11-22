# PARALLEL_RUN_NEXT - Provádění MVP sprintu

> **Poznámka**: Toto je zjednodušený dokument zaměřený na sprinty obsahující pouze sprinty a příkazy.  
> **Plná detailní verze**: Viz `PARALLEL_RUN_NEXT_FULL_CS.md` pro kompletní vysvětlení workflow.  
> **Aktuální stav**: Viz `CURRENT_STATE.md` pro hodnocení stavu implementace.

**Sprint**: Sprint 1-3 (7-8 týdnů) - Vývoj MVP  
**Datum**: 2025-11-22  
**Stav**: Sprint 1 probíhá  
**Cíl**: Vybudovat MVP s 26-fázovým iterativním workflow společného vylepšování

---

## Sprint 1: Základy a křížové revize (Týdny 1-2)

**Cíl**: Nápad → Titulek v1 → Skript v1 → Křížové validační revize  
**Časový horizont**: 2 týdny  
**Aktivní workeři**: Worker02, Worker10, Worker13, Worker15, Worker04

---

### Týden 1: Základy - Počáteční návrhy

**Výstup**: ✅ Pipeline Nápad → Titulek v1 → Skript v1 funguje

#### Příkazy

```bash
# MVP-001: Vytváření nápadu (2 dny) - DOKONČENO ✓
Worker02: Implementovat PrismQ.T.Idea.Creation v T/Idea/Creation/
- Modul: PrismQ.T.Idea.Creation
- Závislosti: Žádné
- Priorita: Kritická
- Úsilí: 2 dny
- Stav: HOTOVO ✓
- Kritéria přijetí:
  * Základní zachycení a uložení nápadu funguje
  * Nápady lze vytvořit z uživatelského vstupu
  * Nápady lze načíst podle ID
  * Data uložena do databáze
  * Testy: Vytvoření, načtení, výpis nápadů

# MVP-002: Generování titulku (2 dny) - DOKONČENO ✓
Worker13: Implementovat PrismQ.T.Title.FromIdea v T/Title/FromIdea/
- Modul: PrismQ.T.Title.FromIdea
- Závislosti: MVP-001 (může začít paralelně)
- Priorita: Kritická
- Úsilí: 2 dny
- Stav: HOTOVO ✓
- Kritéria přijetí:
  * Generovat 3-5 variant titulku z nápadu
  * Každá varianta obsahuje zdůvodnění
  * Titulky jsou poutavé a přesné
  * Výsledky uloženy s odkazem na nápad
  * Testy: Generování titulků ze vzorových nápadů

# MVP-003: Generování skriptu (3 dny) - DOKONČENO ✓
Worker02: Implementovat PrismQ.T.Script.FromIdeaAndTitle v T/Script/FromIdeaAndTitle/
- Modul: PrismQ.T.Script.FromIdeaAndTitle
- Závislosti: MVP-002
- Priorita: Kritická
- Úsilí: 3 dny
- Stav: HOTOVO ✓
- Kritéria přijetí:
  * Generovat skript z nápadu + titulku v1
  * Skript obsahuje narativní strukturu
  * Skript je v souladu s titulkem a nápadem
  * Výsledky uloženy s odkazy
  * Testy: Generování skriptů ze vzorových dvojic nápad+titulek

# Dokumentace (2 dny)
Worker15: Vytvořit dokumentaci MVP workflow
- Modul: Dokumentace
- Závislosti: MVP-001, MVP-002, MVP-003
- Priorita: Vysoká
- Úsilí: 2 dny
- Výstup: Kompletní dokumentace workflow s příklady
- Kritéria přijetí:
  * Dokumentovat všech 26 fází workflow
  * Zahrnout příklady použití
  * Dokumentovat iterační smyčky
  * Kompletní API reference

# Nastavení testů (2 dny)
Worker04: Nastavit testovací framework pro iterativní workflow
- Modul: Testovací infrastruktura
- Závislosti: MVP-001, MVP-002, MVP-003
- Priorita: Vysoká
- Úsilí: 2 dny
- Výstup: Testovací framework podporující iterační cesty
- Kritéria přijetí:
  * Nakonfigurován unit test framework
  * Podpora integračních testů
  * Testovací pomocníci pro sledování verzí
  * Nakonfigurován CI/CD pipeline
```

---

### Týden 2: Cyklus křížové revize

**Výstup**: ✅ Křížově validační revize pro titulek i skript dokončeny

#### Příkazy

```bash
# MVP-004: Revize titulku podle skriptu (1 den) - PROBÍHÁ ~
Worker10: Implementovat PrismQ.T.Review.Title.ByScript v T/Review/Title/ByScriptAndIdea/
- Modul: PrismQ.T.Review.Title.ByScript
- Závislosti: MVP-003 (potřeba titulku v1 i skriptu v1)
- Priorita: Kritická
- Úsilí: 1 den
- Stav: ČÁSTEČNÉ - VYŽADUJE VALIDACI
- Kritéria přijetí:
  * Revidovat titulek v1 proti skriptu v1 a nápadu
  * Generovat strukturovanou zpětnou vazbu (sladění, jasnost, poutavost)
  * Identifikovat nesrovnalosti mezi titulkem a skriptem
  * Navrhnout vylepšení titulku
  * Výstup JSON formát s kategoriemi zpětné vazby
  * Testy: Revize vzorových dvojic titulek/skript

# MVP-005: Revize skriptu podle titulku (1 den) - NEZAHÁJENO ❌
Worker10: Implementovat PrismQ.T.Review.Script.ByTitle v T/Review/Script/
- Modul: PrismQ.T.Review.Script.ByTitle
- Závislosti: MVP-003
- Priorita: Kritická
- Úsilí: 1 den
- Stav: NEZAHÁJENO
- Kritéria přijetí:
  * Revidovat skript v1 proti titulku v1 a nápadu
  * Generovat strukturovanou zpětnou vazbu (sladění, tok, úplnost)
  * Identifikovat mezery mezi obsahem skriptu a slibem titulku
  * Navrhnout vylepšení skriptu
  * Výstup JSON formát s kategoriemi zpětné vazby
  * Testy: Revize vzorových dvojic skript/titulek
```

---

## Sprint 2: Cyklus vylepšování (Týdny 3-4)

**Cíl**: Vytvořit vylepšené verze v2 pomocí křížových revizí, pak vybrousit na v3  
**Časový horizont**: 2 týdny  
**Aktivní workeři**: Worker02, Worker10, Worker13

---

### Týden 3: Generování verzí v2

**Výstup**: ✅ Titulek v2 a skript v2 generovány s křížovým kontextem

#### Příkazy

```bash
# MVP-006: Vylepšení titulku v2 (2 dny)
Worker13: Implementovat PrismQ.T.Title.Improvements v T/Title/Improvements/
- Modul: PrismQ.T.Title.Improvements
- Závislosti: MVP-004, MVP-005 (potřeba obou revizí)
- Priorita: Kritická
- Úsilí: 2 dny
- Stav: NEZAHÁJENO
- Kritéria přijetí:
  * Generovat titulek v2 pomocí zpětné vazby z obou revizí
  * Použít titulek v1, skript v1 a obě zpětné vazby z revizí
  * Zachovat poutavost při zlepšování sladění
  * Uložit v2 s odkazem na v1
  * Testy: Ověřit, že v2 řeší zpětnou vazbu z revizí v1

# MVP-007: Vylepšení skriptu v2 (2 dny)
Worker02: Implementovat PrismQ.T.Script.Improvements v T/Script/Improvements/
- Modul: PrismQ.T.Script.Improvements
- Závislosti: MVP-006 (potřebuje nový titulek v2)
- Priorita: Kritická
- Úsilí: 2 dny
- Stav: NEZAHÁJENO
- Kritéria přijetí:
  * Generovat skript v2 pomocí obou revizí + nového titulku v2
  * Zlepšit sladění s titulkem v2
  * Řešit zpětnou vazbu z revize skriptu
  * Uložit v2 s odkazem na v1
  * Testy: Ověřit, že v2 řeší zpětnou vazbu a je v souladu s titulkem v2

# MVP-008: Revize titulku v2 (1 den)
Worker10: Implementovat PrismQ.T.Review.Title.ByScript (v2) v T/Review/Title/
- Modul: PrismQ.T.Review.Title.ByScript
- Závislosti: MVP-007 (potřeba obou verzí v2)
- Priorita: Kritická
- Úsilí: 1 den
- Stav: NEZAHÁJENO
- Kritéria přijetí:
  * Revidovat titulek v2 proti skriptu v2
  * Generovat zpětnou vazbu pro vybrušování
  * Porovnat vylepšení z v1 na v2
  * Výstup JSON formát se zpětnou vazbou
  * Testy: Revize vzorových dvojic v2 titulek/skript
```

---

### Týden 4: Vybrušování na v3

**Výstup**: ✅ Titulek v3 a skript v3 vybroušeny a připraveny pro brány přijetí

#### Příkazy

```bash
# MVP-009: Vybrušování titulku v3 (1 den)
Worker13: Implementovat PrismQ.T.Title.Refinement v T/Title/Refinement/
- Modul: PrismQ.T.Title.Refinement
- Závislosti: MVP-008 (potřeba zpětné vazby revize v2)
- Priorita: Kritická
- Úsilí: 1 den
- Stav: NEZAHÁJENO
- Kritéria přijetí:
  * Vybrousit titulek z v2 na v3 pomocí zpětné vazby
  * Vylepšit jasnost a poutavost
  * Uložit v3 s odkazem na v2
  * Podporovat verzování (v3, v4, v5, v6, v7, atd.)
  * Testy: Ověřit, že v3 zahrnuje zpětnou vazbu v2

# MVP-010: Revize skriptu v2 podle titulku v3 (1 den)
Worker10: Implementovat PrismQ.T.Review.Script.ByTitle (v2) v T/Review/Script/
- Modul: PrismQ.T.Review.Script.ByTitle
- Závislosti: MVP-009 (potřeba titulku v3)
- Priorita: Kritická
- Úsilí: 1 den
- Stav: NEZAHÁJENO
- Kritéria přijetí:
  * Revidovat skript v2 proti nejnovějšímu titulku v3
  * Generovat zpětnou vazbu pro vybrušování
  * Zkontrolovat sladění s aktualizovaným titulkem
  * Výstup JSON formát se zpětnou vazbou
  * Testy: Revize skriptu v2 proti titulku v3

# MVP-011: Vybrušování skriptu v3 (2 dny)
Worker02: Implementovat PrismQ.T.Script.Refinement v T/Script/Improvements/
- Modul: PrismQ.T.Script.Refinement
- Závislosti: MVP-010
- Priorita: Kritická
- Úsilí: 2 dny
- Stav: NEZAHÁJENO
- Kritéria přijetí:
  * Vybrousit skript z v2 na v3 pomocí zpětné vazby
  * Zajistit sladění s titulkem v3
  * Vylepšit narativní tok
  * Uložit v3 s odkazem na v2
  * Podporovat verzování (v3, v4, v5, v6, v7, atd.)
  * Testy: Ověřit, že v3 zahrnuje zpětnou vazbu a je v souladu s titulkem v3
```

---

## Sprint 3: Validace a kvalita (Týdny 5-8)

**Cíl**: Brány přijetí + komplexní kontroly kvality + GPT expert review + publikování  
**Časový horizont**: 4 týdny  
**Aktivní workeři**: Worker02, Worker10, Worker04, Worker15

---

### Týden 5: Brány přijetí + kontroly kvality (část 1)

**Výstup**: ✅ Brány přijetí prošly + kontroly Grammar, Tone, Content dokončeny

#### Příkazy

```bash
# MVP-012: Brána přijetí titulku (0.5 dne)
Worker10: Implementovat PrismQ.T.Review.Title.Acceptance v T/Review/Title/
- Modul: PrismQ.T.Review.Title.Acceptance
- Závislosti: MVP-011 (potřeba nejnovější verze titulku)
- Priorita: Kritická
- Úsilí: 0.5 dne
- Stav: NEZAHÁJENO
- Kritéria přijetí:
  * Zkontrolovat, zda titulek (nejnovější verze) splňuje kritéria přijetí
  * Kritéria: jasnost, poutavost, sladění se skriptem
  * Pokud PŘIJATO: pokračovat na MVP-013
  * Pokud NEPŘIJATO: smyčka zpět na MVP-008 (revize → vybrousit na další verzi)
  * Vždy používá nejnovější verzi titulku
  * Testy: Testovat scénáře přijetí a odmítnutí

# MVP-013: Brána přijetí skriptu (0.5 dne)
Worker10: Implementovat PrismQ.T.Review.Script.Acceptance v T/Review/Script/
- Modul: PrismQ.T.Review.Script.Acceptance
- Závislosti: MVP-012 (titulek musí být přijat jako první)
- Priorita: Kritická
- Úsilí: 0.5 dne
- Stav: NEZAHÁJENO
- Kritéria přijetí:
  * Zkontrolovat, zda skript (nejnovější verze) splňuje kritéria přijetí
  * Kritéria: úplnost, koherence, sladění s titulkem
  * Pokud PŘIJATO: pokračovat na MVP-014
  * Pokud NEPŘIJATO: smyčka zpět na MVP-010 (revize → vybrousit na další verzi)
  * Vždy používá nejnovější verzi skriptu
  * Testy: Testovat scénáře přijetí a odmítnutí

# MVP-014: Kontrola gramatiky (0.5 dne)
Worker10: Implementovat PrismQ.T.Review.Script.Grammar v T/Review/Grammar/
- Modul: PrismQ.T.Review.Script.Grammar
- Závislosti: MVP-013 (skript musí být přijat)
- Priorita: Vysoká
- Úsilí: 0.5 dne
- Stav: NEZAHÁJENO
- Kritéria přijetí:
  * Zkontrolovat gramatiku, interpunkci, pravopis, syntaxi, čas
  * Generovat specifické opravy s odkazy na řádky
  * Pokud PROJDE: pokračovat na MVP-015
  * Pokud SELŽE: návrat k vybrušování skriptu se zpětnou vazbou
  * Výstup JSON s problémy a navrhovanými opravami
  * Testy: Testovat s gramaticky správnými a nesprávnými skripty

# MVP-015: Kontrola tónu (0.5 dne)
Worker10: Implementovat PrismQ.T.Review.Script.Tone v T/Review/Tone/
- Modul: PrismQ.T.Review.Script.Tone
- Závislosti: MVP-014 (gramatika musí projít)
- Priorita: Vysoká
- Úsilí: 0.5 dne
- Stav: NEZAHÁJENO
- Kritéria přijetí:
  * Zkontrolovat emocionální intenzitu, sladění stylu, konzistenci hlasu
  * Vyhodnotit přiměřenost tónu pro typ obsahu
  * Pokud PROJDE: pokračovat na MVP-016
  * Pokud SELŽE: návrat k vybrušování skriptu se zpětnou vazbou
  * Výstup JSON s analýzou tónu
  * Testy: Testovat s různými styly tónu

# MVP-016: Kontrola obsahu (0.5 dne)
Worker10: Implementovat PrismQ.T.Review.Script.Content v T/Review/Content/
- Modul: PrismQ.T.Review.Script.Content
- Závislosti: MVP-015 (tón musí projít)
- Priorita: Vysoká
- Úsilí: 0.5 dne
- Stav: NEZAHÁJENO
- Kritéria přijetí:
  * Zkontrolovat logické mezery, problémy zápletky, motivaci postav, tempo
  * Ověřit narativní koherenci
  * Pokud PROJDE: pokračovat na MVP-017
  * Pokud SELŽE: návrat k vybrušování skriptu se zpětnou vazbou
  * Výstup JSON s problémy obsahu
  * Testy: Testovat s koherentními a nekoherentními skripty
```

---

### Týden 6: Kontroly kvality (část 2) + čitelnost

**Výstup**: ✅ Všechny kontroly kvality + kontroly čitelnosti prošly

#### Příkazy

```bash
# MVP-017: Kontrola konzistence (0.5 dne)
Worker10: Implementovat PrismQ.T.Review.Script.Consistency v T/Review/Consistency/
- Modul: PrismQ.T.Review.Script.Consistency
- Závislosti: MVP-016 (obsah musí projít)
- Priorita: Vysoká
- Úsilí: 0.5 dne
- Stav: NEZAHÁJENO
- Kritéria přijetí:
  * Zkontrolovat jména postav, časovou osu, lokace, opakované detaily
  * Identifikovat vnitřní rozpory
  * Pokud PROJDE: pokračovat na MVP-018
  * Pokud SELŽE: návrat k vybrušování skriptu se zpětnou vazbou
  * Výstup JSON s problémy konzistence
  * Testy: Testovat s konzistentními a nekonzistentními skripty

# MVP-018: Kontrola editace (0.5 dne)
Worker10: Implementovat PrismQ.T.Review.Script.Editing v T/Review/Editing/
- Modul: PrismQ.T.Review.Script.Editing
- Závislosti: MVP-017 (konzistence musí projít)
- Priorita: Vysoká
- Úsilí: 0.5 dne
- Stav: NEZAHÁJENO
- Kritéria přijetí:
  * Přepisy vět, strukturální opravy, odstranění redundance
  * Zlepšit jasnost a tok
  * Pokud PROJDE: pokračovat na MVP-019
  * Pokud SELŽE: návrat k vybrušování skriptu se zpětnou vazbou
  * Výstup JSON s návrhy úprav
  * Testy: Testovat zlepšení kvality editace

# MVP-019: Kontrola čitelnosti titulku (0.5 dne)
Worker10: Implementovat PrismQ.T.Review.Title.Readability v T/Review/Readability/
- Modul: PrismQ.T.Review.Title.Readability
- Závislosti: MVP-018 (editace musí projít)
- Priorita: Vysoká
- Úsilí: 0.5 dne
- Stav: NEZAHÁJENO
- Kritéria přijetí:
  * Zkontrolovat jasnost, délku, poutavost pro voiceover
  * Vyhodnotit výslovnost a tok
  * Pokud PROJDE: pokračovat na MVP-020
  * Pokud SELŽE: návrat k vybrušování titulku se zpětnou vazbou
  * Výstup JSON se skóre čitelnosti a problémy
  * Testy: Testovat s čitelnými a obtížnými titulky

# MVP-020: Kontrola čitelnosti skriptu (0.5 dne)
Worker10: Implementovat PrismQ.T.Review.Script.Readability v T/Review/Readability/
- Modul: PrismQ.T.Review.Script.Readability
- Závislosti: MVP-019 (čitelnost titulku musí projít)
- Priorita: Vysoká
- Úsilí: 0.5 dne
- Stav: NEZAHÁJENO
- Kritéria přijetí:
  * Zkontrolovat přirozený tok, výslovnost, tempo pro voiceover
  * Identifikovat obtížné pasáže
  * Pokud PROJDE: pokračovat na MVP-021
  * Pokud SELŽE: návrat k vybrušování skriptu se zpětnou vazbou
  * Výstup JSON se skóre čitelnosti a problémy
  * Testy: Testovat s různými styly skriptů

# Testování cest kvality (2 dny)
Worker04: Testovat všechny cesty kontrol kvality
- Závislosti: MVP-017 až MVP-020
- Priorita: Vysoká
- Úsilí: 2 dny
- Stav: NEZAHÁJENO
- Výstup: Komplexní testovací sada pro kontroly kvality
- Kritéria přijetí:
  * Testovat všechny scénáře kontrol kvality
  * Testovat selhání jednotlivých kontrol a obnovení
  * Testovat více selhání v řadě
  * Testovat smyčku zpět k vybrušování a re-kontrole
  * Ověřit sledování verzí skrze smyčky
```

---

### Týden 7-8: GPT expert review + publikování

**Výstup**: ✅ Kompletní MVP s expert review a publikováním

#### Příkazy

```bash
# MVP-021: GPT expert story review (0.5 dne)
Worker10: Implementovat PrismQ.T.Story.ExpertReview v T/Story/ExpertReview/
- Modul: PrismQ.T.Story.ExpertReview
- Závislosti: MVP-020 (všechny kontroly kvality prošly)
- Priorita: Vysoká
- Úsilí: 0.5 dne
- Stav: NEZAHÁJENO
- Kritéria přijetí:
  * Holistické hodnocení pomocí GPT-4/GPT-5
  * Generovat strukturovanou zpětnou vazbu (JSON formát)
  * Vyhodnotit celkovou kvalitu a dopad
  * Pokud PŘIPRAVENO: pokračovat na MVP-023 (publikování)
  * Pokud VYŽADUJE VYLEPŠENÍ: pokračovat na MVP-022
  * Testy: Testovat integraci GPT a parsování zpětné vazby

# MVP-022: GPT expert story polish (0.5 dne)
Worker10: Implementovat PrismQ.T.Story.ExpertPolish v T/Story/ExpertPolish/
- Modul: PrismQ.T.Story.ExpertPolish
- Závislosti: MVP-021 (expert review s potřebou vylepšení)
- Priorita: Vysoká
- Úsilí: 0.5 dne
- Stav: NEZAHÁJENO
- Kritéria přijetí:
  * Aplikovat vylepšení založená na GPT
  * Chirurgické změny pro maximální dopad
  * Návrat na MVP-021 pro ověření (max 2 iterace)
  * Uložit vybroušenou verzi
  * Testy: Testovat aplikaci vybrušování a ověřovací smyčku

# MVP-023: Publikování (2 dny)
Worker02: Implementovat PrismQ.T.Publishing.Finalization v T/Publishing/Finalization/
- Modul: PrismQ.T.Publishing.Finalization
- Závislosti: MVP-021 (expert review připraven)
- Priorita: Kritická
- Úsilí: 2 dny
- Stav: NEZAHÁJENO
- Kritéria přijetí:
  * Označit obsah jako "publikovaný"
  * Export do výstupního formátu (JSON, Markdown, atd.)
  * Uložit publikovanou verzi se všemi sledovanými verzemi
  * Generovat zprávu o publikování
  * Testy: Testovat workflow publikování end-to-end

# E2E testování (2 dny)
Worker04: Dokončit end-to-end testování se všemi cestami
- Závislosti: Všechny MVP vlastnosti
- Priorita: Vysoká
- Úsilí: 2 dny
- Stav: NEZAHÁJENO
- Výstup: Plná E2E testovací sada
- Kritéria přijetí:
  * Testovat šťastnou cestu (vše projde napoprvé)
  * Testovat smyčky přijetí titulku/skriptu
  * Testovat selhání kontrol kvality a obnovení
  * Testovat smyčky čitelnosti
  * Testovat smyčku GPT expert review
  * Testovat více iterací (v4, v5, v6, v7, atd.)
  * Ověřit sledování verzí v celém workflow

# Finální dokumentace (2 dny)
Worker15: Dokončit uživatelskou příručku se všemi fázemi
- Závislosti: Všechny MVP vlastnosti
- Priorita: Vysoká
- Úsilí: 2 dny
- Stav: NEZAHÁJENO
- Výstup: Kompletní uživatelská dokumentace
- Kritéria přijetí:
  * Dokumentovat všech 26 fází workflow
  * Zahrnout kritéria kontrol kvality
  * Dokumentovat příklady iteračních smyček
  * Vysvětlit sledování verzí (v1-v7+)
  * Poskytnout příklady použití a tutoriály
```

---

## Standardy kvality issues

Všechny issues musí splňovat tato kritéria:

### Velikost
- **Malé**: Maximálně 0.5-2 dny úsilí
- **Zaměřené**: Jedna zodpovědnost na issue
- **Testovatelné**: Lze ověřit nezávisle

### Kritéria přijetí
- **Specifická**: Jasné, měřitelné výsledky
- **Kompletní**: Všechny požadavky uvedeny
- **Ověřitelné**: Testy mohou validovat úspěch

### Vstup/Výstup
- **Vstup**: Jasně definované datové struktury
- **Výstup**: Očekávané výsledky zdokumentovány
- **Příklady**: Vzorové vstupy a výstupy poskytnuty

### Závislosti
- **Explicitní**: Všechny závislosti uvedeny
- **Blokování**: Blokováno čím jasně uvedeno
- **Pořadí**: Sekvence provádění definována

### Testy
- **Unit testy**: Testovat jednotlivé komponenty
- **Integrační testy**: Testovat interakce komponent
- **E2E testy**: Testovat kompletní workflow

---

## Souhrn sprintů

### Sprint 1 (Týdny 1-2)
- **Issues**: MVP-001 až MVP-005 (5 issues)
- **Dokončeno**: MVP-001, MVP-002, MVP-003 (3 issues) ✓
- **Probíhá**: MVP-004 (částečně) ~
- **Nezahájeno**: MVP-005 (1 issue) ❌
- **Pokrok**: 60% dokončeno (3 z 5 hotovo)

### Sprint 2 (Týdny 3-4)
- **Issues**: MVP-006 až MVP-011 (6 issues)
- **Stav**: NEZAHÁJENO (blokováno MVP-005)
- **Závislosti**: Vyžaduje dokončení MVP-005

### Sprint 3 (Týdny 5-8)
- **Issues**: MVP-012 až MVP-023 (12 issues)
- **Stav**: NEZAHÁJENO (blokováno Sprintem 2)
- **Závislosti**: Vyžaduje dokončení všech issues Sprintu 2

### Celkově
- **Celkem issues**: 23 MVP issues
- **Dokončeno**: 3 issues (13%)
- **Zbývá**: 20 issues (87%)
- **Odhadovaný čas**: 24 dní práce, 7-8 týdnů kalendářního času

---

## Kritická cesta

```
MVP-004 (validace) → MVP-005 (implementace) → Sprint 2 → Sprint 3
        0.5 dne            1 den              2 týdny    4 týdny
```

**Aktuální bloker**: MVP-005 musí být dokončeno pro odblokování Sprintu 2

---

**Stav**: Sprint 1 Týden 2 (probíhá)  
**Další akce**: Worker10 dokončit validaci MVP-004 a implementaci MVP-005  
**Aktualizováno**: 2025-11-22  
**Vlastník**: Worker01
