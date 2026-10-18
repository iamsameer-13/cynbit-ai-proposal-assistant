# Technical Approach Report: Inquiry-to-Proposal Assistant

## 1. Architecture
```
Inquiry text
   │
   ├─► Retrieval (keyword overlap over services_catalog.json) ─► top-2 services as context
   │
   ├─► Extractor ── LLM (Claude, JSON-only) ─┐
   │              └ Heuristic fallback ──────┤  (used offline or on API failure)
   │                                         ▼
   │                    Validation (allow-listed service, urgency enum)
   │                                         ▼
   ├─► Lead scorer (deterministic, 0-100, explainable breakdown)
   │                                         ▼
   └─► Proposal builder (template + catalog data) ─► Streamlit UI / .md download
```
Files: `core.py` (pipeline), `app.py` (UI), `eval.py` (evaluation), `data/` (catalog and labelled samples).

## 2. Model choices
- **LLM extractor: Claude Sonnet (`claude-sonnet-5-5`, configurable via `CYNBIT_MODEL`).** Strong structured-output reliability and instruction following at moderate cost. A smaller, cheaper model is a drop-in swap once evals show parity.
- **Why not fine-tune:** no labelled dataset exists yet, and prompting plus validation is enough for extraction. Fine-tuning becomes worthwhile after a few hundred reviewed inquiries.
- **Why a rule-based scorer:** sales leads must be able to see why a lead is "Hot". Rules are auditable and tunable without retraining.
- **Heuristic baseline:** regex and keyword matching provide an offline mode, a graceful fallback, and a baseline the LLM must beat.

## 3. Data pipeline
1. **Input:** free-text inquiry (form, email, chat).
2. **Retrieval:** stem and tokenize, then overlap with catalog keywords. Top services and their min budget, timeline and deliverables are injected as context. At scale, replace with embeddings (e.g., a small sentence-transformer plus a vector store) over catalog and past proposals.
3. **Extraction:** schema: `service, budget_inr, urgency, requirements[], risks[], clarifying_questions[]`.
4. **Normalization:** budgets converted to INR (lakh, k, USD at an assumed rate of 85); unknown values stay `null`.
5. **Scoring:** budget fit (40), urgency (25), requirement clarity (25), service fit (10). Bands: Hot ≥ 70, Warm ≥ 45, otherwise Cold.
6. **Output:** structured JSON plus a markdown draft proposal.

## 4. Prompt engineering
- A system prompt fixes the role, output schema and rules (JSON only, never invent budgets, use allow-listed services).
- The inquiry is wrapped in `<inquiry>` tags and declared to be data, which reduces prompt-injection risk. The catalog goes in `<catalog>` tags.
- Output is parsed, fences stripped, and validated in code. Any failure falls back to the heuristic extractor, so the app always returns a result.
- Temperature should be set low in production for consistency (not set in the PoC; defaults apply).

## 5. Evaluation
`eval.py` runs 12 labelled synthetic inquiries (service, urgency, budget, lead band).

**Offline heuristic baseline (measured):** service 12/12, urgency 11/12, band 11/12, budget 12/12.

**Failure case:** inquiry #2, "8k per month", is read as a timeline signal, so urgency becomes medium instead of low and the lead is scored Hot instead of Warm. This is the type of ambiguity an LLM should handle better.

**Caveats (important):** the samples are small, written by me, and fairly clean, so 100% on some metrics overstates real-world accuracy. I have not run the LLM mode in this submission environment, so no LLM numbers are claimed. Next step: collect 100+ real, anonymized inquiries labelled by a salesperson, and compare LLM vs. baseline by field.

## 6. Execution plan
| Phase | Duration | Work |
|---|---|---|
| 0. Discovery | Week 1 | Collect past inquiries, real rate card, interview sales; define labels |
| 1. PoC to pilot | Weeks 1-2 | Replace sample catalog; connect web form/email intake; run in shadow mode |
| 2. Evaluate | Weeks 2-3 | Label 100+ inquiries; compare LLM vs. baseline; tune prompts and score weights |
| 3. Human-in-the-loop launch | Week 4 | Salesperson reviews every draft; capture edits as feedback data |
| 4. Scale | Month 2+ | Embedding retrieval over past proposals, CRM integration, multilingual (Hindi/English) support |

## 7. Operations, cost, privacy
- **Cost:** roughly one short LLM call per inquiry; at agency volumes this is a small monthly cost, to be measured in the pilot.
- **Monitoring:** log inputs, outputs, latency, fallback rate and reviewer edits.
- **Privacy:** store the minimum, mask contact details before logging, and confirm API data-retention terms.
- **Safety:** human approval before anything is sent to a client; no autonomous quoting.

## 8. Limitations and future work
Keyword retrieval is crude; the catalog and prices are placeholders; no multilingual handling; no conversation memory; scoring weights are heuristic and should be fitted to real win/loss data.
