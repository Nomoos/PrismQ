# Osvědčené postupy MVP workflow

**Osvědčené postupy, řešení problémů a pokyny**

## Řešení problémů

### Běžné problémy a řešení

#### Problém 1: Nekonečná smyčka v kontrolách přijetí

**Příznak**: Titulek nebo skript nikdy neprojde kontrolou přijetí

**Řešení**:
```python
# Přidání limitu iterací a eskalace
max_iterations = 5
for i in range(max_iterations):
    if check_acceptance(item):
        break
    if i == max_iterations - 1:
        # Eskalace na manuální recenzi
        manual_review_queue.add(item)
```

#### Problém 2: Kvalitní recenze neustále selhávají

**Příznak**: Gramatické/tónové/obsahové recenze konzistentně selhávají

**Řešení**:
```python
# Úprava citlivosti recenze
review_config = {
    "grammar_strictness": "medium",
    "tone_tolerance": 0.2,
    "content_min_score": 70
}
```

### Debug režim

Povolte debug režim pro podrobné logování:

```python
from PrismQ.T import Workflow
import logging

logging.basicConfig(level=logging.DEBUG)
workflow = Workflow(debug=True)
```

---

## Souhrn

MVP workflow poskytuje komplexní, iterativní přístup k tvorbě obsahu s:

- **26 fázemi** pokrývajícími všechny aspekty od nápadu po publikaci
- **3 hlavními iteračními smyčkami** pro kontinuální vylepšování
- **7 kvalitními dimenzemi** validovanými prostřednictvím AI recenzí
- **Explicitními branami přijetí** zajišťujícími kvalitní standardy
- **Sledováním verzí** zachovávajícím kompletní historii
- **GPT expertní recenzí** pro profesionální leštění

Tato dokumentace poskytuje kompletní pokrytí:
- ✅ Všech 26 fází workflow s podrobnými popisy
- ✅ Příkladů použití pro klíčové vzory
- ✅ Dokumentace iteračních smyček
- ✅ Kompletní API reference
- ✅ Osvědčených postupů a řešení problémů

Pro další informace viz:
- [MVP_WORKFLOW.md](./_meta/issues/MVP_WORKFLOW.md) - Původní specifikace
- [WORKFLOW_CS.md](./WORKFLOW_CS.md) - Kompletní dokumentace stavového automatu
- [T/README.md](./T/README.md) - Přehled pipeline generování textu

---

**Verze**: 1.0  
**Vytvořeno**: 2025-11-22  
