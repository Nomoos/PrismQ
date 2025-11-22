# PARALLEL_RUN_NEXT - Provádění MVP sprintu

> **Poznámka**: Toto je zjednodušený dokument zaměřený na sprinty obsahující pouze sprinty a příkazy.  
> **Plná detailní verze**: Viz `PARALLEL_RUN_NEXT_FULL_CS.md` pro kompletní vysvětlení workflow.  
> **Aktuální stav**: Viz `CURRENT_STATE.md` pro hodnocení stavu implementace.  
> **Refaktorováno**: 2025-11-22 - Zjednodušeno na 22 issues (z 26 fází), aplikovány SOLID principy, zaměřeno na MVP

**Sprint**: Sprint 1-3 (7-8 týdnů) - Vývoj MVP  
**Datum**: 2025-11-22 (Aktualizováno)  
**Stav**: Sprint 1 Dokončen ✅ | Sprint 2 Dokončen ✅ | Sprint 3 Částečně (5/11)  
**Cíl**: Vybudovat MVP s 22-fázovým iterativním workflow společného vylepšování (zjednodušeno z 26)

**Úspěch Sprint 1**: Základy dokončeny - Nápad → Titulek v1 → Skript v1 → Křížové revize fungují ✅  
**Úspěch Sprint 2**: Cyklus vylepšování dokončen - generování v2 a v3 funguje ✅  
**Pokrok Sprint 3**: Brány přijetí + 3 kontroly kvality dokončeny (5/11 - 45%) ⚠️  
**Dokončené Issues**: MVP-001 až MVP-016 (16 issues) → revize v _meta/issues/done/  
**Zbývající**: MVP-017 až MVP-022 (6 issues) - Kontroly kvality, Čitelnost, Finální revize, Publikování

---

## Sprint 1: Základy a křížové revize (Týdny 1-2) ✅ DOKONČENO

**Cíl**: Nápad → Titulek v1 → Skript v1 → Křížové validační revize  
**Časový horizont**: 2 týdny  
**Aktivní workeři**: Worker02, Worker10, Worker13, Worker15, Worker04  
**Stav**: ✅ VŠECHNY ISSUES DOKONČENY (7/7)

### Dokončené Issues (Přesunuty do _meta/issues/done/)

Všechny Sprint 1 issues byly dokončeny, revidovány a přesunuty do adresáře done:

- ✅ **MVP-001**: T.Idea.Creation (Worker02) - Revize: `done/MVP-001-REVIEW.md`
- ✅ **MVP-002**: T.Title.FromIdea (Worker13) - Revize: `done/MVP-002-REVIEW.md`
- ✅ **MVP-003**: T.Script.FromIdeaAndTitle (Worker02) - Revize: `done/MVP-003-REVIEW.md`
- ✅ **MVP-004**: T.Review.Title.ByScript (Worker10) - Revize: `done/MVP-004-REVIEW.md`
- ✅ **MVP-005**: T.Review.Script.ByTitle (Worker10) - Revize: `done/MVP-005-REVIEW.md`
- ✅ **MVP-DOCS**: Dokumentace MVP Workflow (Worker15) - Revize: `done/MVP-DOCS-REVIEW.md`
- ✅ **MVP-TEST**: Testovací Framework (Worker04) - Revize: `done/MVP-TEST-REVIEW.md`

**Shrnutí úspěchů**:
- Základní pipeline funguje: Nápad → Titulek v1 → Skript v1
- Systém křížových revizí dokončen: Titulek ↔ Skript vzájemné revize
- Kompletní dokumentace (1033 řádků EN + 548 řádků CS)
- Testovací framework připraven (49/49 testů prochází, 100%)
- Všechna kritéria přijetí splněna
- Sprint 2 odblokován a připraven ke spuštění

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

