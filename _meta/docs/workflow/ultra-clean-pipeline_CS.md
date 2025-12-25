# Vzor Ultra-clean Pipeline

**Zjednodušená reprezentace běhu PrismQ**

## Přehled

Ultra-Clean Pipeline je zjednodušená, čitelná reprezentace základního iterativního workflow v Text Generation Pipeline PrismQ (T modul). Ukazuje základní tok dat a závislostí mezi fázemi v čistém formátu s tečkovou notací.

## Struktura vzoru

```
Idea.Creation 
→ Title.From.Idea 
→ Content.From.Idea.Title 
→ Review.Title.From.Content.Idea 
→ Title.From.Title.Review.Content 
→ Review.Content.From.Title.Idea 
→ Content.From.Title.Content.Review 
→ Review.Idea.From.Title.Content 
→ Idea.From.Title.Content.Review.Idea
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

### Fáze 3: `Content.From.Idea.Title`
**Účel**: Generování počátečního obsahu  
**Vstupy**: `Title`, `Idea`  
**Výstupy**: `Content` (v1)

Vytváří první verzi obsahu s použitím titulku i původního nápadu jako kontextu.

---

### Fáze 4: `Review.Title.From.Content.Idea`
**Účel**: Recenze titulku proti obsahu a nápadu  
**Vstupy**: `Title`, `Content`, `Idea`  
**Výstupy**: `Review.Title` (zpětná vazba)

Vyhodnocuje, zda je titulek dobře sladěn s obsahem a původním nápadem.

---

### Fáze 5: `Title.From.Title.Review.Content`
**Účel**: Vylepšení titulku na základě obsahu a recenze  
**Vstupy**: `Content`, `Review.Title`, (předchozí) `Title`  
**Výstupy**: `Title` (v2)

Generuje vylepšenou verzi titulku s využitím poznatků z obsahu a zpětné vazby z recenze.

---

### Fáze 6: `Review.Content.From.Title.Idea`
**Účel**: Recenze obsahu proti titulku a nápadu  
**Vstupy**: `Content`, `Title`, `Idea`  
**Výstupy**: `Review.Content` (zpětná vazba)

Vyhodnocuje, zda je obsah dobře sladěn s aktualizovaným titulkem a původním nápadem.

---

### Fáze 7: `Content.From.Title.Content.Review`
**Účel**: Vylepšení obsahu na základě titulku a recenze  
**Vstupy**: `Title`, `Review.Content`, (předchozí) `Content`  
**Výstupy**: `Content` (v2)

Generuje vylepšenou verzi obsahu s využitím aktualizovaného titulku a zpětné vazby z recenze.

---

### Fáze 8: `Review.Idea.From.Title.Content`
**Účel**: Validace úplného sladění  
**Vstupy**: `Idea`, `Title`, `Content`  
**Výstupy**: `Review.Idea` (validace)

Finální validace, že všechny komponenty (nápad, titulek, obsah) jsou soudržně sladěny.

---

### Fáze 9: `Idea.From.Title.Content.Review.Idea`
**Účel**: Finalizace nebo vylepšení reprezentace nápadu  
**Vstupy**: `Title`, `Content`, `Review.Idea`  
**Výstupy**: `Idea` (vylepšený/finalizovaný)

Aktualizuje nebo potvrzuje reprezentaci nápadu na základě plně vyvinutého titulku, obsahu a validační zpětné vazby.

---

## Klíčové charakteristiky

### 1. **Tečková notace**
Každá fáze je reprezentována ve formátu `Entita.Akce.Kontext`:
- **Entita**: Primární artefakt, který je vytvářen nebo modifikován (Idea, Title, Content, Review)
- **Akce**: Prováděná operace (Creation, From, By)
- **Kontext**: Vstupy informující operaci (Idea, Title, Content, Review)

### 2. **Explicitní závislosti**
Notace explicitně ukazuje, na čem každá fáze závisí:
- `Title.From.Idea` → Titulek závisí na Nápadu
- `Content.From.Title.Idea` → Obsah závisí na Titulku i Nápadu
- `Review.Title.From.Content.Idea` → Recenze vyhodnocuje Titulek pomocí Obsahu a Nápadu

### 3. **Iterativní vylepšování**
Vzor ukazuje, jak jsou artefakty iterativně vylepšovány:
- Titulek v1 → Recenze → Titulek v2
- Obsah v1 → Recenze → Obsah v2
- Vícenásobné křížové recenze zajišťují sladění

### 4. **Cyklus společného vylepšování**
Vzor demonstruje metodologii vzájemně závislého vylepšování:
- Titulek je recenzován proti Obsahu
- Obsah je recenzován proti Titulku
- Oba jsou kontinuálně vylepšovány na základě vzájemné zpětné vazby

## Mapování na kompletní workflow

Ultra-Clean Pipeline je zjednodušený pohled na 9 koncepčních fází. Zde je mapování na kompletní 26fázové MVP workflow:

**Poznámka**: Čísla "Fáze Ultra-Clean" (1-9) reprezentují sekvenční fáze v zjednodušeném vzoru, které se mohou mapovat na více nebo nesekvenčních fází v kompletním MVP workflow.

| Fáze Ultra-Clean | Fáze MVP | Popis |
|------------------|----------|-------|
| `Idea.Creation` | Fáze 1 | PrismQ.T.Idea.From.User |
| `Title.From.Idea` | Fáze 2 | PrismQ.T.Title.From.Idea (v1) |
| `Content.From.Title.Idea` | Fáze 3 | PrismQ.T.Content.FromIdeaAndTitle (v1) |
| `Review.Title.From.Content.Idea` | Fáze 4 | PrismQ.T.Review.Title.ByContent (v1) |
| `Title.From.Content.Review.Title` | Fáze 6 | PrismQ.T.Title.From.Title.Review.Content (v2) |
| `Review.Content.From.Title.Idea` | Fáze 5, 10 | PrismQ.T.Review.Content.ByTitle (v1, v2) |
| `Content.From.Title.Review.Content` | Fáze 7, 11 | PrismQ.T.Content.Improvements (v2, v3) |
| `Review.Idea.From.Title.Content` | Fáze 12-13 | Kontroly přijetí titulku a obsahu |
| `Idea.From.Title.Content.Review.Idea` | Fáze 14-23 | Kvalitní recenze, expertní recenze, publikace |

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
- **[Workflow Titulku a Obsahu](../../T/TITLE_SCRIPT_WORKFLOW.md)** - Detailní workflow T modulu

---

**Verze:** 1.0  
**Poslední aktualizace:** 2025-11-24  
**Část:** Dokumentace workflow PrismQ
