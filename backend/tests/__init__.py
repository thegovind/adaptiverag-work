
<create_file path="/home/ubuntu/repos/adaptive-rag-workbench/backend/tests/test_agents.py">
import pytest
from app.agents.orchestrator import OrchestratorAgent
from app.agents.retriever import RetrieverAgent
from app.agents.writer import WriterAgent
from app.agents.verifier import VerifierAgent
from app.agents.curator import CuratorAgent
from semantic_kernel import Kernel

@pytest.fixture
def kernel():
    return Kernel()

@pytest.fixture
def orchestrator(kernel):
    return OrchestratorAgent(kernel)

@pytest.fixture
def retriever(kernel):
    return RetrieverAgent(kernel)

@pytest.fixture
def writer(kernel):
    return WriterAgent(kernel)

@pytest.fixture
def verifier(kernel):
    return VerifierAgent(kernel)

@pytest.fixture
def curator(kernel):
    return CuratorAgent(kernel)

@pytest.mark.asyncio
async def test_orchestrator_create_plan(orchestrator):
    plan1 = await orchestrator.create_plan({"exercise": "exercise1"})
    assert plan1 == ["RetrieverAgent", "WriterAgent"]
    
    plan2 = await orchestrator.create_plan({"exercise": "exercise2"})
    assert plan2 == ["RetrieverAgent", "VerifierAgent", "WriterAgent"]
    
    plan3 = await orchestrator.create_plan({"exercise": "exercise3"})
    assert plan3 == ["CuratorAgent"]

@pytest.mark.asyncio
async def test_retriever_invoke(retriever):
    docs = await retriever.invoke("test query")
    assert isinstance(docs, list)
    assert len(docs) > 0
    assert "content" in docs[0]
    assert "company" in docs[0]

@pytest.mark.asyncio
async def test_writer_invoke_stream(writer):
    mock_docs = [{"content": "test content", "company": "Apple", "year": 2024}]
    tokens = []
    async for token in writer.invoke_stream(mock_docs, "test query"):
        tokens.append(token)
    
    response = "".join(tokens)
    assert len(response) > 0
    assert "Apple" in response

@pytest.mark.asyncio
async def test_verifier_invoke(verifier):
    mock_docs = [{"content": "test content", "company": "Apple", "year": 2024}]
    verified_docs = await verifier.invoke(mock_docs, "test query")
    
    assert len(verified_docs) == 1
    assert "confidence" in verified_docs[0]
    assert "verified" in verified_docs[0]
    assert isinstance(verified_docs[0]["confidence"], float)

@pytest.mark.asyncio
async def test_curator_invoke_stream(curator, tmp_path):
    test_file = tmp_path / "test.pdf"
    test_file.write_text("test content")
    
    tokens = []
    async for token in curator.invoke_stream(str(test_file)):
        tokens.append(token)
    
    response = "".join(tokens)
    assert "Starting document processing" in response
    assert "Successfully indexed" in response
