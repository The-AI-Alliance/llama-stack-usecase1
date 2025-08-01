import os
from dotenv import load_dotenv
from llama_stack_client import Agent, AgentEventLogger, RAGDocument, LlamaStackClient

# Load environment variables
load_dotenv()

# Configuration
vector_db_id = os.getenv("VECTOR_DB_ID", "my_demo_vector_db")
llama_stack_url = os.getenv("LLAMA_STACK_ENDPOINT", "http://localhost:5000")
model_id = os.getenv("INFERENCE_MODEL")

# Initialize client
print(f"🔌 Connecting to Llama Stack API at {llama_stack_url}...")
client = LlamaStackClient(base_url=llama_stack_url, timeout=120)
print("✅ Connected to API")

# Get models
print("🔍 Loading models...")
models = client.models.list()

# Select the first LLM and first embedding models
if not model_id:
    model_id = next(m for m in models if m.model_type == "llm").identifier
embedding_model = next(m for m in models if m.model_type == "embedding")
embedding_model_id = embedding_model.identifier
embedding_dimension = embedding_model.metadata["embedding_dimension"]

print(f"🚀 Using LLM: {model_id}")
print(f"🧠 Using embedding: {embedding_model_id}")

# Setup vector DB
print(f"📊 Setting up vector database: {vector_db_id}...")
_ = client.vector_dbs.register(
    vector_db_id=vector_db_id,
    embedding_model=embedding_model_id,
    embedding_dimension=embedding_dimension,
    provider_id="faiss",
)
print("✅ Vector database ready")

# Load document
source = "https://www.paulgraham.com/greatwork.html"
print("rag_tool> Ingesting document:", source)
document = RAGDocument(
    document_id="document_1",
    content=source,
    mime_type="text/html",
    metadata={},
)

client.tool_runtime.rag_tool.insert(
    documents=[document],
    vector_db_id=vector_db_id,
    chunk_size_in_tokens=50,
)
print("✅ Document loaded and indexed")

# Create agent
print("🤖 Creating AI agent...")
agent = Agent(
    client,
    model=model_id,
    instructions="You are a helpful assistant with access to knowledge search tools. When answering questions, first search for relevant information using your available tools before providing a response.",
    tools=[
        {
            "name": "builtin::rag/knowledge_search",
            "args": {"vector_db_ids": [vector_db_id]},
        }
    ],
)
print("✅ System initialized successfully")

# Export for use in other modules
__all__ = ['client', 'agent', 'model_id', 'AgentEventLogger']


def main():
    """Main function that replicates demo_script.py behavior"""
    
    # First: Non-streaming response
    prompt1 = "How do you do great work?"
    print("prompt (non-streaming)>", prompt1)
    
    response = agent.create_turn(
        messages=[{"role": "user", "content": prompt1}],
        session_id=agent.create_session("rag_session"),
        stream=False,
    )
    
    # TODO: This throws an exception for some kinds of responses!!
    # for log in AgentEventLogger().log(response):
    #     log.print()
    
    print("\n" + "="*50 + "\n")
    
    # Second: Streaming response
    prompt2 = "What are the key principles mentioned about doing great work?"
    print("prompt (streaming)>", prompt2)
    
    response = agent.create_turn(
        messages=[{"role": "user", "content": prompt2}],
        session_id=agent.create_session("rag_session_streaming"),
        stream=True,
    )
    
    for log in AgentEventLogger().log(response):
        log.print()


if __name__ == "__main__":
    main()