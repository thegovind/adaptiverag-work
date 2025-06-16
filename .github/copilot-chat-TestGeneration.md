# Copilot Chat – Test Generation

- Use **pytest** + **pytest-asyncio** for backend testing with proper async test patterns.
- Use **FastAPI TestClient** for testing API endpoints and streaming response validation.
- Mock Azure SDK calls (`SearchClient`, `BlobServiceClient`) with `unittest.mock.AsyncMock`.
- Test **agent workflows** with proper mocking of LLM calls and multi-agent orchestration.
- Aim for comprehensive coverage of **RAG patterns**, document processing, and citation tracking.
- Test **streaming chat endpoints** with proper connection handling and error scenarios.
- For frontend, use **React Testing Library** + **Jest** for component and user interaction tests.
- Keep test fixtures self-contained with realistic but small payloads; no external dependencies.
