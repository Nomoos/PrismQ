# Testy pro PrismQ Skripty

Tento adresář obsahuje testy pro Python skripty v PrismQ projektu.

## Spuštění testů

### Instalace závislostí

```bash
cd scripts
pip install -r requirements.txt
pip install pytest
```

### Spuštění všech testů

```bash
# Z adresáře scripts
python -m pytest tests/ -v

# Nebo přímo
pytest tests/ -v
```

### Spuštění konkrétního testu

```bash
# Spustit pouze testy pro add_module.py
python -m pytest tests/test_add_module.py -v

# Spustit konkrétní testovací třídu
python -m pytest tests/test_add_module.py::TestModuleCreator -v

# Spustit konkrétní test
python -m pytest tests/test_add_module.py::TestModuleCreator::test_parse_github_url_full_https -v
```

### Spuštění testů s pokrytím kódu

```bash
pip install pytest-cov
pytest tests/ --cov=. --cov-report=html
```

## Struktura testů

### test_add_module.py

Obsahuje komplexní testy pro `add_module.py` skript:

- **TestModuleCreator**: Základní testy pro třídu ModuleCreator
  - Parsování GitHub URL (různé formáty)
  - Odvození cesty modulů
  - Odvození názvu remote
  
- **TestModulePathDerivation**: Specializované testy pro odvozování cest
  - Edge cases a speciální situace
  - Vnořené moduly
  - Reálné příklady z projektu

- **TestURLParsing**: Rozšířené testy parsování URL
  - Různé protokoly (HTTP, HTTPS, SSH)
  - Case sensitivity
  - Organizační repozitáře

## Dokumentace testů

Všechny testy jsou dokumentovány v češtině pro lepší pochopení funkcionality.
Každý test obsahuje:
- Název v angličtině (podle pytest konvence)
- Docstring v češtině popisující účel testu
- Jasné očekávání a aserce

## Pokrytí testy

Testy pokrývají následující funkcionality:

✅ Parsování GitHub URL (všechny podporované formáty)  
✅ Odvozování cesty modulů z názvů repozitářů  
✅ Generování názvů remote  
✅ Validace vstupů  
✅ Edge cases a speciální situace  

## Přidání nových testů

Při přidávání nových testů dodržujte následující konvence:

1. Používejte pytest fixtures pro setup
2. Dokumentujte testy v češtině
3. Pojmenujte testy popisně: `test_<co_se_testuje>`
4. Seskupujte související testy do tříd
5. Používejte jasné aserce s informativními zprávami

## Příklad nového testu

```python
def test_nova_funkcionalita(self, creator):
    """
    Test nové funkcionality.
    
    Popisuje co se testuje a proč.
    """
    # Arrange - příprava
    vstup = "testovací data"
    
    # Act - provedení
    vysledek = creator.nova_metoda(vstup)
    
    # Assert - ověření
    assert vysledek == "očekávaný výsledek"
```

## Continuous Integration

Testy jsou spuštěny automaticky při každém push do repozitáře.
Všechny testy musí projít před mergem pull requestu.
