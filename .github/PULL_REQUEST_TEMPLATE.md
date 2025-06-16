## Purpose
<!-- Describe the RAG pattern change, agent improvement, or feature being implemented. What problem does it solve? -->
* ...

## Does this introduce a breaking change?
<!-- Mark one with an "x". -->
```
[ ] Yes
[ ] No
```

## Pull Request Type
What kind of change does this Pull Request introduce?

<!-- Please check the one that applies to this PR using "x". -->
```
[ ] Bugfix
[ ] New RAG pattern or agent workflow
[ ] Frontend UI improvement
[ ] Backend API enhancement
[ ] Agent configuration update
[ ] Documentation content changes
[ ] Infrastructure/deployment change
[ ] Code style update (formatting, local variables)
[ ] Refactoring (no functional changes, no api changes)
[ ] Other... Please describe:
```

## Components Changed
<!-- Mark all that apply with "x" -->
```
[ ] Backend agents (Retriever, Writer, Verifier, Curator)
[ ] FastAPI endpoints and streaming responses
[ ] Frontend React components and pages
[ ] Agent configuration (agent_configs.yaml)
[ ] Azure service integration
[ ] Document processing pipeline
[ ] Testing infrastructure
```

## How to Test
*  Get the code

```
git clone [repo-address]
cd adaptive-rag-workbench
git checkout [branch-name]
```

* Install dependencies and test
```
make install
make test
```

* Run the application locally
```
make dev
```

## RAG Pattern Testing
<!-- If applicable, describe which RAG patterns were tested -->
* Test Context-Aware Generation: [ ]
* Test Agentic QA with Verification: [ ]  
* Test Adaptive Knowledge Base Management: [ ]
* Test streaming responses: [ ]
* Test agent orchestration: [ ]

## What to Check
Verify that the following are valid
* All async patterns are implemented correctly
* Agent workflows handle errors gracefully
* Environment variables are properly configured
* Type hints and Pydantic models are accurate
* Frontend components follow Microsoft design patterns
* ...

## Other Information
<!-- Add any other helpful information about Azure services, configuration changes, or deployment considerations -->