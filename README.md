# Email Triage OpenEnv

AI-powered enterprise email triage environment built using OpenEnv, FastAPI, and deployed on Hugging Face Spaces.

![Dashboard Preview](./screenshots/dashboard.png)

## Live Demo

https://huggingface.co/spaces/bhagya1234567890/email-triage-openenv

## Preview

![AI Insights](./screenshots/ai-panel.png)

![Reward Panel](./screenshots/reward-panel.png)

![Inbox View](./screenshots/inbox-view.png)

## Overview

This project simulates a real-world enterprise email triage workflow where an AI agent classifies emails, detects urgency, extracts deadlines, recommends actions, and receives structured rewards through the OpenEnv framework.

It is designed as a realistic benchmark for evaluating intelligent agents on communication-heavy enterprise workflows.

## Features

* Dense visual RL reward shaping
* Precision urgency classification and sentiment extraction
* Continuous OpenEnv evaluation loop
* Thread-aware deterministic inbox mocking
* Live real-time UI/UX state synchronization

## Tech Stack

Python, FastAPI, OpenEnv, Docker, Hugging Face Spaces

## API Endpoints

```bash
POST /reset
POST /step
GET /state
GET /health
```

## Reward Logic

```text
+0.30 classification
+0.30 action
+0.20 urgency
+0.20 fast resolution
```

## Baseline Performance

* Validation Status: Passed
* Hugging Face Deployment: Live
* Max Episode Steps: 15
* Reward Range: 0.0 – 1.0
* Difficulty Levels: Easy / Medium / Hard

## Author

Bhagya Yelleti
