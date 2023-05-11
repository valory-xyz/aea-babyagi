<h1 align="center">
    <b>AEA BabyAGI</b>
</h1>

### Adaptation of [babyagi](https://github.com/yoheinakajima/babyagi) in the [Open AEA](https://github.com/valory-xyz/open-aea) framework.

## Agents
- **simple_babyagi**: Adaptation of the babyAGI agent loop/functions using only the OpenAI API without extra tooling (NOTE: chromadb, pinecone, and more can be added on just as in babyagi if you want!)
- **agent_agi**: Inherit from Open AEA's "Agent" class to extend babyagi's functionality within simple_babyagi into an Open AEA "Agent" with Finite State Machine Behaviour (FSMBehaviour) (NOTE: this allows for defining states and state transition functions to determine how the agent loop works).
- **aea_babyagi**: Inherit from Open AEA's "AEA" class to extend babyagi's functionality within simple_babyagi & agent_agi into an autonomous economic agent.

## Getting Started

Create a .env file from the .env.example provided in this repo that includes your OpenAI API key and other environment variables you want to use:
```bash
OPENAI_API_KEY="YOUR_API_KEY"
PINECONE_API_KEY="YOUR_API_KEY"
```

paste your AEA's private key in ethereum_private_key.txt:
```bash
0x0000000000000000000000000000000000000000000000000000000000000000
```

Install project dependencies:
```bash
poetry shell
poetry install
```

Import AEA packages:
```bash
svn export https://github.com/valory-xyz/open-aea/tags/v1.33.0/packages packages
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

