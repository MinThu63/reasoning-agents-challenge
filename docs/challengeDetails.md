Challenge details
 
Reasoning Agents
Create intelligent agents that solve complex problems through multi-step reasoning
121 projects linked to challenge
Link a project to this challenge
Description
🧠 Reasoning Agents - Starter Kit
Track: Battle #2 - Reasoning Agents with Microsoft Foundry
Welcome to the Reasoning Agents track. In this challenge, you will build a multi-agent system using Microsoft Foundry that demonstrates reasoning, orchestration, grounded knowledge, semantic business understanding, and production-ready deployment patterns.
________________________________________
Prerequisites
Before starting this challenge, ensure you have the following:
Required Skills
•	Basic Python programming — variables, functions, classes, and working with APIs
•	Command line familiarity — navigating directories, running scripts
•	Basic understanding of AI concepts — what LLMs are, prompts, responses, and tool use
Required Accounts (Free Tiers Available)
Account	Purpose	Sign Up
GitHub	Version control and submission	github.com

Microsoft Azure	Access to Microsoft Foundry	azure.microsoft.com/free

Discord	Community support	aka.ms/agentsleague/discord

Required Tools
•	Python 3.10+ — python.org/downloads
•	Visual Studio Code — code.visualstudio.com
•	Git — git-scm.com
Azure Subscription Notes
❗IMPORTANT
Microsoft Foundry requires an Azure subscription. A free trial provides Azure credit for a limited period. Some features may incur costs after the trial. Check the Azure pricing calculator to estimate costs.
⚠️WARNING
Free Tier Limitations: A free Azure subscription can have important constraints that may affect this challenge:
•	Limited model access depending on region and quota
•	Tight rate limits
•	Regional restrictions
•	Some orchestration and evaluation features may require pay-as-you-go
💡Recommendation: For fuller access, consider a pay-as-you-go subscription or explore Azure for Students or Microsoft for Startups Founders Hub.
⏱️ Time Commitment
•	Setup: ~1–2 hours
•	Learning basics: ~4–6 hours
•	Building solution: ~10–20 hours depending on complexity
________________________________________
🛠️ Environment Setup Guidance
Step 1: Initiate your Project Repository
# Create a new directory for your project
mkdir <your-unique-project-name>            
cd <your-unique-project-name>
# Initialize a new Git repository
git init
# Create a README file
echo "# Reasoning Agents Challenge" > README.md
# Create a .gitignore file
echo ".venv/" > .gitignore
echo ".env" >> .gitignore
Step 2: Create a Python Virtual Environment
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
Step 3: Set Up Azure Credentials
1.	Go to Microsoft Foundry Portal
2.	Create or select your Foundry Project
3.	Copy the Project endpoint
4.	Create a .env file in this directory:
# Option 1: Use Project Endpoint (Recommended)
AZURE_AI_PROJECT_ENDPOINT=your-project-endpoint-here

# Option 2: Use Individual Settings
# AZURE_SUBSCRIPTION_ID=your-subscription-id
# AZURE_RESOURCE_GROUP=your-resource-group
# AZURE_AI_PROJECT_NAME=your-project-name

