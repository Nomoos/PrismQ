# Vzor Ultra-clean Pipeline

**Zjednodušená reprezentace běhu PrismQ**

## Přehled

Ultra-Clean Pipeline je zjednodušená, čitelná reprezentace základního iterativního workflow v Text Generation Pipeline PrismQ (T modul). Ukazuje základní tok dat a závislostí mezi fázemi v čistém formátu s tečkovou notací.

## Struktura vzoru

```
Idea.Creation 
→ Title.From.Idea 
→ Script.From.Title.Idea 
→ Review.Title.By.Script.Idea 
→ Title.From.Script.Review.Title 
→ Review.Script.By.Title.Idea 
→ Script.From.Title.Review.Script 
→ Review.Idea.By.Title.Script 
→ Idea.From.Title.Script.Review.Idea
```

## Vysvětlení vzoru

### Fáze 1: `Idea.Creation`
**Účel**: Počáteční vytvoření nápadu  
**Vstupy**: Žádné (výchozí bod)  
**Výstupy**: `Idea`

Vytváří základní nápad pro obsah.

---

### Fáze 2: `Title.From.Idea`
**Účel**: Generování počátečního titulku z nápadu  
**Vstupy**: `Idea`  
**Výstupy**: `Title` (v1)

Vytváří první verzi titulku založenou pouze na nápadu.

---

### Fáze 3: `Script.From.Title.Idea`
**Účel**: Generování počátečního skriptu  
**Vstupy**: `Title`, `Idea`  
**Výstupy**: `Script` (v1)

Vytváří první verzi skriptu s použitím titulku i původního nápadu jako kontextu.

---

### Fáze 4: `Review.Title.By.Script.Idea`
**Účel**: Recenze titulku proti skriptu a nápadu  
**Vstupy**: `Title`, `Script`, `Idea`  
**Výstupy**: `Review.Title` (zpětná vazba)

Vyhodnocuje, zda je titulek dobře sladěn s obsahem skriptu a původním nápadem.

---

### Fáze 5: `Title.From.Script.Review.Title`
**Účel**: Vylepšení titulku na základě skriptu a recenze  
**Vstupy**: `Script`, `Review.Title`, (předchozí) `Title`  
**Výstupy**: `Title` (v2)

Generuje vylepšenou verzi titulku s využitím poznatků ze skriptu a zpětné vazby z recenze.

---

### Fáze 6: `Review.Script.By.Title.Idea`
**Účel**: Recenze skriptu proti titulku a nápadu  
**Vstupy**: `Script`, `Title`, `Idea`  
**Výstupy**: `Review.Script` (zpětná vazba)

Vyhodnocuje, zda je skript dobře sladěn s aktualizovaným titulkem a původním nápadem.

---

### Fáze 7: `Script.From.Title.Review.Script`
**Účel**: Vylepšení skriptu na základě titulku a recenze  
**Vstupy**: `Title`, `Review.Script`, (předchozí) `Script`  
**Výstupy**: `Script` (v2)

Generuje vylepšenou verzi skriptu s využitím aktualizovaného titulku a zpětné vazby z recenze.

---

### Fáze 8: `Review.Idea.By.Title.Script`
**Účel**: Validace úplného sladění  
**Vstupy**: `Idea`, `Title`, `Script`  
**Výstupy**: `Review.Idea` (validace)

Finální validace, že všechny komponenty (nápad, titulek, skript) jsou soudržně sladěny.

---

### Fáze 9: `Idea.From.Title.Script.Review.Idea`
**Účel**: Finalizace nebo vylepšení reprezentace nápadu  
**Vstupy**: `Title`, `Script`, `Review.Idea`  
**Výstupy**: `Idea` (vylepšený/finalizovaný)

Aktualizuje nebo potvrzuje reprezentaci nápadu na základě plně vyvinutého titulku, skriptu a validační zpětné vazby.

---

## Klíčové charakteristiky

### 1. **Tečková notace**
Každá fáze je reprezentována ve formátu `Entita.Akce.Kontext`:
- **Entita**: Primární artefakt, který je vytvářen nebo modifikován (Idea, Title, Script, Review)
- **Akce**: Prováděná operace (Creation, From, By)
- **Kontext**: Vstupy informující operaci (Idea, Title, Script, Review)