# Dokumentace (2 dny) - DOKONČENO ✓
Worker15: Vytvořit dokumentaci MVP workflow
- Modul: Dokumentace
- Závislosti: MVP-001, MVP-002, MVP-003
- Priorita: Vysoká
- Úsilí: 2 dny
- Stav: HOTOVO ✓
- Výstup: Kompletní dokumentace workflow s příklady
- Dokončené soubory:
  * MVP_WORKFLOW_DOCUMENTATION.md (1033 řádků, EN)
  * MVP_WORKFLOW_DOCUMENTATION_CS.md (548 řádků, CS)
  * WORKFLOW.md a WORKFLOW_CS.md aktualizovány s křížovými odkazy
- Kritéria přijetí:
  * ✅ Dokumentovat všech 26 fází workflow
  * ✅ Zahrnout příklady použití (4 kompletní příklady)
  * ✅ Dokumentovat iterační smyčky (3 vzory smyček)
  * ✅ Kompletní API reference (Workflow, Idea, Title, Script, Review, Publication)

# Nastavení testů (2 dny) - DOKONČENO ✓
Worker04: Nastavit testovací framework pro iterativní workflow
- Modul: Testovací infrastruktura
- Závislosti: MVP-001, MVP-002, MVP-003
- Priorita: Vysoká
- Úsilí: 2 dny
- Stav: HOTOVO ✓
- Výstup: Testovací framework podporující iterační cesty
- Dokončené soubory:
  * pytest.ini (kořenová konfigurace s markery)
  * tests/helpers.py (VersionTracker, WorkflowStageValidator, IntegrationTestHelper)
  * tests/test_helpers.py (35 unit testů)
  * tests/test_integration_workflow.py (14 integračních testů)
  * tests/README.md (484 řádků API reference)
- Pokrytí testy: 49/49 testů prochází (100%)
- Kritéria přijetí:
  * ✅ Nakonfigurován unit test framework (pytest s markery)
  * ✅ Podpora integračních testů (14 integračních testů)
  * ✅ Testovací pomocníci pro sledování verzí (třída VersionTracker)
  * ✅ Kompletní testovací dokumentace (484-řádkové README)
```

---

### Týden 2: Cyklus křížové revize

**Výstup**: ✅ DOKONČENO - Křížově validační revize pro titulek i skript dokončeny

#### Příkazy

```bash
# MVP-004: Revize titulku podle skriptu (1 den) - DOKONČENO ✓
Worker10: Implementovat PrismQ.T.Review.Title.ByScript v T/Review/Title/ByScriptAndIdea/
- Modul: PrismQ.T.Review.Title.ByScript
- Závislosti: MVP-003 (potřeba titulku v1 i skriptu v1)
- Priorita: Kritická
- Úsilí: 1 den
- Stav: HOTOVO ✓
- Dokončené soubory:
  * T/Review/Title/ByScriptAndIdea/by_script_and_idea.py (700+ řádků)
  * T/Review/Title/ByScriptAndIdea/__init__.py
  * T/Review/Title/ByScriptAndIdea/_meta/tests/test_by_script_and_idea.py (34 testů)
  * T/Review/Title/ByScriptAndIdea/_meta/tests/test_acceptance_criteria.py (8 testů)
  * T/Review/Title/ByScriptAndIdea/README.md
- Pokrytí testy: 42/42 testů prochází (100%)
- Kritéria přijetí:
  * ✅ Revidovat titulek v1 proti skriptu v1 a nápadu
  * ✅ Generovat strukturovanou zpětnou vazbu (sladění, jasnost, poutavost, SEO)
  * ✅ Identifikovat nesrovnalosti mezi titulkem a skriptem (extrakce klíčových slov + filtrování stopwords)
  * ✅ Navrhnout vylepšení titulku (prioritizováno podle skóre dopadu)
  * ✅ Výstup JSON formát s kategoriemi zpětné vazby (serializace to_dict())
  * ✅ Testy: Revize vzorových dvojic titulek/skript (34 unit + 8 akceptačních testů)

