# Inicializace prostředí

Společný postup pro všechny moduly:

1. **Kontrola Python** - ověření instalace Python 3.12+
2. **Virtual environment** - vytvoření/aktivace `.venv` v adresáři modulu
3. **Instalace dependencies** - `pip install` z `requirements.txt` (pytest, requests)
4. **Kontrola Ollama** - ověření dostupnosti serveru na `localhost:11434`
5. **Spuštění modulu** - Python skript

Batch skript `Run.bat` automatizuje celý proces.
