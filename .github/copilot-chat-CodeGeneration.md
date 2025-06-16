# Copilot Chat – Code Generation

- Target **FastAPI** with **Python 3.12** for backend API development and agent orchestration.
- Use **Semantic Kernel** for AI agent workflows with proper async patterns throughout.
- Implement **streaming chat endpoints** using FastAPI's `StreamingResponse` for real-time interactions.
- Build **agent classes** (Retriever, Writer, Verifier, Curator) following the established patterns.
- Use **Pydantic models** for request/response validation and configuration management.
- Implement **React/TypeScript** frontend with **Radix UI** components and **Tailwind CSS**.
- Follow **async patterns** for Azure SDK calls (`BlobServiceClient`, `SearchClient`, etc.).
- Add comprehensive **type hints** and Google-style docstring summaries.
- Use `logging` at INFO level for proper observability; never use `print`.
- Access secrets via **environment variables** or Pydantic Settings; no hard-coded strings.
- Structure code in `backend/app/agents/` with proper registration in `agent_configs.yaml`.
- Implement **RAG patterns** with citation tracking and confidence scoring.
