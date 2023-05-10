# aea-babyagi

Adaptation of [babyagi](https://github.com/yoheinakajima/babyagi) in the [Open AEA](https://github.com/valory-xyz/open-aea) framework.

- simple_babyagi: minimal recreation of babyAGI loop and functions using only the OpenAI API without extra tooling (NOTE: chromadb, pinecone, etc, can be added on just as in babyagi if you want)
- agent_agi: Inherit from Open AEA's "Agent" class to extend babyagi's functionality within simple_babyagi, into an Open AEA "Agent" with Finite State Machine Behaviour (FSMBehaviour) (NOTE: this allows for defining states and state transition functions to determine how the agent loop works).
- aea_babyagi: Inherit from Open AEA's "AEA" class to extend babyagi's functionality within simple_babyagi & agent_agi into an autonomous economic agent.

## Getting Started

Create a .env file from the .env.example provided in this repo that includes your OpenAI API key and other environment variables you want to use:
```bash
OPENAI_API_KEY="YOUR_API_KEY"
PINECONE_API_KEY="YOUR_API_KEY"
```

Install project dependencies:
```bash
poetry shell
poetry install
```

Run the agents:
```bash
poetry run python simple_babyagi.py "develop a task list" "solve world hunger"
``` ```bash
poetry run python agent_babyagi.py "develop a task list" "solve world hunger"
``` ```bash
poetry run python aea_babyagi.py "develop a task list" "solve world hunger"
```

