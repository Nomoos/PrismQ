# Kontrola běhu modulu: PrismQ.T.Publishing

## 🎯 Účel modulu
Publikování finálního textového obsahu na cílové platformy. Modul exportuje Stories do různých formátů, generuje SEO metadata, vytváří social media posts, a připravuje content pro multi-platform distribution.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Story)
- **Typ dat:** Story objekty ve stavu "PrismQ.T.Publishing"
- **Povinné hodnoty:**
  - Story s polished title a content
  - SEO metadata z modulu 19
  - Publishing metadata (author, date, categories)
- **Nepovinné hodnoty:**
  - `--preview`, `--debug` flags
  - Target platforms (blog, Medium, social media)
  - Scheduling parameters
- **Očekávané předpoklady:**
  - Stories prošlé polish (modul 19)
  - Přístup k publishing APIs (WordPress, Medium, atd.)
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Načtení Stories** - dotaz na stav "PrismQ.T.Publishing"
2. **Format conversion:**
   - **Blog format**: HTML s proper headings, paragraphs
   - **Social media snippets**: Twitter, Facebook, LinkedIn posts
   - **Email newsletter**: Email-friendly HTML
   - **PDF export**: Downloadable version (optional)
   - **Plain text**: Fallback format
3. **SEO finalization:**
   - Meta title (optimalizovaný pro search)
   - Meta description (~155 chars, engaging)
   - Keywords/tags
   - OpenGraph tags (Facebook, LinkedIn)
   - Twitter Card tags
   - Canonical URL
   - Schema.org markup (Article schema)
4. **Social media content:**
   - Twitter thread (pokud content dlouhý)
   - Facebook post s hook
   - LinkedIn post (professional tone)
   - Instagram caption (pokud applicable)
   - Hashtag suggestions
5. **Content taxonomy:**
   - Categories assignment
   - Tags generation
   - Topic clustering
   - Related content linking
6. **Publishing actions:**
   - Upload to blog/CMS (WordPress API)
   - Schedule publikace (immediate nebo delayed)
   - Post na social media (Buffer/Hootsuite API)
   - Email newsletter distribution (pokud applicable)
   - RSS feed update
7. **Post-publishing:**
   - Generate shareable links
   - Create tracking URLs (UTM parameters)
   - Analytics integration (Google Analytics events)
   - Backup published version
8. **Update Story:**
   - Uložení publishing metadata
   - State změna na "Published" nebo "TextPublished"
   - Zaznamenání publishing timestamp
   - URLs published verze

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:**
  - Published Story na target platforms
  - Social media posts
  - SEO-optimized web page
  
- **Formát výstupu:**
  - Blog: HTML page na web
  - Social: Posts na Twitter, Facebook, LinkedIn
  - Email: Newsletter email (pokud applicable)
  - Databáze: Updated Story s publishing info
  
- **Vedlejší efekty:**
  - RSS feed updated
  - Sitemap updated
  - Analytics tracking active
  - Social media notifications sent
  - Backups created
  - Publishing reports generated
  
- **Chování při chybě:**
  - API error: Retry s backoff, pak manual intervention
  - Publishing failed: Rollback, log error, alert admin
  - Partial failure: Continue with successful platforms, flag failed ones

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 19 - polished Story
- Publishing APIs:
  - WordPress/CMS API
  - Social media APIs (Twitter, Facebook, LinkedIn)
  - Email marketing API (Mailchimp, SendGrid)
  - Buffer/Hootsuite (social scheduling)
- SEO tools
- Analytics platforms (Google Analytics)
- Databáze

**Výstupní závislosti:**
- Audio pipeline: Modul 21 (PrismQ.A.Voiceover) - může číst published text
- Video pipeline: Modul 26 (PrismQ.V.Scene) - může používat published content
- Analytics: Modul 30 (PrismQ.M.Analytics) - trackuje published content performance

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Multi-platform publishing vyžaduje různé formáty
- SEO metadata critical pro discoverability
- Social media posts by měly být engaging, ne jen links
- Scheduling umožňuje optimal publishing times
- Tracking URLs essential pro ROI analysis
- Content can be published immediately nebo scheduled
- Publishing může být atomic (all-or-nothing) nebo partial (best effort)

**Rizika:**
- **API failures**: Publishing platforms mohou být nedostupné
- **Rate limiting**: Social APIs mají request limits
- **Format compatibility**: Různé platformy různé requirements
- **Duplicate content**: SEO penalty pokud stejný content na více doménách
- **Broken links**: Internal links mohou být broken
- **Authentication expiry**: API tokens mohou expirovat
- **Content approval**: Některé platformy vyžadují manual approval
- **Scheduling conflicts**: Stejný čas publikace jako jiný content

**Doporučení:**
- Robust error handling a retry logic
- Health checks pro všechny APIs před publishing
- Dry-run mode pro testování bez actual publish
- Content backup před publish (rollback capability)
- Multi-stage publishing (blog first, then social)
- Publishing queue system pro handling vysokého volume
- Monitoring a alerting pro publishing failures
- Regular API token renewal
- Content calendar integration (avoid conflicts)
- A/B testing různých publishing times
- Track engagement metrics per platform
- Implement content promotion strategy post-publish
- Regular SEO audits published content
