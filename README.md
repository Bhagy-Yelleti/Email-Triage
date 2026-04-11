# Email Triage OpenEnv

A benchmark-quality reinforcement learning environment for enterprise email decision-making, threat detection, and multi-step incident response.

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

## Benchmark Highlights

- adversarial phishing detection
- deceptive sender spoofing
- delayed consequence simulation
- deterministic seeded episodes
- multi-step RL state transitions
- strategic stakeholder conflicts
- benchmark-grade reward shaping

## Flagship Hard Task — Adversarial Enterprise Inbox

This task simulates a high-pressure enterprise inbox containing critical incidents, phishing attempts, deceptive sender domains, and delayed escalation threads.

The agent must balance speed, safety, and business priority while making sequential decisions.

## Dynamic Consequence Modeling

Actions taken in earlier steps affect future inbox state.

Examples include:
- breach alerts triggered by missed phishing
- CEO escalation threads
- missed deadline penalties
- cascading customer incidents

## RL Environment Design

- multi-step episode transitions
- deterministic seeded randomness
- partial reward shaping
- long-horizon delayed penalties
- adaptive thread generation

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

+0.20 critical resolution  
+0.20 phishing detection  
+0.15 stakeholder priority  
+0.15 delayed consequence prevention  
+0.15 efficiency  
+0.15 thread memory

## Baseline Performance

* Validation Status: Passed
* Hugging Face Deployment: Live
* Max Episode Steps: 35
* Reward Range: 0.0 – 1.0
* Difficulty Levels: Easy / Medium / Hard / Dynamic / Adversarial

## Author

Bhagya Yelleti
