# TOON vs JSON: Quick Summary

> **Full Document**: See [TOON_VS_JSON_AI_APPLICATIONS.md](./TOON_VS_JSON_AI_APPLICATIONS.md) for comprehensive analysis

**Research Date**: 2025-11-17  
**TL;DR**: Use **JSON for everything except LLM prompts**. Convert structured data to **TOON for 30-60% token savings** in LLM inputs.

---

## What is TOON?

**TOON (Token-Oriented Object Notation)** is a compact encoding of JSON specifically designed for Large Language Models.

- **Purpose**: Reduce token costs in LLM prompts
- **Lossless**: Exact JSON representation, just more compact
- **Syntax**: YAML-style indentation + CSV-style tabular arrays
- **Savings**: 30-60% fewer tokens on uniform arrays
- **Spec**: https://github.com/toon-format/spec
- **Status**: Production-ready (v2.0, MIT licensed)

---

## Quick Decision Guide

```
Choose a format:

├─ Is this for an LLM prompt?
│  ├─ No → ✅ Use JSON (universal standard)
│  └─ Yes
│     ├─ Data is uniform and tabular (10+ rows)?
│     │  └─ ✅ Use TOON (30-60% token savings)
│     └─ Data is nested or non-uniform?
│        └─ ✅ Use JSON (better for complex structures)
│
├─ Is this API communication?
│  └─ ✅ Use JSON (REST standard)
│
├─ Is this data storage or ML training?
│  └─ ✅ Use JSON/JSONL (framework standard)
│
└─ Is this a config file?
   └─ ✅ Use JSON or TOML (not TOON)
```

---

## Side-by-Side Comparison

**Same data, different formats:**

### JSON (95 tokens)
```json
{
  "friends": ["ana", "luis", "sam"],
  "hikes": [
    {
      "id": 1,
      "name": "Blue Lake Trail",
      "distanceKm": 7.5,
      "elevationGain": 320,
      "companion": "ana",
      "wasSunny": true
    },
    {
      "id": 2,
      "name": "Ridge Overlook",
      "distanceKm": 9.2,
      "elevationGain": 540,
      "companion": "luis",
      "wasSunny": false
    }
  ]
}
```

### TOON (45 tokens, 53% savings)
```toon
friends[3]: ana,luis,sam

hikes[2]{id,name,distanceKm,elevationGain,companion,wasSunny}:
  1,Blue Lake Trail,7.5,320,ana,true
  2,Ridge Overlook,9.2,540,luis,false
```

---

## Comparison at a Glance

| Feature | JSON | TOON | Winner |
|---------|------|------|--------|
| **Token Efficiency** | Baseline | 30-60% fewer | 🏆 TOON |
| **Uniform Arrays** | Verbose | CSV-style compact | 🏆 TOON |
| **Nested Data** | Standard | Similar or more | 🏆 JSON |
| **LLM Validation** | Schema needed | Built-in (length, fields) | 🏆 TOON |
| **API Standard** | ✅ Yes | ❌ No | 🏆 JSON |
| **Universal Support** | ✅ Yes | ⚠️ Limited (JS/TS) | 🏆 JSON |
| **Ecosystem** | ✅ Mature | ⚠️ Growing | 🏆 JSON |
| **Parse Speed** | ✅ Faster | Slower | 🏆 JSON |
| **Human Familiarity** | ✅ Universal | CSV-like | 🏆 JSON |

---

## Token Cost Savings

**Example**: 10,000 LLM classification requests

| Format | Tokens per Request | Total Tokens | Cost (GPT-4) |
|--------|-------------------|--------------|--------------|
| JSON | 8,000 | 80M | $800 |
| TOON | 4,000 | 40M | $400 |
| **Savings** | **50%** | **40M** | **$400/month** |

**Annual savings**: **$4,800**

---

## When TOON Wins

✅ **Use TOON when**:
- Sending structured data to LLMs
- Data is uniform and tabular (10+ rows)
- Token costs are significant (>1000 LLM requests/day)
- 30-60% token savings matter to your budget

**Best for**:
- Content classification batches
- Scoring large datasets
- Multi-shot learning examples
- Structured data analysis

---

## When JSON Wins

✅ **Use JSON when**:
- API communication (REST standard)
- Data storage (database, files)
- ML training data (JSONL format)
- Internal processing (universal support)
- Configuration files (use JSON or TOML)
- Logging and metrics
- Data is deeply nested or non-uniform

**Best for**:
- Everything except LLM prompts

---

## PrismQ Usage Recommendations

### The Hybrid Approach 🎯

```
Internal Processing (JSON)
       ↓
Convert to TOON for LLM Prompt
       ↓
LLM Processing (30-60% fewer tokens)
       ↓
Parse Response (JSON)
       ↓
Store Results (JSON)
```

### Implementation Strategy

**Phase 1**: Research & Setup
- Find/implement Python TOON library
- Test token savings on sample data
- Measure conversion overhead

**Phase 2**: Pilot (Classification Module)
- Convert classification prompts to TOON
- Measure actual token savings
- Monitor LLM accuracy

