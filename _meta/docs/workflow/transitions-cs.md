# Přechody stavů


### Dopředná progrese (Postupné obohacování formátů)

Workflow následuje **model postupného obohacování**:

**Cesta pouze textu (Nejrychlejší - Zastavení po textu):**
```
IdeaInspiration → Idea (Creation → Outline → Title) → ScriptDraft → 
ScriptReview → ScriptApproved → TextPublishing → PublishedText → 
AnalyticsReviewText → Archived
```

**Cesta text + audio (Střední - Zastavení po audiu):**
```
... → ScriptApproved → TextPublishing → PublishedText → Voiceover → 
VoiceoverReview → VoiceoverApproved → AudioPublishing → PublishedAudio → 
AnalyticsReviewAudio → Archived
```

**Cesta plné produkce (Kompletní - Všechny formáty):**
```
... → PublishedText → Voiceover → ... → PublishedAudio → ScenePlanning → 
KeyframePlanning → KeyframeGeneration → VideoAssembly → VideoReview → 
VideoFinalized → PublishPlanning → PublishedVideo → AnalyticsReviewVideo → 
Archived
```

**Klíčový tok dat:**
```
ScriptApproved
    ↓
TextPublishing → PublishedText (text je publikován)
    ↓
Voiceover (používá publikovaný text jako zdroj)
    ↓
VoiceoverApproved → AudioPublishing → PublishedAudio (audio je publikováno)
    ↓
ScenePlanning (používá publikované audio jako základ)
    ↓
... → PublishedVideo (video je publikováno)
```

### Zpětné přechody (Revizní smyčky)

Problémy s kvalitou nebo vylepšení spouštějí zpětný pohyb:

**Revize fáze skriptu**
- `ScriptReview → ScriptDraft` - Potřeba velkých revizí skriptu
- `ScriptReview → Idea` - Vyžadovány zásadní změny konceptu
- `ScriptApproved → ScriptReview` - Problémy nalezeny po schválení

**Revize publikace textu**
- `TextPublishing → ScriptApproved` - Problémy s formátováním textu, potřeba revize skriptu
- `Voiceover → PublishedText` - Problémy s hlasem vzhledem ke zdroji publikovaného textu

**Revize fáze hlasu**
- `VoiceoverReview → Voiceover` - Potřeba nového nahrávání
- `VoiceoverReview → PublishedText` - Potřeba revize zdroje publikovaného textu
- `Voiceover → PublishedText` - Chyby v publikovaném textu objeveny během nahrávání

**Revize publikace audia**
- `AudioPublishing → VoiceoverApproved` - Problémy se souborem audia, potřeba re-exportu
- `ScenePlanning → PublishedAudio` - Problémy s plánováním videa vzhledem ke zdroji audia

**Revize vizuální fáze**
- `KeyframePlanning → ScenePlanning` - Potřeba revize struktury scény
- `KeyframeGeneration → KeyframePlanning` - Potřeba úpravy specifikací klíčových snímků
- `ScenePlanning → PublishedAudio` - Problémy s časováním audia ovlivňují vizuály

**Revize fáze videa**
- `VideoReview → VideoAssembly` - Problémy se skládáním/editací
- `VideoReview → KeyframeGeneration` - Problémy s vizuálními assety
- `VideoFinalized → VideoReview` - Problémy objeveny po schválení

**Revize fáze publikace**
- `PublishPlanning → VideoFinalized` - Potřeba změn videa před publikací

### Zpětnovazební smyčky

**Učební smyčky specifické pro formát**
- `AnalyticsReviewText → IdeaInspiration` - Poznatky z výkonu textu
- `AnalyticsReviewAudio → IdeaInspiration` - Poznatky z výkonu audia
- `AnalyticsReviewVideo → IdeaInspiration` - Poznatky z výkonu videa
- Poznatky napříč formáty informují budoucí obsahovou strategii
- Analytika raného formátu informuje produkční rozhodnutí pro pozdější formáty
- Data o výkonu se vracejí zpět pro vylepšení budoucího obsahu

**Smyčka vylepšení konceptu**
- `ScriptDraft → Idea` - Koncept potřebuje zásadní přepracování
- `Idea → IdeaInspiration` - Návrat ke zdrojům inspirace

### Časné ukončení

Obsah může být archivován z jakéhokoli stavu:
```
[Jakýkoli stav] → Archived
```

**Důvody pro časnou archivaci:**
- Koncept již není životaschopný
- Omezení zdrojů
- Strategický pivot
- Problémy s kvalitou neřešitelné
- Duplicitní obsah
- Externí faktory