# MVP-005: Revize skriptu podle titulku (1 den) - DOKONČENO ✓
Worker10: Implementovat PrismQ.T.Review.Script.ByTitle v T/Review/Script/ByTitle/
- Modul: PrismQ.T.Review.Script.ByTitle
- Závislosti: MVP-003
- Priorita: Kritická
- Úsilí: 1 den
- Stav: HOTOVO ✓
- Dokončené soubory:
  * T/Review/Script/ByTitle/script_review_by_title.py (hlavní logika)
  * T/Review/Script/ByTitle/__init__.py
  * T/Review/Script/ByTitle/_meta/tests/test_script_review_by_title.py (32 testů)
  * T/Review/Script/ByTitle/README.md
- Pokrytí testy: 32/32 testů prochází (100%)
- Kritéria přijetí:
  * ✅ Revidovat skript v1 proti titulku v1 a nápadu
  * ✅ Generovat strukturovanou zpětnou vazbu (sladění: titulek 25% + nápad 30%, kvalita obsahu 45%)
  * ✅ Identifikovat mezery mezi obsahem skriptu a slibem titulku (regex matching, filtrování stopwords)
  * ✅ Navrhnout vylepšení skriptu (prioritizováno podle odhadů dopadu)
  * ✅ Výstup JSON formát s kategoriemi zpětné vazby (ScriptReview.to_dict())
  * ✅ Testy: Revize vzorových dvojic skript/titulek (32 unit testů, všechny scénáře)
  * Testy: Revize vzorových dvojic skript/titulek
```

---

## Sprint 2: Cyklus vylepšování (Týdny 3-4) ✅ DOKONČENO

**Cíl**: Vytvořit vylepšené verze v2 pomocí křížových revizí, pak vybrousit na v3  
**Časový horizont**: 2 týdny  
**Aktivní workeři**: Worker02, Worker10, Worker13  
**Stav**: ✅ VŠECHNY ISSUES DOKONČENY (6/6)

### Dokončené Issues (Přesunuty do _meta/issues/done/)

Všechny Sprint 2 issues byly dokončeny a revidovány:

- ✅ **MVP-006**: Generování Titulku v2 (Worker13) - Revize: `done/MVP-006-REVIEW.md`
- ✅ **MVP-007**: Generování Skriptu v2 (Worker02) - Revize: `done/MVP-007-REVIEW.md`
- ✅ **MVP-008**: T.Review.Title.ByScript v2 (Worker10) - Revize: `done/MVP-008-REVIEW.md`
- ✅ **MVP-009**: Vybrušování Titulku v3 (Worker13) - Revize: `done/MVP-009-REVIEW.md`
- ✅ **MVP-010**: T.Review.Script.ByTitle v2 (Worker10) - Revize: `done/MVP-010-REVIEW.md`
- ✅ **MVP-011**: Vybrušování Skriptu v3 (Worker02) - Revize: `done/MVP-011-REVIEW.md`

**Shrnutí úspěchů**:
- Pipeline generování v2 dokončena: Titulek v2 + Skript v2
- Vybrušování v3 funguje: Titulek v3 + Skript v3
- Systém křížových revizí v2 funkční
- Iterační cyklus vylepšování (v1→v2→v3→v4+) ověřen
- Všechna kritéria přijetí splněna
- Sprint 3 odblokován

---

### Týden 3: Generování verzí v2

**Výstup**: ✅ Titulek v2 a skript v2 generovány s křížovým kontextem

#### Příkazy

```bash
# MVP-006: Vylepšení titulku v2 (2 dny)
Worker13: Implementovat PrismQ.T.Title.FromOriginalTitleAndReviewAndScript
- Modul: PrismQ.T.Title.FromOriginalTitleAndReviewAndScript
- Umístění: T/Title/FromOriginalTitleAndReviewAndScript/
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
Worker02: Implementovat PrismQ.T.Script.FromOriginalScriptAndReviewAndTitle
- Modul: PrismQ.T.Script.FromOriginalScriptAndReviewAndTitle
- Umístění: T/Script/FromOriginalScriptAndReviewAndTitle/
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
Worker13: Implementovat PrismQ.T.Title.FromOriginalTitleAndReviewAndScript (v3)
- Modul: PrismQ.T.Title.FromOriginalTitleAndReviewAndScript
- Umístění: T/Title/FromOriginalTitleAndReviewAndScript/ (stejný modul, zpracovává v2→v3→v4+)
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
Worker02: Implementovat PrismQ.T.Script.FromOriginalScriptAndReviewAndTitle (v3)
- Modul: PrismQ.T.Script.FromOriginalScriptAndReviewAndTitle
- Umístění: T/Script/FromOriginalScriptAndReviewAndTitle/ (stejný modul, zpracovává v2→v3→v4+)
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