# Model Deployment Name
AZURE_AI_MODEL_DEPLOYMENT=gpt-4o
💡TIP
Keep secrets out of source control. Never commit .env files or credentials to GitHub.
________________________________________
Project Ideas
In this track, we encourage you to create a multi-agent solution using one of the following development approaches.
Development Approaches
1.	Local development: Build and test your custom agent solution locally with the OSS Microsoft Agent Framework.
2.	Cloud-based development: Use Microsoft Foundry to orchestrate agents in the cloud using the UI or SDK.
Whatever approach you choose, you are encouraged to:
•	Use Microsoft Foundry-hosted, GitHub-hosted, or locally-hosted models where appropriate
•	Use visualisation and monitoring tools to understand agent behaviour
•	Integrate external tools, APIs, or MCP servers
•	Implement evaluations and deployment strategies
•	Use AI-assisted development tools such as GitHub Copilot
________________________________________
🌍 Core Challenge Scenario
The challenge scenario is to build a multi-agent enterprise learning system that helps organisations manage internal team certification programmes. The system should be able to:
•	Understand certification requirements mapped to organisational roles
•	Generate team-level and role-based study plans
•	Provide grounded practice questions from approved knowledge sources
•	Offer feedback on team and individual progress
•	Adapt learning schedules to real work context and team capacity
•	Surface manager-level insights across team readiness and risk
Baseline Flow
1.	The learner provides the topics they want to study.
2.	A Learning Path Curator suggests relevant content, based on the learner's goals and role.
3.	A Study Plan Generator converts that content into a practical study schedule, accounting for the learner's workload.
4.	An Engagement Agent keeps the learner on track, adapting reminders to work patterns and focus windows.
5.	Once the learner is ready, an Assessment Agent evaluates readiness using grounded, cited questions.
6.	If the assessment passes, the system recommends the next certification or advancement step. Otherwise, it loops back into the preparation workflow.
7.	A Manager Insights Agent provides visibility into team progress, risk areas, and completion patterns.
💡TIP
Some of these capabilities can be extended with the Microsoft Learn MCP server and the Microsoft Learn MCP documentation.
Example Use Cases
•	An employee requests a a certification study plan that adapts to their workload
•	A manager wants visibility into team learning progress and exam readiness risk areas
•	An assessment agent generates grounded, cited questions from approved organisational knowledge sources
•	A planner agent uses historical study patterns and work signals to recommend realistic study windows
________________________________________
🧠 Microsoft IQ Integration (Core Requirement)
Your project must integrate at least one Microsoft IQ intelligence layer to ground the enterprise learning scenario in real organisational signals. You can choose one, or combine all three.
Work IQ
Work IQ is the intelligence layer that personalises Microsoft 365 Copilot for users and organisations. Microsoft describes it as combining data, context, and skills/tools so Copilot and agents can respond using organisational signals rather than connector-only approaches. It draws from Microsoft 365 tenant data, metadata and activity patterns, and can also incorporate Dynamics 365, Power Apps, and connected business systems through extensibility. Use it when your agent needs to understand work context, collaboration patterns, or where a task fits into the flow of work.
Good fit for this challenge
•	Adapt study reminders around around meetings and focus time
•	Personalise engagement based on each learner's work patterns
•	Ground scheduling and capacity decisions in organisational work context
Reference
•	Work IQ overview
Foundry IQ
Foundry IQ is a configurable, multi-source knowledge layer for Microsoft Foundry. Microsoft states that it provides a knowledge base with knowledge sources and agentic retrieval, returning permission-aware, grounded answers with citations. Supported knowledge sources include internal stores such as Azure Blob Storage, SharePoint, and OneLake, as well as public web data. It uses Azure AI Search for indexing and retrieval infrastructure.
Good fit for this challenge
•	Retrieve certification content from approved documents
•	Ground assessment questions in curated material
•	Provide cited answers from uploaded or indexed knowledge
Reference
•	What is Foundry IQ?
Fabric IQ
Fabric IQ is presented by Microsoft as a semantic foundation within Microsoft Fabric. Microsoft describes it as bringing together data, meaning, and actions into a single semantic layer, with Ontology at the core. That ontology connects people, processes, systems, actions, rules, and data into unified business entities and relationships so people and AI can reason and act with more confidence.
Good fit for this challenge
•	Model the relationship between employee, role, certification, skill gap, pass threshold, and study plan
•	Analyse completion rates, pass likelihoods, and workforce readiness gaps
•	Reuse semantic meaning across analytics, planning, and agent experiences
Reference
•	Fabric IQ: The Semantic Foundation for Enterprise AI
________________________________________
🏗️ Multi-Agent Architecture
At this link you can find a suggested architecture for the enterprise learning and workforce optimisation system, combining multi-agent orchestration with the Microsoft IQ layers.
1. Learning Path Curator Agent
Primary role: Suggest relevant learning paths and supporting material.
Recommended grounding:
•	Foundry IQ knowledge base connected to approved learning content
•	Optional integration with Microsoft Learn MCP server tools
What it should do:
•	Map a certification target to relevant skills and resources
•	Return cited content rather than unsupported free-text recommendations
2. Study Plan Generator Agent
Primary role: Convert learning content into a practical study schedule.
Recommended grounding:
•	Fabric IQ semantic layer for modelling certification, role, skill areas, and recommended study hours
•	Optional use of synthetic historical learner outcomes
What it should do:
•	Recommend milestones at role level
•	Allocate study hours accounting for workload and schedule
•	Adjust sequencing based on difficulty, prerequisites
3. Engagement Agent
Primary role: Keep the learner progressing.
Recommended grounding:
•	Work IQ to understand work context, communication patterns, and preferred timing
What it should do:
•	Suggest appropriate times for reminders based on work rhythm
•	Adapt engagement to individual workload and focus windows
•	Avoid one-size-fits-all reminder behaviour across a diverse team
4. Assessment Agent
Primary role: Evaluate learner readiness.
Recommended grounding:
•	Foundry IQ for grounded question generation
•	Fabric IQ for interpreting patterns and scoring thresholds
What it should do:
•	Generate credible, cited questions from approved content
•	Score or interpret readiness based on known certification criteria
•	Feed results back into the planning loop and surface aggregate team readiness signals
5. Manager Insights Agent
Primary role: Provide team-level visibility into certification readiness and workforce development.
Recommended grounding:
•	Work IQ for organisational context and team capacity signals
•	Fabric IQ for semantic analysis of learning metrics and workforce skill gaps
What it should do:
•	Summarise learning progress by team, role, or certification track
•	Highlight patterns such as capacity-constrained teams or likely exam risk areas
•	Present insights without exposing sensitive personal data
________________________________________
🔄 Example End-to-End Flow
Here's the e-2-e workflow:
1.	A learner asks for help preparing for a certification.
2.	Foundry IQ retrieves grounded learning materials and certification guidance from the approved organisational knowledge base.
3.	Fabric IQ interprets structured data such as required skills by role, recommended study hours, and prior synthetic team study outcomes.
4.	Work IQ helps identify realistic study windows for each team member based on their meeting load and focus patterns.
5.	The Study Plan Generator produces a practical, capacity-aware schedule for the team.
6.	The Engagement Agent uses work context to keep team members on track without disrupting peak work periods.
7.	The Assessment Agent creates grounded questions and evaluates each team member's readiness.
8.	The Manager Insights Agent surfaces team-level progress, risk areas, and readiness summaries.
9.	The system either recommends the next certification step for ready employees or loops back into the study preparation workflow for those who need more time.
________________________________________
📊 Synthetic Data and Documents (Required)
❗IMPORTANT
Use synthetic data only. Do not use real customer data, real employee data, or any PII.
This starter kit requires demo data only and explicitly prohibits customer data, PII, credentials, and confidential information in submissions. In addition, Microsoft’s Foundry synthetic data guidance says to avoid including PII or other sensitive data in the source material used for generation, and to validate outputs before production use.
Synthetic Data Guidance for This Challenge
Use these practical guardrails:
•	Use clearly fabricated identifiers such as L-1001, EMP-001, or TEAM-A
•	Do not use real names, real email addresses, real document titles, or real customer records
•	Keep examples representative but obviously fictional
•	Validate generated outputs before using them in demos or evaluation loops
•	Be explicit in your README that the dataset is synthetic and for demonstration only
Example Synthetic Dataset: Learner Performance
[
  {
    "learner_id": "L-1001",
    "role": "Cloud Engineer",
    "certification": "AZ-204",
    "practice_score_avg": 67,
    "hours_studied": 18,
    "exam_outcome": "Fail"
  },
  {
    "learner_id": "L-1002",
    "role": "DevOps Engineer",
    "certification": "AZ-400",
    "practice_score_avg": 82,
    "hours_studied": 24,
    "exam_outcome": "Pass"
  },
  {
    "learner_id": "L-1003",
    "role": "Data Engineer",
    "certification": "DP-203",
    "practice_score_avg": 74,
    "hours_studied": 20,
    "exam_outcome": "Pass"
  }
]
Example Synthetic Dataset: Work Activity Signals
[
  {
    "employee_id": "EMP-001",
    "meeting_hours_per_week": 22,
    "focus_hours_per_week": 10,
    "preferred_learning_slot": "Morning"
  },
  {
    "employee_id": "EMP-002",
    "meeting_hours_per_week": 15,
    "focus_hours_per_week": 18,
    "preferred_learning_slot": "Afternoon"
  }
]
Example Synthetic Dataset: Fabric IQ Semantic Model Seed
{
  "certifications": [
    {
      "id": "AZ-204",
      "skills": ["API Development", "Azure Functions", "Storage"],
      "recommended_hours": 20
    },
    {
      "id": "AZ-400",
      "skills": ["CI/CD", "Monitoring", "GitHub Actions"],
      "recommended_hours": 25
    }
  ]
}
Example Synthetic Document: Engineering Certification Guide
Engineering Certification Enablement Guide (Synthetic)

