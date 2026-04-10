---
title: OpenEnv Email Triage
emoji: "📬"
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# 📧 Email Triage OpenEnv

Production-grade AI-powered email prioritization and response environment built using OpenEnv and deployed on Hugging Face Spaces.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi)
![OpenEnv](https://img.shields.io/badge/OpenEnv-Certified-success.svg)
![Hugging Face Spaces](https://img.shields.io/badge/Hugging%20Face-Spaces-yellow?logo=huggingface)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker&logoColor=white)
![Hackathon Submission](https://img.shields.io/badge/Hackathon-Submission-purple)

---

## 🚀 Live Demo

> Fully deployed and validator-compliant production environment.

🔗 **Hugging Face Space:**
[https://huggingface.co/spaces/bhagya1234567890/email-triage-openenv](https://huggingface.co/spaces/bhagya1234567890/email-triage-openenv)

*(All UI features seamlessly hook into the OpenEnv reinforcement APIs!)*

---

## 🖼️ Application Screenshots

### Dashboard Overview
> Full UI screenshot of inbox + analytics + AI panel

![Dashboard Overview](screenshots/dashboard.png)

### AI Intelligence Panel
> Screenshot showing recommendation, deadline, sentiment

![AI Intelligence](screenshots/ai-panel.png)

### Reward Breakdown
> Screenshot of RL/OpenEnv scoring panel

![Reward Breakdown](screenshots/reward-breakdown.png)

### Inbox Queue View
> Screenshot with multiple realistic emails

![Inbox Queue View](screenshots/inbox-queue.png)

*(Note: Ensure you populate the `/screenshots` directory with your live grabs!)*

---

## ✨ Features

* **Intelligent Email Classification:** Automatically categorizes inbound load (Work, Personal, Finance, Spam).
* **Urgency Detection:** Identifies critical issues (e.g., server down alerts, urgent transactions).
* **Deadline Extraction:** Detects implicit and explicit timeline requests ("ASAP", "By Friday").
* **Sentiment Analysis:** Discovers negative incident emotions ensuring rapid escalation.
* **Explainable AI Reasoning:** Visualizes exactly *why* a model made its triage decision for maximum transparency.
* **Reward Shaping for RL Agents:** Multi-parameter float distribution explicitly rewarding sub-tasks without breaking the `(0, 1)` validator boundary.
* **Structured OpenEnv API:** Implements standardized `/step`, `/reset`, and `/state` validation workflows.
* **Production-Grade UI Dashboard:** Stunning 3-panel enterprise UI interface designed specifically for human-in-the-loop review.
* **Deployed on Hugging Face Spaces:** Publicly available Docker execution instantly scaling to reviewers.

---

## 🏗️ Architecture

- **Frontend Dashboard:** A vanilla HTML/CSS/JS glassmorphism client implementing rigorous UI state management bridging seamlessly to RL environments.
- **FastAPI Backend:** Lightweight Python 3.9+ webserver powering OpenEnv specification endpoints.
- **OpenEnv Routes:** The rigid RL endpoints bridging the local states dicts to standard `StepRequests`.
- **Reward Engine:** Calculates granular metric points leveraging expected vs actual actions, plus partial completion metrics (`urgency`, `category`).
- **AI Reasoning Pipeline:** Synthesizes metadata from simulated LLM JSON responses (or explicit environment state mocking) to deliver real-time confidence scores and drafting matrices.

---

## 🌍 Real-World Utility

This environment simulates **real-world enterprise email triage workflows**. 

Support, operations, and leadership teams are overwhelmed by thousands of emails daily. Understanding the *intent, urgency, and deadlines* within unstructured text is critical for AI assistants to be useful. 
This project captures the core decision loop: classifying urgency, routing ownership, drafting suggested responses, and prioritizing incident escalations, all graded via a reproducible OpenEnv benchmark!

---

## 💻 Tech Stack

- **Python** (Core Environment & Logic)
- **FastAPI** (Server Infrastructure)
- **Hugging Face Spaces** (Cloud Deployment)
- **OpenEnv** (RL Evaluation Specifications)
- **Docker** (Containerization & Portability)
- **HTML / CSS / JS** (Client UI)

---

## 🛠️ Run environment locally

```bash
# Set up environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start the uvicorn API
uvicorn app:app --host 0.0.0.0 --port 7860
```
Open `http://localhost:7860` to view the comprehensive UI Dashboard.

## 🤖 Baseline inference

```bash
export API_BASE_URL="..."
export MODEL_NAME="..."
export HF_TOKEN="..."
python inference.py
```
> Note: Outputs strictly adhere to the OpenEnv output requirements: `[START]`, `[STEP]`, `[END]`.

## 📦 Docker & Spec Testing
```bash
docker build -t openenv-email-triage .
docker run --rm -p 7860:7860 openenv-email-triage
openenv validate
```
