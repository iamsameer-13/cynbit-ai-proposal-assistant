# Cynbit Inquiry-to-Proposal Assistant

AI/ML Engineer Intern assessment: _Identify an AI Opportunity for Cynbit_.

An AI assistant that reads a client inquiry, extracts service, budget and urgency, scores the lead (0-100, explainable) and drafts a proposal with clarifying questions.

## Deliverables

1. [`docs/01_AI_Opportunity_Report.md`](docs/01_AI_Opportunity_Report.md) — opportunity analysis
2. This repo — working Streamlit app (`app.py`, `core.py`) and evaluation (`eval.py`)
3. [`docs/02_Technical_Approach_Report.md`](docs/02_Technical_Approach_Report.md) — architecture, models, pipeline, plan

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py          # works offline with a heuristic extractor
export ANTHROPIC_API_KEY=...  # optional: enables the LLM extractor (see .env.example)
python eval.py --offline      # evaluation on 12 labelled sample inquiries
```

No API key? The app still runs using the heuristic baseline. If an LLM call fails it falls back automatically.

## Deploy a live demo

https://cynbit-ai-proposal-assistant-mkbrru4dgwgu2mvxseqfly.streamlit.app/

## Honest notes

- The services catalog and prices in `data/` are **illustrative assumptions**, not Cynbit's real pricing.
- Sample inquiries are synthetic and small. Offline baseline results: service 12/12, urgency 11/12, band 11/12, budget 12/12. LLM mode was not benchmarked here.
