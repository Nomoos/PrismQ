# YouTube Scraping - Rychlá Referenční Karta / Quick Reference Card

**Pro kompletní návod viz:** [MANUAL_TESTING_PROCEDURE.md](./MANUAL_TESTING_PROCEDURE.md)  
**For complete guide see:** [MANUAL_TESTING_PROCEDURE.md](./MANUAL_TESTING_PROCEDURE.md)

---

## ⚡ Rychlý Start / Quick Start

### 1. Instalace / Installation
```bash
cd Sources/Content/Shorts/YouTube
pip install -r requirements.txt
cp .env.test.example .env.test
```

### 2. Základní Testy / Basic Tests

**Scrape z kanálu / Scrape from channel:**
```bash
python -m src.cli scrape-channel --env-file .env.test --top 5
```

**Scrape trending:**
```bash
python -m src.cli scrape-trending --env-file .env.test --top 10
```

**Vyhledávání / Search:**
```bash
python -m src.cli scrape-keyword --env-file .env.test --keyword "startup ideas" --top 8
```

### 3. Zobrazení Výsledků / View Results

**Statistiky / Statistics:**
```bash
python -m src.cli stats --env-file .env.test
```

**Seznam nápadů / List ideas:**
```bash
python -m src.cli list --env-file .env.test
```

### 4. Čištění / Cleanup

**Vymazat databázi / Clear database:**
```bash
python -m src.cli clear --env-file .env.test
```

---

## 📋 Dostupné Příkazy / Available Commands

| Příkaz / Command | Popis / Description |
|------------------|---------------------|
| `scrape-channel` | Scrape z YouTube kanálu / Scrape from YouTube channel |
| `scrape-trending` | Scrape trending Shorts / Scrape trending Shorts |
| `scrape-keyword` | Vyhledávání podle klíčových slov / Search by keywords |
| `list` | Zobrazit sesbírané nápady / Display collected ideas |
| `stats` | Zobrazit statistiky / Show statistics |
| `process` | Zpracovat na IdeaInspiration formát / Process to IdeaInspiration format |
| `clear` | Vymazat databázi / Clear database |

---

## 🔧 Často Používané Parametry / Common Parameters

| Parametr | Účel / Purpose | Příklad / Example |
|----------|----------------|-------------------|
| `--env-file .env.test` | Použít testovací config / Use test config | `--env-file .env.test` |
| `--top N` | Maximální počet výsledků / Max results | `--top 10` |
| `--channel URL` | URL kanálu / Channel URL | `--channel "@SnappyStories_1"` |
| `--keyword TEXT` | Klíčové slovo / Keyword | `--keyword "business tips"` |
| `--no-interactive` | Bez interaktivních dotazů / No prompts | `--no-interactive` |

---

## 🎯 Testovací Kanály / Test Channels

| Název / Name | Handle | Účel / Purpose |
|--------------|--------|----------------|
| SnappyStories_1 | `@SnappyStories_1` | Oficiální testovací kanál / Official test channel |
| MrBeast | `@MrBeast` | Velký kanál s Shorts / Large channel with Shorts |
| Kurzgesagt | `@kurzgesagt` | Vzdělávací / Educational |

---

## ⚠️ Nejčastější Problémy / Common Issues

### "No module named 'dotenv'"
```bash
pip install python-dotenv
```

### "yt-dlp not found"
```bash
pip install --upgrade yt-dlp
```

### "No Shorts found"
```bash
# Použít testovací kanál / Use test channel
python -m src.cli scrape-channel --channel "@SnappyStories_1" --top 5 --env-file .env.test
```

### "Database locked"
```bash
# Zavřít ostatní aplikace / Close other apps
rm test_db.s3db-journal  # Linux/macOS
del test_db.s3db-journal  # Windows
```

---

## 📚 Další Dokumentace / Additional Documentation

- **[MANUAL_TESTING_PROCEDURE.md](./MANUAL_TESTING_PROCEDURE.md)** - Kompletní manuální testovací postup / Complete manual testing procedure
- **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** - Automatizované testování / Automated testing
- **[CONFIGURATION.md](./CONFIGURATION.md)** - Konfigurace / Configuration
- **[SCRAPING_BEST_PRACTICES.md](./SCRAPING_BEST_PRACTICES.md)** - Osvědčené postupy / Best practices

---

**Vytvořeno / Created**: 2025-11-03  
**Verze / Version**: 1.0.0
