# 🥗 NutriChef AI

A conversational culinary and macro concierge assistant built on Google Agent Development Kit (ADK) and Gemini. NutriChef AI helps health-conscious individuals cook delicious meals, hit their calories and macronutrient goals, and visualize plating presentations with generative AI.

---

## ✨ Features

- **Firestore Recipe Catalog**: Search, view, and save healthy recipes with full macronutrient profiles (calories, protein, carbs, fat), dietary tags, ingredients, and instructions.
- **AI Plating Visualizer & Cloud Storage Publisher**: Generates professional culinary food photography using `gemini-2.5-flash-image` on Vertex AI and uploads the images to a public Cloud Storage bucket.
- **TheMealDB Integration**: Connects to the global culinary database to search for real meal ideas and ingredient lists across international cuisines.
- **A2UI Rich Card Rendering**: Emits native A2UI (v0.8) display cards formatted as structured JSON for rich visual presentation.
- **Web Chat Frontend**: Built with FastAPI and a modern HTML/CSS chat interface that communicates with the agent via the A2A protocol and natively renders A2UI cards and plating images.

---

## 🏗️ Architecture

```
User (Browser) 
      │
      ▼
FastAPI Proxy / Chat UI (Cloud Run)
      │  (A2A Protocol)
      ▼
NutriChef AI Agent (Agent Runtime / ADK)
      ├── Firestore Database (`recipes` collection)
      ├── Google Cloud Storage (Public recipe media bucket)
      ├── Vertex AI (`gemini-3.8-flash` & `gemini-2.5-flash-image`)
      └── TheMealDB Public API
```

---

## 📁 Project Structure

```
nutrichef-ai/
├── app/
│   ├── agent.py               # Main agent logic, tools, and A2UI schema
│   └── a2ui_utils.py          # A2UI response rewrapping callback
├── frontend/
│   ├── main.py                # FastAPI proxy communicating over A2A
│   ├── static/index.html      # Responsive chat interface with A2UI card renderer
│   ├── Dockerfile             # Container configuration for Cloud Run
│   └── requirements.txt       # Frontend dependencies
├── scripts/
│   └── seed_firestore.py      # Firestore database seeding script
├── project_brief.md           # Project specification and requirements
├── pyproject.toml             # Agent dependencies and package metadata
└── agents-cli-manifest.yaml   # Agents CLI configuration
```

## Requirements

Before you begin, ensure you have:
- **uv**: Python package manager (used for all dependency management in this project) - [Install](https://docs.astral.sh/uv/getting-started/installation/) ([add packages](https://docs.astral.sh/uv/concepts/dependencies/) with `uv add <package>`)
- **agents-cli**: Agents CLI - Install with `uv tool install google-agents-cli`
- **Google Cloud SDK**: For GCP services - [Install](https://cloud.google.com/sdk/docs/install)


## Quick Start

Install `agents-cli` and its skills if not already installed:

```bash
uvx google-agents-cli setup
```

Install required packages:

```bash
agents-cli install
```

Test the agent with a local web server:

```bash
agents-cli playground
```

You can also use features from the [ADK](https://adk.dev/) CLI with `uv run adk`.

## Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `agents-cli install` | Install dependencies using uv                                                         |
| `agents-cli playground` | Launch local development environment                                                  |
| `agents-cli lint`    | Run code quality checks                                                               |
| `agents-cli eval`    | Evaluate agent behavior (generate, grade, analyze, and more — see `agents-cli eval --help`) |
| `uv run pytest tests/unit tests/integration` | Run unit and integration tests                                                        |
| `agents-cli deploy`  | Deploy agent to Agent Runtime                                                                |
| `agents-cli publish gemini-enterprise` | Register deployed agent to Gemini Enterprise                    || [A2A Inspector](https://github.com/a2aproject/a2a-inspector) | Launch A2A Protocol Inspector                                                        |

## 🛠️ Project Management

| Command | What It Does |
|---------|--------------|
| `agents-cli scaffold enhance` | Add CI/CD pipelines and Terraform infrastructure |
| `agents-cli infra cicd` | One-command setup of entire CI/CD pipeline + infrastructure |
| `agents-cli scaffold upgrade` | Auto-upgrade to latest version while preserving customizations |

---

## Development

Edit your agent logic in `app/agent.py` and test with `agents-cli playground` - it auto-reloads on save.

## Deployment

```bash
gcloud config set project <your-project-id>
agents-cli deploy
```

To add CI/CD and Terraform, run `agents-cli scaffold enhance`.
To set up your production infrastructure, run `agents-cli infra cicd`.

## Observability

Built-in telemetry exports to Cloud Trace, BigQuery, and Cloud Logging.

## A2A Inspector

This agent supports the [A2A Protocol](https://a2a-protocol.org/). Use the [A2A Inspector](https://github.com/a2aproject/a2a-inspector) to test interoperability.
See the [A2A Inspector docs](https://github.com/a2aproject/a2a-inspector) for details.
