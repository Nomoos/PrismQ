# Databázová integrace

Společný vzor pro všechny moduly pracující s databází:

- **Databáze:** Jedna sdílená SQLite databáze `db.s3db`
- **Spojení:** Nastaveno JEDNOU při inicializaci, znovu použito napříč operacemi
- **Transakce:** Commit při úspěchu, rollback při chybě
- **Cleanup:** Spojení uzavřeno ve `finally` bloku při ukončení
- **Tabulky:** Story, Idea, Title, Script, Review (dle potřeby modulu)