## Sprint 3: Validace a kvalita (Týdny 5-8) ⚠️ ČÁSTEČNĚ (5/11 Dokončeno)

**Cíl**: Brány přijetí + komplexní kontroly kvality + finální revize + publikování  
**Časový horizont**: 4 týdny  
**Aktivní workeři**: Worker02, Worker10, Worker04, Worker15  
**Stav**: PROBÍHÁ - Brány přijetí + 3 kontroly kvality dokončeny

### Dokončené Issues (Přesunuty do _meta/issues/done/)

Sprint 3 issues dokončené dosud:

- ✅ **MVP-012**: T.Review.Title.Acceptance (Worker10) - Revize: `done/MVP-012-REVIEW.md`
- ✅ **MVP-013**: T.Review.Script.Acceptance (Worker10) - Revize: `done/MVP-013-REVIEW.md`
- ✅ **MVP-014**: T.Review.Script.Grammar (Worker10) - Revize: `done/MVP-014-REVIEW.md`
- ✅ **MVP-015**: T.Review.Script.Tone (Worker10) - Revize: `done/MVP-015-REVIEW.md`
- ✅ **MVP-016**: T.Review.Script.Content (Worker10) - Revize: `done/MVP-016-REVIEW.md` (sloučeno z main)

**Shrnutí úspěchů**:
- Systém bran přijetí funguje (titulek + skript)
- Kontrola gramatiky operační
- Kontrola tónu operační
- Kontrola obsahu operační (sloučeno z main)
- Implementována logika smyčky zpět
- 5 z 11 Sprint 3 issues dokončeno (45%)

---

### Zbývající práce Sprint 3 (6 issues)

#### Kontroly kvality (2 zbývající)

```bash
# MVP-017: Kontrola konzistence (0.5 dne) - NEZAHÁJENO ❌ (DALŠÍ PRIORITA)
Worker10: Implementovat PrismQ.T.Review.Script.Consistency v T/Review/Consistency/
- Modul: PrismQ.T.Review.Script.Consistency
- Závislosti: MVP-016 ✅ (obsah musí projít - DOKONČENO)
- Priorita: VYSOKÁ
- Úsilí: 0.5 dne
- Stav: NEZAHÁJENO
- Účel: Zkontrolovat jména postav, časovou osu, lokace, rozpory
- Kritéria přijetí:
  * Validovat konzistenci jmen postav v celém skriptu
  * Zkontrolovat časovou osu na logickou posloupnost a rozpory
  * Ověřit, že zmínky o lokacích jsou konzistentní
  * Detekovat opakované detaily a rozpory
  * Výstup JSON s nalezenými konkrétními problémy konzistence
  * Rozhodnutí Projde/Selže: PROJDE → MVP-018, SELŽE → smyčka vybrušování
  * Testy: Scénáře konzistentního a nekonzistentního skriptu

# MVP-018: Kontrola editace (0.5 dne) - NEZAHÁJENO ❌
Worker10: Implementovat PrismQ.T.Review.Script.Editing v T/Review/Editing/
- Modul: PrismQ.T.Review.Script.Editing
- Závislosti: MVP-017 (konzistence musí projít)
- Priorita: VYSOKÁ
- Úsilí: 0.5 dne
- Stav: NEZAHÁJENO
- Účel: Přepisy vět, strukturální opravy, odstranění redundance
- Kritéria přijetí:
  * Identifikovat věty vyžadující přepsání pro jasnost
  * Detekovat strukturální problémy v organizaci skriptu
  * Najít a označit redundantní obsah
  * Navrhnout konkrétní vylepšení editace
  * Výstup JSON s doporučeními pro editaci
  * Rozhodnutí Projde/Selže: PROJDE → MVP-019, SELŽE → smyčka vybrušování
  * Testy: Scénáře dobře a špatně editovaného skriptu
```

