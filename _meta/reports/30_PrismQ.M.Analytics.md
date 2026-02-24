# Kontrola běhu modulu: PrismQ.M.Analytics

**Účel:** Sběr, agregace a analýza metrik z publikovaného obsahu napříč platformami pro data-driven content strategy.

---

## 📥 Vstup
- **Zdroj:** API všech publishing platforem + databáze
- **Data:** Engagement metriky (views, listens, reads), social metriky, SEO metriky, audience demographics, revenue data
- **Předpoklady:** Published content (moduly 20, 25, 28, 29), přístup k analytics APIs, platné API credentials

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Data collection — text metriky (GA: page views, time on page), audio (downloads, completion rate), video (views, watch time, retention), social (engagement rate, CTR), SEO (rankings, impressions), revenue (ad revenue, affiliate)
3. Data aggregation — normalize across platforms, calculate total reach/engagement, time-series data
4. Analysis — performance vs benchmarks, audience demographics, content type comparison, trend analysis
5. [AI insights generation](shared/ollama_ai_integrace.md) — actionable recommendations, optimal publish times, top-performing formats
6. Reporting — real-time dashboards, weekly/monthly reports, anomaly alerts
7. [Uložení výsledků](shared/databazova_integrace.md) — store metrics, update performance scores, tag high-performers

---

## 📤 Výstup
- **Primární:** Analytics dashboards, performance reports, actionable insights
- **DB změny:** Tabulka `Analytics` — metriky, performance scores, audience profiles, trend data
- **Další krok:** Feedback loop → Modul 01 (informuje budoucí content strategy)
