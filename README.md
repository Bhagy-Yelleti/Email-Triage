---
title: OpenEnv Email Triage
emoji: "📬"
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# Production-Grade Email Assistant Environment

A deterministic, real-world OpenEnv environment for training and evaluating AI agents on advanced email triage workflows. The environment models a realistic operations and personal assistant task: reading complex emails, predicting categories, extracting deadlines, estimating priority, and choosing safe handling actions.

## 🌟 Why this is Real-World Useful

Support, operations teams, and individuals triage thousands of emails daily. Understanding the **intent, urgency, and deadlines** within unstructured text is critical for AI assistants to be useful. 
This environment moves beyond simple keyword matching to full semantic understanding. It captures out-of-band operational workflows with measurable outcomes, rich rewarding, and reproducible deterministic scoring in an OpenEnv-compliant lifecycle setup.

## 🏗️ OpenEnv Architecture & UI UX Upgrade

The environment complies fully with the OpenEnv specification (`reset()`, `step(action)`, `state()`, `/schema`) but acts as a fully fleshed out **Production Web Application** deployed via Hugging Face Spaces. 

**Interactive Frontend features:**
- Clean, modern Inbox sidebar queue
- Live preview pane simulating email clients
- Live AI Extraction pane displaying Category, Score, Urgency, Extracted Deadlines.
- Auto-Responder drafts for context-heavy emails (e.g. meetings, offers).
- Analytics summary cards tracking overall episodes score.

*(Imagine screenshot here showcasing the polished 3-pane dashboard with badges and AI extraction info)*

## 📥 Dataset & Task Difficulty Progression

The environment processes a curated subset of 8-10 demo emails across 3 varied difficulty levels:

1. **Easy** (`email-easy-001`): Obvious bank frauds, simple newsletter spams, and straightforward "URGENT" server-down warnings.
2. **Medium** (`email-medium-001`): Ambiguous project deadline extensions, standard HR benefit enrollments.
3. **Hard** (`email-hard-001`): Phishing scams disguised as IT passwords resets, subtle internship confirmation deadlines, unstructured vendor outreach.

## 🎮 Observation & Action Space

**Observation Space (State representation):**
At each step, agents are served the `current_email` object containing `sender`, `subject`, `body`, as well as environment tracking counts. In the UI, the environment also enriches output with deterministic semantic analysis (`deadline_extracted`, `sentiment`, `suggested_reply`).

**Action Space Payload:**
```json
{
  "action": 2, 
  "category": "work",
  "urgency_level": "medium"
}
```
*Where action is an integer {0=mark_urgent, 1=archive, 2=reply, 3=mark_spam}.*

## 🏆 Advanced Reward Logic Explanation

Dense rewards have been added without breaking the `[0.0, 1.0]` API requirement:
- **+0.2** for correctly extracting and identifying the email category.
- **+0.3** for accurately identifying the `urgency_level`.
- **+0.5** for selecting the exact correct routing action (Spam, Reply, Archive, Urgent).
- **-0.2 Penalty** for incorrectly classifying valid emails as Spam or repeating actions unnecessarily.

This rich partial reward structure ensures the RL agent gets meaningful gradients early in the learning process by validating its intermediate cognitive steps (e.g. understanding it's a 'finance' category even if it incorrectly 'archives' instead of 'replying' to a refund).

## 🚀 Future Scope

- Integrating a multi-action step where the agent drafts the reply email string.
- Connecting to live IMAP configurations.
- More adversarial evaluations introducing prompt injections in email bodies.

---

## 🛠️ Run environment locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860
```
Open `http://localhost:7860/dashboard` to view the UI.

## 🤖 Baseline inference

```bash
export API_BASE_URL="..."
export MODEL_NAME="..."
export HF_TOKEN="..."
python inference.py
```
Outputs strictly adhere to the OpenEnv output requirements: `[START]`, `[STEP]`, `[END]`.

## 📦 Docker & Spec Testing
```bash
docker build -t openenv-email-triage .
docker run --rm -p 7860:7860 openenv-email-triage
openenv validate
```
