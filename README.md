<h1 align="center">
    <b>AEA BabyAGI</b>
</h1>

### Adaptation of [babyagi](https://github.com/yoheinakajima/babyagi) in the [Open AEA](https://github.com/valory-xyz/open-aea) framework.

## Project
```ml
├─ actions — "contains all the functions used to compose the low-high level actions of each agent"
├─ simple_babyagi — "Adaptation of the babyAGI agent loop/functions using only the OpenAI API without extra tooling"
├─ agent_babyagi - "Use Open AEA's Agent class to extend simple_babyagi into an Open AEA "Agent" with Finite State Machine Behaviour"
├─ aea_babyagi - "Inherit from Open AEA's "AEA" class to extend babyagi's functionality within agent_agi into an autonomous economic agent."
```

## Getting Started

Create a `.env` file from the `.env.example` provided in this repo:
```bash
cp .env.example .env
```

Set your OpenAI API key and, optionally, other environment variables you want to use in the `.env` file:
```bash
OPENAI_API_KEY="YOUR_API_KEY"
PINECONE_API_KEY="YOUR_API_KEY"
```

Install project dependencies (you can find install instructions for Poetry [here](https://python-poetry.org/docs/)):
```bash
poetry shell
poetry install
```

Import AEA packages:
```bash
svn export https://github.com/valory-xyz/open-aea/tags/v1.33.0/packages packages
```

Source the environment variables:
``` bash
source .env
```

Run the agents:
```bash
poetry run python simple_babyagi.py "develop a task list" "solve world hunger"
``` 
```bash
poetry run python agent_babyagi.py "develop a task list" "solve world hunger"
``` 
```bash
poetry run python aea_babyagi.py "develop a task list" "solve world hunger"
```
