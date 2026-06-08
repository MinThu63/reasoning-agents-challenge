Microsoft Agent Framework
Choose a programming language 
Agent Framework offers two primary categories of capabilities:
	Description
Agents
Individual agents that use LLMs to process inputs, call tools and MCP servers, and generate responses. Supports Microsoft Foundry, Anthropic, Azure OpenAI, OpenAI, Ollama, and more.

Workflows
Graph-based workflows that connect agents and functions for multi-step tasks with type-safe routing, checkpointing, and human-in-the-loop support.
The framework also provides foundational building blocks, including model clients (chat completions and responses), an agent session for state management, context providers for agent memory, middleware for intercepting agent actions, and MCP clients for tool integration. Together, these components give you the flexibility and power to build interactive, robust, and safe AI applications.
Get started
Bash 
pip install agent-framework
Python 
    from agent_framework.foundry import FoundryChatClient
    from azure.identity import AzureCliCredential

    credential = AzureCliCredential()
    client = FoundryChatClient(
        project_endpoint="https://your-foundry-service.services.ai.azure.com/api/projects/your-foundry-project",
        model="gpt-5.4-mini",
        credential=credential,
    )

    agent = client.as_agent(
        name="HelloAgent",
        instructions="You are a friendly assistant. Keep your answers brief.",
    )
Python 
    # Non-streaming: get the complete response at once
    result = await agent.run("What is the largest city in France?")
    print(f"Agent: {result}")
That's it — an agent that calls an LLM and returns a response. From here you can add tools, multi-turn conversations, middleware, and workflows to build production applications.
Note
Agent Framework does not automatically load .env files. To use a .env file, call load_dotenv() at the start of your application, or set environment variables directly in your shell or IDE.
When to use agents vs workflows
Use an agent when…	Use a workflow when…
The task is open-ended or conversational	The process has well-defined steps
You need autonomous tool use and planning	You need explicit control over execution order
A single LLM call (possibly with tools) suffices	Multiple agents or functions must coordinate
If you can write a function to handle the task, do that instead of using an AI agent.
Why Agent Framework?
Agent Framework combines AutoGen's simple agent abstractions with Semantic Kernel's enterprise features — session-based state management, type safety, middleware, telemetry — and adds graph-based workflows for explicit multi-agent orchestration.
Semantic Kernel and AutoGen pioneered the concepts of AI agents and multi-agent orchestration. The Agent Framework is the direct successor, created by the same teams. It combines AutoGen's simple abstractions for single- and multi-agent patterns with Semantic Kernel's enterprise-grade features such as session-based state management, type safety, filters, telemetry, and extensive model and embedding support. Beyond merging the two, Agent Framework introduces workflows that give developers explicit control over multi-agent execution paths, plus a robust state management system for long-running and human-in-the-loop scenarios. In short, Agent Framework is the next generation of both Semantic Kernel and AutoGen.
To learn more about migrating from either Semantic Kernel or AutoGen, see the Migration Guide from Semantic Kernel and Migration Guide from AutoGen.
Both Semantic Kernel and AutoGen have benefited significantly from the open-source community, and the same is expected for Agent Framework. Microsoft Agent Framework welcomes contributions and will keep improving with new features and capabilities.
Important
If you use Microsoft Agent Framework to build applications that operate with any third-party servers, agents, code, or non-Azure Direct models ("Third-Party Systems"), you do so at your own risk. Third-Party Systems are Non-Microsoft Products under the Microsoft Product Terms and are governed by their own third-party license terms. You are responsible for any usage and associated costs.
We recommend reviewing all data being shared with and received from Third-Party Systems and being cognizant of third-party practices for handling, sharing, retention and location of data. It is your responsibility to manage whether your data will flow outside of your organization's Azure compliance and geographic boundaries and any related implications, and that appropriate permissions, boundaries and approvals are provisioned.
You are responsible for carefully reviewing and testing applications you build using Microsoft Agent Framework in the context of your specific use cases, and making all appropriate decisions and customizations. This includes implementing your own responsible AI mitigations such as metaprompt, content filters, or other safety systems, and ensuring your applications meet appropriate quality, reliability, security, and trustworthiness standards. See also: Transparency FAQ
Next steps
Go deeper:
•	Agents overview — architecture, providers, tools
•	Workflows overview — sequential, concurrent, branching
•	Integrations — A2A, AG-UI, Azure Functions, M365

Step 1: Your First Agent
Choose a programming language 
Create an agent and get a response — in just a few lines of code.
Bash 
pip install agent-framework
Create and run an agent:
Python 
client = FoundryChatClient(
    project_endpoint="https://your-project.services.ai.azure.com",
    model="gpt-4o",
    credential=AzureCliCredential(),
)

agent = Agent(
    client=client,
    name="HelloAgent",
    instructions="You are a friendly assistant. Keep your answers brief.",
)
Python 
# Non-streaming: get the complete response at once
result = await agent.run("What is the capital of France?")
print(f"Agent: {result}")
Or stream the response:
Python 
# Streaming: receive tokens as they are generated
print("Agent (streaming): ", end="", flush=True)
async for chunk in agent.run("Tell me a one-sentence fun fact.", stream=True):
    if chunk.text:
        print(chunk.text, end="", flush=True)
print()
Note
Agent Framework does not automatically load .env files. To use a .env file for configuration, call load_dotenv() at the start of your script:
Python 
from dotenv import load_dotenv
load_dotenv()
Alternatively, set environment variables directly in your shell or IDE. See the settings migration note for details.
Tip
See the full sample for the complete runnable file.