Cloud Engineer:
- Primary: AZ-204
- Secondary: AZ-305

DevOps Engineer:
- Primary: AZ-400

Recommended Study Pattern:
- 1–2 hours daily focused study
- Weekly assessment checkpoints
- Target 75% practice score before exam
Example Synthetic Document: Team Learning Report
Quarterly Learning Performance Summary (Synthetic)

Average study time: 21 hours
Pass rate: 68%

Observation:
Learners with more than 20 study hours and more than 75% on practice scores show stronger certification outcomes.
Example Synthetic Document: Workload Insights Report
Workload and Learning Correlation (Synthetic)

Insights:
- Employees with more than 20 meeting hours per week show lower study completion.
- Optimal completion appears when learners have 12–18 meeting hours and at least 15 focus hours.

Recommendation:
Schedule learning blocks during focus-heavy periods.
________________________________________
🧪 Suggested Implementation Pattern
The documentation linked above describes the products and core capabilities. The following is a suggested implementation pattern for this challenge.
Suggested Work IQ Implementation
Use the Work IQ concept as the context layer that informs the Engagement Agent and any user-specific planning logic.
Suggested pattern
•	Treat work signals such as meetings, focus time, and collaboration load as contextual inputs
•	Use those signals to choose study windows, reminder timing, or escalation thresholds
•	Keep outputs supportive and privacy-conscious
Suggested Foundry IQ Implementation
Use Foundry IQ as the grounded knowledge layer for the Learning Path Curator and Assessment Agent.
Suggested pattern
•	Create a knowledge base from synthetic guidance docs, approved learning references, and PDFs or markdown files
•	Connect one or more agents to that knowledge base
•	Require the agent to cite source content when answering questions or generating assessments
Suggested Fabric IQ Implementation
Use Fabric IQ as the semantic layer for business meaning and structured decision support across the enterprise learning system.
Suggested pattern
•	Model entities such as learner, certification, role, skill gap, readiness score, and recommended hours
•	Represent relationships and rules such as prerequisites, role alignment, or pass thresholds
•	Use those semantic structures to inform study recommendations and manager insight summaries
________________________________________
🚀 Hosted Agents in Foundry Agent Service (Recommended for Final Solution)
If you want to deploy the completed solution as a managed agent endpoint, consider Hosted Agents in Foundry Agent Service.
What Hosted Agents Are
Microsoft describes Hosted Agents as a managed platform for deploying and operating AI agents securely and at scale. They are intended for scenarios where open-source or custom agent applications would otherwise require you to manage containerisation, web server setup, security, memory persistence, scaling, instrumentation, and version rollbacks yourself.
Hosted Agents are a good fit when you need to:
•	Bring your own code or framework rather than only prompt definitions
•	Control compute resources such as CPU and memory
•	Run stateful workloads with persisted files and state
•	Expose a dedicated endpoint for your agent
How Hosted Agents Work
Based on Microsoft’s concept documentation:
•	You package your agent as a container image
•	You push that image to Azure Container Registry
•	Foundry Agent Service pulls the image, provisions compute, assigns a dedicated Microsoft Entra ID agent identity, and exposes a dedicated endpoint
•	At runtime, your agent can call Foundry models, tools, and downstream Azure services using that agent identity
•	The platform handles scaling, session state persistence, observability, and lifecycle management
Why Hosted Agents Fit This Challenge
Hosted Agents are suitable for the final solution if you want to:
•	Deploy the full multi-agent implementation rather than only a playground prototype
•	Use Microsoft Agent Framework or your own codebase
•	Separate orchestration logic from model hosting concerns
•	Keep secrets and permissions managed through platform identity rather than embedding them in app code
Suggested Hosted Agent Deployment Pattern for the Challenge
This is a suggested architecture pattern for your submission:
1.	Entry agent hosted in Foundry Agent Service
A top-level hosted agent receives the user request and coordinates the workflow.
2.	Task-specific sub-agents
The hosted solution dispatches work to specialised agents, such as the learning planner, engagement agent, assessment agent, and manager insights agent.
3.	Foundry IQ as the grounding layer
Approved content and synthetic knowledge documents are connected to a knowledge base.
4.	Fabric IQ as the semantic layer
Structured business concepts, relationships, and synthetic metrics guide planning and interpretation.
5.	Work IQ as the work-context layer
Context about work patterns and timing informs engagement and scheduling behaviour.
6.	Observability and evaluation
Use telemetry, logs, and test data to validate that the agent remains grounded, safe, and useful.
Hosted Agent Design Suggestions
These are practical suggestions, not product requirements:
•	Keep the top-level hosted agent focused on orchestration and routing
•	Keep knowledge retrieval separate from semantic analytics where possible
•	Avoid baking secrets into the container image
•	Treat state and files as part of the managed runtime rather than ad hoc local storage assumptions
•	Start with a minimal sandbox size and increase only when justified by your workload
•	Use immutable versions and staged rollout patterns if you iterate beyond a hackathon demo
Hosted Agents References
•	Hosted agents in Foundry Agent Service (preview)
•	Azure AI Foundry agents overview
•	Build a workflow in Microsoft Foundry
________________________________________
🚀 Quick Start Resources
Build your first agent with Microsoft Foundry UI
AI Agent Fundamentals
Build a multi-agent workflow with Microsoft Foundry
Workflow concepts in Microsoft Foundry
Build and orchestrate agents locally with Microsoft Agent Framework
Microsoft Agent Framework tutorials
Understand Work IQ
Work IQ overview
Understand Foundry IQ
What is Foundry IQ?
Understand Fabric IQ
Fabric IQ: The Semantic Foundation for Enterprise AI
Understand Synthetic Data in Foundry
Generate synthetic data with Microsoft Foundry (Preview)
________________________________________
🧠 Reasoning Patterns and Best Practices
When designing your reasoning agents and multi-agent workflows, consider applying well-established reasoning patterns and agentic best practices to improve robustness, transparency, and outcomes.
Common reasoning patterns to explore
1.	Planner–Executor — Separate planning from action execution
2.	Critic / Verifier — Add a validation layer before a final answer is returned
3.	Self-reflection and iteration — Allow review and refinement when confidence is low
4.	Role-based specialisation — Give agents clear responsibilities to reduce overlap
Best practices for building with Microsoft Foundry
•	Use telemetry, trace logs, and visual workflows to understand how agents collaborate
•	Apply evaluation strategies using test cases, scoring rubrics, or human review
•	Build with Responsible AI principles across both application logic and data design
Helpful resources:
•	Foundry Control Plane overview
•	Evaluate generative AI applications in Microsoft Foundry
•	Evaluate AI agents with the Microsoft Foundry SDK
•	Responsible AI in Microsoft Foundry
________________________________________
🔐 Security, Synthetic Data, and Responsible AI
What You Must Not Include
•	Azure API keys, connection strings, or credentials
•	Customer data or personally identifiable information (PII)
•	Confidential or proprietary company information
•	Internal engineering materials not approved for open source
•	Pre-release information under NDA
•	Trade secrets or proprietary algorithms
Security Best Practices
•	Never commit .env files
•	Use environment variables and managed identity where possible
•	Consider Azure Key Vault for production secrets
•	Review .gitignore
•	Scan for secrets before pushing
•	Use demo and synthetic data only
Responsible AI Considerations
When building reasoning agents:
•	Implement guardrails for inputs and outputs
•	Add safety validation where appropriate
•	Test for bias and uneven outcomes across scenarios
•	Be transparent that users are interacting with AI
•	Include human oversight in important decisions
________________________________________
✅ Submission Requirements
To be considered valid, your solution must:
•	Implement a multi-agent system aligned to the challenge scenario
•	Use Microsoft Foundry (UI or SDK) and/or the Microsoft Agent Framework
•	Demonstrate reasoning and multi-step decision-making across agents
•	Integrate with external tools, APIs, and/or MCP where they add real value
•	Integrate at least one Microsoft IQ layer
•	Use synthetic data and synthetic documents only
•	Be demoable and clearly explain the agent interactions
•	Include clear documentation for agent responsibilities, orchestration flow, tools, and data sources
🖊️NOTE
Your solution must align to the challenge scenario, but you do not need to follow the suggested architecture exactly.
Highly Valued Extras
•	Evaluations, telemetry, or observability
•	Advanced reasoning patterns
•	Responsible AI controls and fallbacks
•	A clear hosted deployment story for the final solution
________________________________________
🏆 Evaluation Criteria
Criterion	Impact
Accuracy & Relevance	25% — Meets the challenge requirements and produces relevant outputs
Reasoning & Multi-step Thinking	25% — Demonstrates decomposition, planning, and effective agent collaboration
Creativity & Originality	15% — Shows novel thinking or strong scenario design
User Experience & Presentation	15% — Clear, polished, and demoable
Reliability & Safety	20% — Robust patterns, strong tool/data hygiene, and safe behaviour
________________________________________
Glossary
Term	Definition
Agent	An AI system that can perceive context, make decisions, and take actions toward a goal
Multi-agent system	Multiple specialised agents working together to solve a larger problem
Orchestration	The logic that coordinates agents, tools, and workflow state
LLM	A large language model used for understanding and generation
Prompt	An instruction or input given to a model
MCP	Model Context Protocol, a standard way to connect models to tools and data sources
Foundry IQ	Microsoft Foundry’s multi-source, permission-aware grounding layer for agents
Work IQ	The Microsoft 365 Copilot intelligence layer built from data, context, and skills/tools
Fabric IQ	The semantic intelligence layer in Microsoft Fabric built around ontology and business meaning
Hosted Agent	A containerised custom agent deployed to Foundry Agent Service with managed hosting
Telemetry	Data collected about behaviour, performance, traces, and quality
Guardrails	Safety mechanisms that constrain harmful or incorrect outputs
Evaluation	The process of measuring quality, grounding, and reliability
________________________________________
🔧 Troubleshooting
Issue	Suggested Response
ModuleNotFoundError: No module named 'azure'	Ensure dependencies are installed in the active virtual environment
Authentication errors	Check environment variables and permissions
Retrieval quality is poor	Review the knowledge source content and grounding design
Agent answers are generic	Tighten agent role instructions and improve grounding sources
Synthetic data looks too realistic	Replace any potentially sensitive values and simplify identifiers
Reminder logic feels unrealistic	Revisit how contextual work signals are interpreted
Getting Help
1.	Search existing GitHub Issues
2.	Ask in the Discord #agentsleague channel
3.	Open a new issue using the repository template
________________________________________
Additional Resources
•	Microsoft Foundry documentation
•	Microsoft Foundry Agent Service overview
•	Microsoft Agent Framework documentation
•	Microsoft Agent Framework GitHub repository
•	AI Agents for Beginners
•	GitHub Copilot resources
•	Microsoft Learn MCP server repository
•	Generate synthetic data with Microsoft Foundry (Preview)
________________________________________
✅ Summary
This challenge is designed to help you demonstrate:
•	Multi-agent system design
•	Grounded enterprise retrieval with Foundry IQ
•	Context-aware reasoning with Work IQ
•	Semantic business understanding with Fabric IQ
•	Safe demo construction using synthetic data
•	Production-minded deployment through Hosted Agents
A strong submission will show not just that agents can answer questions, but that they can reason across organisational knowledge, work context, and structured business meaning in a way that is safe, explainable, and demoable at enterprise scale.
________________________________________
Questions? Join Discord #agentsleague channel
Resources-Modules
🚀 Quick Start Resources
Build your first agent with Microsoft Foundry UI
AI Agent Fundamentals
Build a multi-agent workflow with Microsoft Foundry
Workflow concepts in Microsoft Foundry
Build and orchestrate agents locally with Microsoft Agent Framework
Microsoft Agent Framework tutorials
Understand Work IQ
Work IQ overview
Understand Foundry IQ
What is Foundry IQ?
Understand Fabric IQ
Fabric IQ: The Semantic Foundation for Enterprise AI
Understand Synthetic Data in Foundry
Generate synthetic data with Microsoft Foundry (Preview)
•	Microsoft Foundry documentation
•	Microsoft Foundry Agent Service overview
•	Microsoft Agent Framework documentation
•	Microsoft Agent Framework GitHub repository
•	AI Agents for Beginners
•	GitHub Copilot resources
•	Microsoft Learn MCP server repository
•	Generate synthetic data with Microsoft Foundry (Preview)

