import os
from dotenv import load_dotenv
from llama_stack_client import Agent, AgentEventLogger, RAGDocument, LlamaStackClient

load_dotenv()

vector_db_id = os.getenv("VECTOR_DB_ID", "my_demo_vector_db")
llama_stack_url = os.getenv("LLAMA_STACK_API_URL", "http://localhost:5000")
client = LlamaStackClient(base_url=llama_stack_url, timeout=120)

models = client.models.list()

# Select the first LLM and first embedding models
model_id = next(m for m in models if m.model_type == "llm").identifier
embedding_model_id = (
    em := next(m for m in models if m.model_type == "embedding")
).identifier
embedding_dimension = em.metadata["embedding_dimension"]

try:
    _ = client.vector_dbs.register(
        vector_db_id=vector_db_id,
        embedding_model=embedding_model_id,
        embedding_dimension=embedding_dimension,
        provider_id="faiss",
    )
except:
    pass

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

prompt = "how to do great work?"
print("prompt>", prompt)

response = agent.create_turn(
    messages=[{"role": "user", "content": prompt}],
    session_id=agent.create_session("test_session"),
    stream=True,
)

print("\n=== Analyzing log events ===")
for i, log in enumerate(AgentEventLogger().log(response)):
    if i>10:
        break
    print(f"\nEvent {i}:")
    print(f"  Type: {type(log)}")
    if hasattr(log, 'event'):
        print(f"  Event type: {type(log.event)}")
        if hasattr(log.event, 'payload'):
            print(f"  Payload type: {type(log.event.payload)}")
    print("  Printing log:")
    log.print()