#### Kontroly čitelnosti (2 zbývající)

```bash
# MVP-019: Kontrola čitelnosti titulku (0.5 dne) - NEZAHÁJENO ❌
Worker10: Implementovat PrismQ.T.Review.Title.Readability v T/Review/Readability/
- Modul: PrismQ.T.Review.Title.Readability
- Závislosti: MVP-018 (editace musí projít)
- Priorita: STŘEDNÍ
- Úsilí: 0.5 dne
- Stav: NEZAHÁJENO
- Účel: Zkontrolovat jasnost, délku, poutavost pro voiceover
- Kritéria přijetí:
  * Vyhodnotit jasnost a srozumitelnost titulku
  * Zkontrolovat délku titulku (optimální pro voiceover a platformy)
  * Posoudit poutavost a efektivitu háčku
  * Ověřit obtížnost výslovnosti
  * Vypočítat skóre čitelnosti
  * Výstup JSON s metrikami čitelnosti a problémy
  * Rozhodnutí Projde/Selže: PROJDE → MVP-020, SELŽE → smyčka vybrušování titulku
  * Testy: Scénáře čitelných a obtížně čitelných titulků

# MVP-020: Kontrola čitelnosti skriptu (0.5 dne) - NEZAHÁJENO ❌
Worker10: Implementovat PrismQ.T.Review.Script.Readability v T/Review/Readability/
- Modul: PrismQ.T.Review.Script.Readability
- Závislosti: MVP-019 (čitelnost titulku musí projít)
- Priorita: STŘEDNÍ
- Úsilí: 0.5 dne
- Stav: NEZAHÁJENO
- Účel: Zkontrolovat přirozený tok, výslovnost, tempo pro voiceover
- Kritéria přijetí:
  * Vyhodnotit přirozený tok pro mluvení/voiceover
  * Identifikovat obtížně vyslovitelná slova nebo fráze
  * Zkontrolovat tempo (příliš rychlé/pomalé sekce)
  * Vypočítat skóre čitelnosti pro audio
  * Detekovat neohrabané konstrukce vět
  * Výstup JSON s metrikami čitelnosti a problematickými sekcemi
  * Rozhodnutí Projde/Selže: PROJDE → MVP-021, SELŽE → smyčka vybrušování skriptu
  * Testy: Scénáře přirozeného a neohrabaného toku skriptu
```

#### Finální revize a publikování (2 zbývající)