Architecture
 

3 Layers
1. Work IQ: The "People & Productivity" Brain
This layer understands how you work. 
•	What it looks at: Your emails, Teams chats, calendar meetings, and personal documents (Microsoft 365). 
•	What it does: It maps out who you collaborate with and what projects you are actively discussing. It gives the AI "memory" so it understands your daily habits and can help you draft emails or summarize meetings based on your actual workflow. 
2. Fabric IQ: The "Numbers & Analytics" Brain
This layer understands the hard business data. 
•	What it looks at: Databases, sales figures, inventory systems, and analytics (Microsoft Fabric / Power BI). 
•	What it does: It turns raw numbers into unified business concepts. If an AI agent needs to know your "Gross Revenue" or "Active Customers," Fabric IQ ensures it pulls the exact, mathematically correct data instead of guessing. 
3. Foundry IQ: The "Company Knowledge" Brain
This layer acts as the company librarian.
•	What it looks at: Company policies, HR manuals, technical documentation, contracts, and wikis. 
•	What it does: It securely searches through all your company's unstructured files to find the exact rules and facts needed to answer a question. This is the layer that ensures the AI grounds its answers in your company's actual rulebook so it doesn't hallucinate information. 
In short: Work IQ knows your team's chats, Fabric IQ knows your sales metrics, and Foundry IQ knows the company rulebook. When you build an agent for the hackathon, you are choosing which of these "brains" your agent needs to tap into to do its job. 

