# Zpracování chyb

Společný vzor pro ošetření chyb ve všech modulech:

- **Import error:** Zobrazení chybové zprávy, ukončení
- **Ollama nedostupný:** `RuntimeError` s instrukcemi
- **Databáze nedostupná:** Zobrazení chyby, ukončení
- **Databáze při save:** Rollback transakce, logování chyby
- **AI generování selhalo:** Skip položky, pokračování s dalšími
- **Ctrl+C:** Čisté ukončení s uzavřením DB spojení