```bash
# MVP-021: Finální revize příběhu (0.5 dne) - NEZAHÁJENO ❌
Worker10: Implementovat PrismQ.T.Story.FinalReview v T/Story/FinalReview/
- Modul: PrismQ.T.Story.FinalReview
- Závislosti: MVP-020 (všechny kontroly kvality prošly)
- Priorita: VYSOKÁ
- Úsilí: 0.5 dne
- Stav: NEZAHÁJENO
- Účel: Holistické finální hodnocení před publikováním
- Kritéria přijetí:
  * Provést komplexní hodnocení příběhu (titulek + skript společně)
  * Zkontrolovat celkové sladění mezi titulkem a skriptem
  * Ověřit, že všechny brány kvality úspěšně prošly
  * Generovat finální hodnocení připravenosti
  * Výstup JSON s finálním stavem schválení a případnými doporučeními
  * Rozhodnutí Projde/Selže: PROJDE → MVP-022 (publikování), SELŽE → cílené vybrušování
  * Testy: Scénáře připraveno k publikování a vyžaduje vylepšení

# MVP-022: Publikování (1.5 dne) - NEZAHÁJENO ❌
Worker02: Implementovat PrismQ.T.Publishing.Finalization v T/Publishing/Finalization/
- Modul: PrismQ.T.Publishing.Finalization
- Závislosti: MVP-021 (finální revize musí projít)
- Priorita: VYSOKÁ
- Úsilí: 1.5 dne
- Stav: NEZAHÁJENO
- Účel: Označit jako publikováno, exportovat formáty, generovat zprávu o publikování
- Kritéria přijetí:
  * Označit stav obsahu jako "publikováno" v databázi
  * Exportovat do více formátů (JSON, Markdown, HTML)
  * Generovat kompletní zprávu o publikování
  * Uložit finální verzi s kompletní historií verzí
  * Zaznamenat časové razítko publikování a metadata
  * Výstup potvrzení publikování s cestami exportu
  * Testy: End-to-end workflow publikování s různými typy obsahu
```

---


## Příležitosti pro paralelní provádění

### Aktuálně k dispozici (Lze spustit nyní)
```bash
# MVP-017: Kontrola konzistence - PŘIPRAVENO KE SPUŠTĚNÍ ✅
Worker10: Implementovat Kontrolu konzistence
- Všechny závislosti splněny (MVP-016 dokončeno)
- Odhadováno: 0.5 dne
- Lze spustit okamžitě
```

### Blokováno (Čeká na závislosti)
```
MVP-018 → blokováno MVP-017
MVP-019 → blokováno MVP-018
MVP-020 → blokováno MVP-019
MVP-021 → blokováno MVP-020
MVP-022 → blokováno MVP-021
```

### Žádné příležitosti pro paralelní provádění
Kvůli sekvenčním závislostem kontrol kvality musí být issues dokončeny v pořadí. Není možná žádná paralelní práce v aktuálním sprintu.

---

## Standardy kvality issues

Všechny issues musí splňovat tato kritéria:

### Velikost
- **Malé**: Maximálně 0.5-2 dny úsilí
- **Zaměřené**: Jedna zodpovědnost na issue
- **Testovatelné**: Lze ověřit nezávisle

### Aplikace SOLID principů

Každá issue je navržena podle SOLID principů:

#### Princip jedné zodpovědnosti (S)
- Každá issue se zaměřuje na JEDEN konkrétní modul nebo funkci
- Příklad: MVP-017 se zabývá pouze kontrolou konzistence, ne editací nebo gramatikou
- Jasné, zaměřené prohlášení o účelu pro každou issue

#### Princip otevřeno/uzavřeno (O)
- Moduly jsou rozšiřitelné bez úprav
- Moduly revizí následují konzistentní vzory
- Nové typy revizí lze přidat bez změny existujících

#### Liskovův substituce princip (L)
- Všechny moduly revizí následují stejný interface kontrakt
- Jakýkoli modul revize lze použít zaměnitelně v pipeline
- Konzistentní formáty vstupu/výstupu napříč podobnými moduly

#### Princip segregace rozhraní (I)
- Moduly vystavují pouze potřebnou funkcionalitu
- Čistá, minimální veřejná API
- Žádné vynucené závislosti na nepoužívané funkcionalitě

#### Princip inverze závislostí (D)
- Moduly závisí na abstrakcích (vzory rozhraní revizí)
- Workflow vysoké úrovně nezávisí na implementačních detailech nízké úrovně
- Volná vazba mezi fázemi pipeline

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