Difference between Traditional & Modern AI Frameworks
From traditional AI frameworks to agentic AI
To understand what makes AI agent frameworks different, it helps to first look at what traditional AI frameworks provide.
Traditional AI frameworks: Enhancing apps with intelligence
Traditional AI frameworks help developers integrate intelligent capabilities into applications. These frameworks improve performance and user engagement in several key ways:
•	Personalization:
AI can analyze user behavior and preferences to deliver tailored recommendations and experiences.
Example: Streaming platforms like Netflix suggest shows and movies based on viewing history, enhancing engagement.
•	Automation and efficiency:
AI automates repetitive tasks and streamlines workflows, improving operational efficiency.
Example: AI chatbots in customer service handle common inquiries, reducing response times and freeing human agents for complex issues.
•	Enhanced user experience:
AI introduces features like natural language processing, voice recognition, and predictive text.
Example: Virtual assistants like Siri and Google Assistant understand voice commands, making device interactions more intuitive.
Beyond traditional AI: The rise of AI agent frameworks
While traditional AI enhances applications, AI Agent Frameworks go further by enabling the development of autonomous, goal-oriented agents. These agents don't just process data—they reason, act, and learn to achieve objectives.
Key capabilities include:
•	Agent collaboration and coordination:
Supports multiple agents that communicate, share information, and work together to solve complex problems.
•	Task automation and management:
Automates multi-step workflows and dynamic task delegation across agents for more efficient operations.
•	Contextual understanding and adaptation:
Enables agents to perceive context, make decisions based on real-time data, and adapt to changing environments.
Recommendation
 

