# Gaby AI: Autonomous Data Cleaning, Analyst, Insights & Scraper!

This project is for the (Kaggle Google BigQuery AI)[https://www.kaggle.com/competitions/bigquery-ai-hackathon/writeups] submission.

Gaby AI is an autonomous data cleaning agent using BigQuery AI as his personal Memory **Gatekeeper**.

Leveraged BigQuery Methods:

- AI.GENERATE for field descriptions
- AI.GENERATE_TABLE for missing data strategies
- Vector search for semantic field matching

## Demo Streamlit App: How it works:

To this date, Gaby AI is an autonomous data cleaning agent using BigQuery AI as reasoning engine.

1. User uploads dataset via Streamlit → DataProfiler creates episode
2. Local analysis (pandas) generates field summaries → BigQuery storage
3. Gaby agents (DatasetSummarizer, FieldDescription) process via prompts
4. BigQuery AI.GENERATE creates contextual field descriptions at scale
5. Results displayed in Streamlit with learning stored for future episodes
6. Reinforcement learning improves strategies based on success metrics

## Directory Structure

```text
.
├── docker-compose.yml          # Setup Agent with Dockers.
├── notebooks                  # Jupyter notebooks for experimentation and analysis
├── pyproject.toml            # Modern Python project configuration and dependencies
├── README.md                 # Project documentation and setup instructions
├── requirements.txt          # Python package dependencies
├── scripts                   # Automation scripts for deployment and maintenance
├── server                    # Backend server components and API endpoints
├── src                       # Main source code directory
│   └── gaby_agent           # Core Gaby AI agent package
│       ├── app.py           # Main Streamlit application entry point
│       ├── core             # Core business logic and agent functionality
│       │   ├── agent        # Local Agent functions / handlers / utils.
│       │   ├── config.py    # Workspace Configuration setup.
│       │   ├── gatekeeper   # BigQuery AI/ML integration and data access layer.
│       │   ├── pipeline.py  # Base Procedure for ETL processing pipelines and workflows
│       │   └── schema.py    # Database schema definitions and validation
│       ├── data             # Stores user's data input and cleaned data output
```

## Objective

To build autonomous human-like agent to reason all types of datasets. On a more realistic note, an agent that lives at the heart of all data teams.

## Architecture
```text
                            ┌─────────────────────────────┐
                            │    Streamlit Web App        │
                            │  (Gaby UI, file upload,     │
                            │   tag management, results)  │
                            └────────────┬────────────────┘
                                         │ user interactions
                                         ▼
                    ┌─────────────────────────────────────────────────┐
                    │              Gaby Agent Core                    │
                    │  (GabyBasement, Instructor, DataProfiler,      │
                    │   episode management, config validation)       │
                    └────────┬─────────────┬─────────────┬───────────┘
                             │             │             │
        data cleaning /      │  reasoning  │  SQL gen /  │  RL learning /
        profiling            │  prompts    │  execution  │  observations
                             ▼             ▼             ▼
    ┌─────────────────────┐  ┌──────────────────┐  ┌─────────────────────┐
    │   Stage Processors  │  │   Local LLMs     │  │  Policy & Learning  │
    │ - DatasetSummarizer │◄─┤ (Ollama/Gemini   │  │ - Reward tracking   │
    │ - FieldDescription  │  │  for reasoning &  │  │ - Episode storage   │
    │ - MissingAnalysis   │  │  field analysis)  │  │ - Strategy updates  │
    │ - Schema Detection  │  │                  │  │ - Observation store │
    └─────────┬───────────┘  └─────────┬────────┘  └─────────┬───────────┘
              │                        │                     │
              │ pandas operations      │ prompt/response     │ learning
              │ & data validation      │ for descriptions    │ artifacts
              ▼                        ▼                     ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │                         Google BigQuery                             │
    │  Data Layer:                                                        │
    │  - cleaning_service.sample_dataset (raw data)                      │
    │  - cleaning_service.field_summary (column analysis)                │
    │  - observations.* (agent learning history)                         │
    │  - cognitive.* (decision patterns & policies)                      │
    │  - cleaned_data.* (processed output datasets)                      │
    │                                                                     │
    │  AI/ML Layer:                                                       │
    │  - AI.GENERATE (field descriptions, missing data strategies)       │
    │  - AI.GENERATE_TABLE (structured data generation)                  │
    │                                                                     │
    │  Infrastructure:                                                    │
    │  - Remote models (Gemini 2.5 Flash via endpoints)                  │
    │  - Audit logs, policy checkpoints, staging tables                  │
    │  - Real-time query execution with pandas_gatekeeper decorator      │
    └─────────────────────────────────────────────────────────────────────┘
              ▲                         ▲                          ▲
              │ upload & analyze        │ AI-generated insights    │ store learning
              │ dataset summaries       │ & field descriptions     │ & observations
              │                         │                          │
    ┌─────────┴───────────┐   ┌─────────┴──────────┐   ┌─────────┴───────────┐
    │  Python Libraries   │   │  BigQuery Wrapper  │   │   MCP Integration   │
    │ - pandas (local)    │   │ - @pandas_gatekeeper│   │ - Model Context     │
    │ - pathlib (files)   │   │ - SQL generators    │   │   Protocol support │
    │ - uuid (episodes)   │   │ - Error handling    │   │ - Agent sandboxing  │
    └─────────────────────┘   └────────────────────┘   └─────────────────────┘
```

## Reinforcement Learning Methods

These lightmodels depend on BigQuery ML methods to assist in agent's feedback loop and dedecision-makng pocesses.

```text
Agent Learning Summary

   ┌─────────────────────┐          ┌───────────────────────────┐
   │                     │ Actions  │                           │
   │   Agent (Gaby AI)   ├─────────►│   BigQuery SQL + AI/ML    │
   │                     │          │   (AI.GENERATE_*, ML.*)   │
   └─────────────────────┘          └───────────────────────────┘
              ▲                               │
              │ Predicted Rewards/Policies    │ Data Access & Processing
              │                               ▼
   ┌─────────────────────┐          ┌───────────────────────────┐
   │ Reward Trajectory   │◄─────────┤  Environment (Datasets)   │
   │   Projection        │  New     │ (raw + processed tables)  │
   │ (Forecast States)   │  Insights└───────────────────────────┘
   └─────────────────────┘
```

## Dataset used for testing / validation

Cafe Sales Dataset Source:

https://www.kaggle.com/account/login?titleType=dataset-downloads&showDatasetDownloadSkip=False&messageId=datasetsWelcome&returnUrl=%2Fdatasets%2Fahmedmohamed2003%2Fcafe-sales-dirty-data-for-cleaning-training%2Fversions%2F1%3Fresource%3Ddownload

Other sample datasets were generated by Gemini.

## TODO

*AI/ML & Data Science Stack*
- Remove the Cognitive states since is standalone app for comp.
- Orchestrating agent as controller architecture.

*Backend*
xx Revise directory / file paths e.g. add default setup for Google.
- Upload Model with BigQUery on GIT
- Add MCP Server (Python based) to connect to external tools

*Frontend*
- Improve frontend e.g. enable user to add level of unclean-ness
- Add DB IP connection routes.
- Add Assets

*House Keeping*
- Fix writing in docs
- Add Post Stage Actions