### 2. **Explicitní závislosti**
Notace explicitně ukazuje, na čem každá fáze závisí:
- `Title.From.Idea` → Titulek závisí na Nápadu
- `Script.From.Title.Idea` → Skript závisí na Titulku i Nápadu
- `Review.Title.By.Script.Idea` → Recenze vyhodnocuje Titulek pomocí Skriptu a Nápadu

### 3. **Iterativní vylepšování**
Vzor ukazuje, jak jsou artefakty iterativně vylepšovány:
- Titulek v1 → Recenze → Titulek v2
- Skript v1 → Recenze → Skript v2
- Vícenásobné křížové recenze zajišťují sladění

### 4. **Cyklus společného vylepšování**
Vzor demonstruje metodologii vzájemně závislého vylepšování:
- Titulek je recenzován proti Skriptu
- Skript je recenzován proti Titulku
- Oba jsou kontinuálně vylepšovány na základě vzájemné zpětné vazby

## Mapování na kompletní workflow

Ultra-Clean Pipeline je zjednodušený pohled. Zde je mapování na kompletní 26fázové MVP workflow:

| Fáze Ultra-Clean | Fáze MVP | Popis |
|------------------|----------|-------|
| `Idea.Creation` | Fáze 1 | PrismQ.T.Idea.Creation |
| `Title.From.Idea` | Fáze 2 | PrismQ.T.Title.FromIdea (v1) |
| `Script.From.Title.Idea` | Fáze 3 | PrismQ.T.Script.FromIdeaAndTitle (v1) |
| `Review.Title.By.Script.Idea` | Fáze 4 | PrismQ.T.Review.Title.ByScript (v1) |
| `Title.From.Script.Review.Title` | Fáze 6 | PrismQ.T.Title.Improvements (v2) |
| `Review.Script.By.Title.Idea` | Fáze 5, 10 | PrismQ.T.Review.Script.ByTitle (v1, v2) |
| `Script.From.Title.Review.Script` | Fáze 7, 11 | PrismQ.T.Script.Improvements (v2, v3) |
| `Review.Idea.By.Title.Script` | Fáze 12-13 | Kontroly přijetí titulku a skriptu |
| `Idea.From.Title.Script.Review.Idea` | Fáze 14-23 | Kvalitní recenze, expertní recenze, publikace |

## Výhody Ultra-Clean notace

### 1. **Čitelnost**
Čistý, lidsky čitelný formát, který rychle předává podstatu workflow.

### 2. **Jasnost závislostí**
Okamžitě viditelné, na čem každá fáze závisí, což činí tok dat transparentním.

### 3. **Komunikace**
Snadné pro diskuzi a vysvětlení workflow zúčastněným stranám, vývojářům a tvůrcům obsahu.

### 4. **Dokumentace**
Slouží jako stručná reference pro základní iterativní proces.

### 5. **Zjednodušení**
Abstrahuje implementační detaily při zachování koncepčního toku.

## Použití v dokumentaci

### Rychlá reference
Použijte Ultra-Clean Pipeline jako rychlou referenci v horní části detailní dokumentace workflow pro okamžité poskytnutí kontextu čtenářům.

### Koncepční diskuze
Použijte ji při diskuzi o filosofii workflow a metodologii iterativního vylepšování.

### Onboarding
Použijte ji pro představení PrismQ workflow novým členům týmu před ponořením se do detailních fází.

### Architektonické diagramy
Začleňte ji do high-level architektonických diagramů pro zobrazení základní smyčky tvorby obsahu.

## Související dokumentace

- **[Fáze MVP](./mvp-stages_CS.md)** - Kompletní 26fázové workflow s detailní implementací
- **[Stavový automat](./state-machine_CS.md)** - Kompletní dokumentace stavového automatu
- **[Přechody](./transitions_CS.md)** - Pravidla a logika přechodů stavů
- **[Workflow Titulku a Skriptu](../../T/TITLE_SCRIPT_WORKFLOW.md)** - Detailní workflow T modulu

---

**Verze:** 1.0  
**Poslední aktualizace:** 2025-11-24  
**Část:** Dokumentace workflow PrismQ
