---
title: OpenEnv Email Triage
emoji: "📨"
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# OpenEnv Email Triage Environment

A deterministic, real-world OpenEnv environment for training and evaluating agents on customer email triage workflows. The environment models a realistic operations task: classify urgency, route ownership, and choose safe final handling actions under policy constraints.

## Why this environment

Support and operations teams triage thousands of emails daily. Incorrect prioritization or routing delays incident response and impacts users. This environment captures that operational decision loop with measurable outcomes and reproducible scoring.

## Environment design

- **Domain:** Customer operations and incident triage.
- **Core API:** `reset()`, `step(action)`, and `state()`.
- **Typed models:** Pydantic schemas for observation, action, reward signal, and grader output.
- **Episode boundaries:** Ends on explicit `finalize` action or when max-step budget is reached.
- **Determinism:** Fixed tasks and deterministic grader logic for reproducible benchmark scores.

## Action space

Action payload (JSON):

```json
{
  "kind": "set_priority | set_team | set_action | add_note | finalize",
  "value": "string"
}
```

### Supported values

- `set_priority`: `low | medium | high | critical`
- `set_team`: `support | finance | security | engineering | compliance`
- `set_action`: `respond | escalate | defer | close`

## Observation space

Each step returns:

- task metadata (`task_id`, `difficulty`)
- input email (`email_subject`, `email_body`)
- constraints and policy notes
- current prediction state (`predicted_priority`, `predicted_team`, `predicted_action`)
- partial score (`partial_score`) and trajectory status (`step_count`, `max_steps`)

## Tasks and difficulty progression

1. **Easy** (`email-easy-001`)  
   Password reset lockout before customer demo.
2. **Medium** (`email-medium-001`)  
   Duplicate enterprise billing charge requiring finance escalation.
3. **Hard** (`email-hard-001`)  
   Potential data exfiltration incident with PII risk.

## Grader and scoring

Each episode gets a deterministic score in `[0.0, 1.0]`:

- Priority correctness: 35%
- Team routing correctness: 30%
- Final action correctness: 25%
- Efficiency bonus: 10%
- Safety/format penalties are subtracted and clipped

Pass threshold: `score >= 0.80`.

## Reward shaping

Dense reward includes:

- partial positive signal for each correct decision dimension
- stronger reward for correct terminal configuration
- efficiency signal for shorter valid trajectories
- penalties for invalid or malformed actions

This avoids sparse binary feedback and provides useful gradient for policy learning.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run environment locally

```bash
uvicorn src.app:app --host 0.0.0.0 --port 7860
```

Health check:

```bash
curl http://localhost:7860/health
```

## Run baseline inference

Set required variables:

- `API_BASE_URL` (LLM API endpoint)
- `MODEL_NAME` (model identifier)
- `HF_TOKEN` (API key)

Optional:

- `OPENAI_API_KEY` (fallback key source)
- `ENV_BASE_URL` (environment endpoint, default `http://localhost:7860`)

Run:

```bash
python inference.py
```

The script emits structured logs in strict format:

- `[START] ...`
- `[STEP] step=... action=... reward=... done=... error=...`
- `[END] success=... steps=... score=... rewards=...`

## Docker

```bash
docker build -t openenv-email-triage .
docker run --rm -p 7860:7860 openenv-email-triage
```

## OpenEnv metadata and validation

- Metadata file: `openenv.yaml`
- Validate locally (if installed):

```bash
openenv validate
```

## Suggested Hugging Face Space deployment

1. Create a **Docker Space**.
2. Push this repository.
3. Set Space secrets:
   - `API_BASE_URL`
   - `MODEL_NAME`
   - `HF_TOKEN`
   - optional `OPENAI_API_KEY`
4. Verify:
   - `GET /health` returns 200
   - `POST /reset` returns valid episode object

## Baseline reproducibility notes

- Tasks are fixed and deterministic.
- Graders are deterministic and bounded in `[0.0, 1.0]`.
- Inference uses low-temperature generation and a deterministic fallback policy.