### Sprint 1 (Týdny 1-2) ✅ DOKONČENO
- **Issues**: MVP-001 až MVP-005 + Dokumentace + Testy (7 issues)
- **Dokončeno**: Všech 7 issues ✅
  - MVP-001: Vytvoření nápadu ✅
  - MVP-002: Generování titulku ✅
  - MVP-003: Generování skriptu ✅
  - MVP-004: Revize titulku podle skriptu ✅
  - MVP-005: Revize skriptu podle titulku ✅
  - MVP-DOCS: Dokumentace Workflow ✅
  - MVP-TEST: Testovací Framework ✅
- **Pokrok**: 100% dokončeno (7 z 7 hotovo)
- **Revize**: Všechny issues revidovány v _meta/issues/done/

### Sprint 2 (Týdny 3-4) ✅ DOKONČENO
- **Issues**: MVP-006 až MVP-011 (6 issues)
- **Dokončeno**: Všech 6 issues ✅
  - MVP-006: Generování Titulku v2 ✅
  - MVP-007: Generování Skriptu v2 ✅
  - MVP-008: Revize Titulku v2 ✅
  - MVP-009: Vybrušování Titulku v3 ✅
  - MVP-010: Revize Skriptu v2 ✅
  - MVP-011: Vybrušování Skriptu v3 ✅
- **Pokrok**: 100% dokončeno (6 z 6 hotovo)
- **Revize**: Všechny issues revidovány v _meta/issues/done/

### Sprint 3 (Týdny 5-8) ⚠️ ČÁSTEČNĚ (5/11 Dokončeno)
- **Issues**: MVP-012 až MVP-022 (11 issues)
- **Dokončeno**: 5 issues ✅
  - MVP-012: Brána přijetí titulku ✅
  - MVP-013: Brána přijetí skriptu ✅
  - MVP-014: Kontrola gramatiky ✅
  - MVP-015: Kontrola tónu ✅
  - MVP-016: Kontrola obsahu ✅ (sloučeno z main)
- **Zbývající**: 6 issues ❌
  - MVP-017: Kontrola konzistence (VYSOKÁ priorita - DALŠÍ)
  - MVP-018: Kontrola editace (VYSOKÁ priorita)
  - MVP-019: Čitelnost titulku (STŘEDNÍ priorita)
  - MVP-020: Čitelnost skriptu (STŘEDNÍ priorita)
  - MVP-021: Finální revize příběhu (VYSOKÁ priorita)
  - MVP-022: Publikování (VYSOKÁ priorita)
- **Pokrok**: 45% dokončeno (5 z 11 hotovo)
- **Revize**: Dokončené issues revidovány v _meta/issues/done/

### Celkově
- **Celkem issues**: 22 MVP issues (sníženo z 23 - sloučena expert review do finální revize)
- **Dokončeno**: 16 issues (73%) ✅
- **Zbývá**: 6 issues (27%)
- **Aktuální sprint**: Sprint 3 (částečný pokrok)
- **Odhadovaný zbývající čas**: ~4-5 dní práce, 1.5-2 týdny kalendářního času

---

## Kritická cesta

```
Sprint 1 ✅ → Sprint 2 ✅ → MVP-017 (další) → Kontroly kvality → Publikování
  HOTOVO       HOTOVO        0.5 dne          2 dny             1.5 dne
```

**Aktuální stav**: Sprint 1 DOKONČEN ✅ | Sprint 2 DOKONČEN ✅ | Sprint 3 PROBÍHÁ (45%)

**Další priorita**: MVP-017 (Kontrola konzistence) - VYSOKÁ priorita, blokuje zbývající kontroly kvality

---

**Stav**: Sprint 3 probíhá (5/11 Dokončeno)  
**Další akce**: Worker10 implementovat MVP-017 (Kontrola konzistence)  
**Aktualizováno**: 2025-11-22 (Refaktorováno - SOLID principy, zaměření na MVP, zjednodušeno)  
**Vlastník**: Worker01  
**Dokument pokroku**: Viz `PROGRESS_ASSESSMENT_2025-11-22.md` pro detailní analýzu  
**Kontrola integrity**: Viz `INTEGRITY_CHECK_2025-11-22.md` pro ověření po sloučení