**Phase 3**: Expand if Successful
- Add to Scoring module
- Create helper utilities
- Document best practices

---

## Quick Code Examples

### Example 1: Classification with TOON

```python
import json
# import toon  # When available

def classify_batch(ideas: list[dict]) -> list[dict]:
    """Classify ideas with TOON for token efficiency."""
    
    # Option 1: Use TOON (if library available)
    if TOON_AVAILABLE:
        toon_data = toon.encode({"ideas": ideas})
        format_type = "TOON"
    else:
        # Option 2: Fallback to JSON
        toon_data = json.dumps({"ideas": ideas}, indent=2)
        format_type = "JSON"
    
    prompt = f"""
Classify each idea. Data in {format_type} format:

{toon_data}

Return results:

results[{len(ideas)}]{{id,category,confidence}}:

Use comma delimiter.
"""
    
    response = llm.complete(prompt)  # 30-50% fewer tokens with TOON
    
    # Parse response
    if TOON_AVAILABLE and format_type == "TOON":
        return toon.decode(response)["results"]
    else:
        return json.loads(response)["results"]
```

### Example 2: Token Counting

```python
import tiktoken

def compare_token_efficiency(data: dict) -> dict:
    """Compare JSON vs TOON token efficiency."""
    
    encoder = tiktoken.get_encoding("cl100k_base")  # GPT-4
    
    # JSON
    json_str = json.dumps(data, indent=2)
    json_tokens = len(encoder.encode(json_str))
    
    # TOON (if available)
    if TOON_AVAILABLE:
        toon_str = toon.encode(data)
        toon_tokens = len(encoder.encode(toon_str))
    else:
        toon_tokens = json_tokens
    
    # Calculate savings
    savings_pct = 100 * (json_tokens - toon_tokens) / json_tokens
    
    return {
        "json_tokens": json_tokens,
        "toon_tokens": toon_tokens,
        "savings_pct": savings_pct,
        "recommendation": "TOON" if savings_pct > 20 else "JSON"
    }

# Test with your data
results = compare_token_efficiency({"ideas": [...]})
print(f"Token savings: {results['savings_pct']:.1f}%")
print(f"Recommendation: {results['recommendation']}")
```

---

## TOON Ecosystem Status

**As of 2025-11-17:**

| Language | Support | Package |
|----------|---------|---------|
| JavaScript/TypeScript | ✅ Official | `@toon-format/toon` |
| Python | ⚠️ Community | Check PyPI |
| Go | ⚠️ Limited | TBD |
| Rust | ⚠️ Limited | TBD |
| Java | ⚠️ Limited | TBD |

**Note**: JSON has universal support across all languages.

---

## Key Takeaways

1. **TOON is specialized** for one use case: LLM prompts with structured data
2. **JSON remains default** for everything else (APIs, storage, processing)
3. **Token savings are real**: 30-60% on uniform tabular data
4. **Cost impact matters** at scale (e.g., $400/month for 10K requests)
5. **Hybrid approach works**: JSON internally, TOON for LLM input
6. **Ecosystem is growing**: Official JS/TS support, Python coming

---

## Next Steps for PrismQ

### Immediate Actions
1. ✅ Review this research
2. ⬜ Identify Python TOON library or implementation approach
3. ⬜ Test token savings on sample PrismQ data
4. ⬜ Decide on pilot scope (Classification module?)

### If Proceeding with TOON
1. ⬜ Install/implement TOON encoder/decoder
2. ⬜ Convert 1-2 high-volume LLM prompts to TOON
3. ⬜ Measure actual token cost savings
4. ⬜ Monitor LLM accuracy and response quality
5. ⬜ Expand based on ROI

### If Sticking with JSON
- ✅ Continue current approach (working well)
- ⬜ Revisit when Python TOON library is official
- ⬜ Monitor TOON ecosystem maturity

---

## Resources

- **TOON Spec**: https://github.com/toon-format/spec
- **TOON GitHub**: https://github.com/toon-format/toon
- **npm package**: https://www.npmjs.com/package/@toon-format/toon
- **JSON Spec**: RFC 8259
- **Tokenizer**: tiktoken (OpenAI)

---

## Example ROI Calculation

**Scenario**: PrismQ Classification Module

- **Current**: 500 LLM requests/day with JSON (8,000 tokens each)
- **With TOON**: 500 requests/day with TOON (4,000 tokens each, 50% savings)

**Monthly:**
- JSON: 500 × 30 days × 8,000 tokens = 120M tokens = $1,200
- TOON: 500 × 30 days × 4,000 tokens = 60M tokens = $600
- **Savings: $600/month or $7,200/year**

**Implementation Cost**:
- Setup time: ~1-2 weeks (research, implement, test)
- Maintenance: Minimal (just conversion layer)

**ROI**: Positive after first month if volume is high enough.

---

**Quick Links**:
- Full research: [TOON_VS_JSON_AI_APPLICATIONS.md](./TOON_VS_JSON_AI_APPLICATIONS.md)
- Research index: [README.md](./README.md)
- TOON Spec: https://github.com/toon-format/spec