Step 2: Add Tools
Choose a programming language 
Tools let your agent call custom functions — like fetching weather data, querying a database, or calling an API.
Define a tool with the @tool decorator:
Python 
# NOTE: approval_mode="never_require" is for sample brevity.
# Use "always_require" in production for user confirmation before tool execution.
@tool(approval_mode="never_require")
def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."
Create an agent with the tool:
Python 
agent = Agent(
    client=client,
    name="WeatherAgent",
    instructions="You are a helpful weather agent. Use the get_weather tool to answer questions.",
    tools=[get_weather],
)
Tip
See the full sample for the complete runnable file.

Step 3: Multi-Turn Conversations
Choose a programming language 
Use a session to maintain conversation context so the agent remembers what was said earlier.
Use AgentSession to maintain context across multiple calls:
Python 
client = FoundryChatClient(
    project_endpoint="https://your-project.services.ai.azure.com",
    model="gpt-4o",
    credential=AzureCliCredential(),
)

agent = Agent(
    client=client,
    name="ConversationAgent",
    instructions="You are a friendly assistant. Keep your answers brief.",
)
Python 
# Create a session to maintain conversation history
session = agent.create_session()

# First turn
result = await agent.run("My name is Alice and I love hiking.", session=session)
print(f"Agent: {result}\n")

# Second turn — the agent should remember the user's name and hobby
result = await agent.run("What do you remember about me?", session=session)
print(f"Agent: {result}")
Tip
See the full sample for the complete runnable file.

Step 4: Memory & Persistence
Choose a programming language 
Add context to your agent so it can remember user preferences, past interactions, or external knowledge.
Define a context provider that stores user info in session state and injects personalization instructions:
Python 
class UserMemoryProvider(ContextProvider):
    """A context provider that remembers user info in session state."""

    DEFAULT_SOURCE_ID = "user_memory"

    def __init__(self):
        super().__init__(self.DEFAULT_SOURCE_ID)

    async def before_run(
        self,
        *,
        agent: Any,
        session: AgentSession | None,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """Inject personalization instructions based on stored user info."""
        user_name = state.get("user_name")
        if user_name:
            context.extend_instructions(
                self.source_id,
                f"The user's name is {user_name}. Always address them by name.",
            )
        else:
            context.extend_instructions(
                self.source_id,
                "You don't know the user's name yet. Ask for it politely.",
            )

    async def after_run(
        self,
        *,
        agent: Any,
        session: AgentSession | None,
        context: SessionContext,
        state: dict[str, Any],
    ) -> None:
        """Extract and store user info in session state after each call."""
        for msg in context.input_messages:
            text = msg.text if hasattr(msg, "text") else ""
            if isinstance(text, str) and "my name is" in text.lower():
                state["user_name"] = text.lower().split("my name is")[-1].strip().split()[0].capitalize()
Create an agent with the context provider:
Python 
client = FoundryChatClient(
    project_endpoint="https://your-project.services.ai.azure.com",
    model="gpt-4o",
    credential=AzureCliCredential(),
)

agent = Agent(
    client=client,
    name="MemoryAgent",
    instructions="You are a friendly assistant.",
    context_providers=[UserMemoryProvider()],
)
Run it — the agent now has access to the context:
Python 
session = agent.create_session()

# The provider doesn't know the user yet — it will ask for a name
result = await agent.run("Hello! What's the square root of 9?", session=session)
print(f"Agent: {result}\n")

# Now provide the name — the provider stores it in session state
result = await agent.run("My name is Alice", session=session)
print(f"Agent: {result}\n")

# Subsequent calls are personalized — name persists via session state
result = await agent.run("What is 2 + 2?", session=session)
print(f"Agent: {result}\n")

# Inspect session state to see what the provider stored
provider_state = session.state.get("user_memory", {})
print(f"[Session State] Stored user name: {provider_state.get('user_name')}")
Tip
See the full sample for the complete runnable file.

Step 5: Workflows
Choose a programming language 
Workflows let you chain multiple steps together — each step processes data and passes it to the next.
Define workflow steps (executors) and connect them with edges:
Build and run the workflow:
Tip
See the full sample for the complete runnable file.
Next steps
Go deeper:
•	Workflows overview — understand workflow architecture
•	Sequential workflows — linear step-by-step patterns
•	Agents in workflows — using agents as workflow steps
________________________________________
Additional resources 
Documentation 
•	Step 4: Memory & Persistence 
Add context providers and persistent memory to your agent. 
•	Step 3: Multi-Turn Conversations 
Maintain context across multiple exchanges with AgentSession. 
•	Step 6: Host Your Agent 
Deploy your agent so users and other agents can interact with it. 
•	Step 2: Add Tools 
Give your agent the ability to call functions and interact with the world. 
•	Step 1: Your First Agent 
Create and run your first AI agent with Agent Framework in under 5 minutes. 
•	Microsoft Agent Framework Agent Types - Microsoft Foundry 
Learn different Agent Framework agent types. 
•	Get started with Agent Framework 
A step-by-step tutorial to build your first agent and progressively add tools, conversations, memory, workflows, and hosting. 
•	Microsoft Agent Framework Overview 
Build AI agents and multi-agent workflows in .NET and Python with Microsoft Agent Framework. 

