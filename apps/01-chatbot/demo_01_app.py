import chainlit as cl
from demo_01_client import agent, model_id, AgentEventLogger

# Session variable
session_id = None


@cl.on_chat_start
async def on_chat_start():
    """Initialize the chat session"""
    global session_id
    print("=== Starting new chat session ===")
    session_id = agent.create_session("chat_session")
    print(f"📝 Created agent session: {session_id}")

@cl.set_starters
async def set_starters():
    """Set starter suggestions for the user"""
    print("📱 UI: Setting up starter suggestions...")
    starters = [
        cl.Starter(
            label="What are the key ideas?",
            message="What are the key ideas about doing great work according to Paul Graham?",
        ),
        cl.Starter(
            label="How to find what to work on?",
            message="According to Paul Graham, how do you find what to work on?",
        ),
        cl.Starter(
            label="Role of curiosity?",
            message="What does Paul Graham say about the role of curiosity in doing great work?",
        ),
        cl.Starter(
            label="Dealing with setbacks?",
            message="What advice does Paul Graham give about dealing with setbacks and failures?",
        ),
    ]
    print(f"✅ UI: {len(starters)} starter suggestions configured")
    return starters


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages"""
    global session_id
    print(f"\n📥 UI: Received user message: {message.content}")
    print(f"🔍 UI: Checking system readiness (agent: {agent is not None}, session: {session_id is not None})")
    
    if not agent or not session_id:
        error_msg = "\u26a0\ufe0f System not ready. Please refresh the page."
        print(f"❌ UI: System not ready - {error_msg}")
        print("📤 UI: Sending error response...")
        await cl.Message(error_msg).send()
        print("✅ UI: Error response sent")
        return
    
    try:
        print("🤖 Creating agent response...")
        # Get response from agent
        response = agent.create_turn(
            session_id=session_id,
            messages=[{"role": "user", "content": message.content}],
            stream=True, # TODO: Enable streaming
        )

        # Create empty message for streaming
        msg = cl.Message(content="")
        
        # Stream tokens to Chainlit UI
        for log in AgentEventLogger().log(response):
            log.print()
            # Stream the text content from TurnStreamPrintableEvent
            if hasattr(log, 'content') and log.content:
                await msg.stream_token(log.content)
        
        # Send the completed message
        await msg.send()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        await cl.Message(f"Error: {str(e)}").send()