Current Agents
1. Study Plan Generator Agent
•	Primary Role: Convert the learning content (suggested by your Curator agent) into a practical study schedule.
•	What it must do: It should recommend milestones at the role level, allocate study hours while accounting for the employee's workload and schedule, and adjust the sequencing based on difficulty and prerequisites.
•	Recommended Grounding: Use Fabric IQ to model certifications, roles, skill areas, and recommended study hours.
2. Engagement Agent
•	Primary Role: Keep the learner progressing and on track.
•	What it must do: It must suggest appropriate times for reminders based on the learner's work rhythm, adapt engagement to individual workloads, and avoid sending one-size-fits-all reminders to everyone.
•	Recommended Grounding: Use Work IQ to understand the employee's work context, communication patterns, and preferred timing.
3. Assessment Agent
•	Primary Role: Evaluate learner readiness.
•	What it must do: It must generate credible, cited practice questions from approved content, score or interpret readiness based on certification criteria, and feed the results back into the system to either recommend the actual exam or loop the user back for more study.
•	Recommended Grounding: Use Foundry IQ to ground the question generation in your fake company rules, and Fabric IQ to interpret the scoring thresholds.
4. Manager Insights Agent
•	Primary Role: Provide team-level visibility into certification readiness and workforce development.
•	What it must do: It should summarize learning progress by team, role, or certification track, highlight patterns (like capacity-constrained teams or exam risk areas), and present these insights without exposing sensitive personal data.
•	Recommended Grounding: Use Work IQ for team capacity signals and Fabric IQ to analyze the learning metrics and skill gaps.
5. Entry Agent (Dispatcher)
•	Primary Role: Orchestrate the entire workflow.
•	What it must do: This is the top-level agent that receives the initial user request and acts as the coordinator, dispatching tasks to the specialized sub-agents listed above. It should focus strictly on routing and orchestration.

Traditional RAG vs Agentic Retrieval
 
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

•	Unlocking Knowledge for Agents: Foundry IQ acts as a managed knowledge layer and a single endpoint for your agents, replacing the need to build custom, fragile RAG (Retrieval-Augmented Generation) pipelines from scratch. It unifies fragmented enterprise data into topic-centric "Knowledge Bases" so agents can access permissions-aware information without knowing where the data originally lives.
•	Building the Data Pipeline (Knowledge Sources): This covers how data actually enters the system. Knowledge Sources can be either "indexed" (where Foundry IQ copies, chunks, and vectorizes data from places like Azure Blob or OneLake into an Azure AI Search index) or "remote" (queried directly at runtime, such as Bing web search, Remote SharePoint, or external systems via MCP servers).
•	Querying Multi-Source Knowledge Bases: This explains the agentic retrieval process. When an agent receives a complex question, the Knowledge Base performs query planning (breaking the question down into focused subqueries), routes them in parallel to the appropriate Knowledge Sources, and then reranks and merges the results. You can control the cost, speed, and depth of this process using "Retrieval Reasoning Effort" levels (minimal, low, or medium).



