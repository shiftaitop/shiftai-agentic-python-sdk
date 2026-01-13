# Shiftai Agentic Infra Python SDK

This SDK is the official gateway to the Shift AI Agentic Infra services, enabling developers to directly integrate and use agentic capabilities in their applications.





## Dependencies

### Allowed Dependencies (Only These)

- ✅ `httpx` - Async HTTP client (required for API calls)
- ✅ `dataclasses` - Standard library (for data models)
- ✅ `typing` - Standard library (for type hints)
- ✅ Standard library only: `json`, `datetime`, `uuid`, `asyncio`
- ✅ SDK internal modules - All models and utilities owned by SDK



## Installation & Usage Modes



### Package Usage 

```bash
pip install shiftaiagenticinfra-sdk-python
```

## Quick Start

```python
import asyncio
from shiftai import ShiftaiagenticinfraClient

async def main():
    # 1. Initialize client
    client = ShiftaiagenticinfraClient(
        base_url="api.theshiftai.in",
        api_key="pk_your_api_key"
    )

    # 2. Send a human message
    human_response = await client.messages.send_human_message(
        username="john_doe",
        message="Hello, how can I help you?",
        agent_name="SupportBot",
        agent_platform="OpenAI",
        agent_version="1.0.0"  # Required: Agent version 
    )

    print(f"Message sent! ID: {human_response.messageId}")

    # 3. Send a bot response
    bot_response = await client.messages.send_bot_message(
        username="john_doe",
        message="I can help you with your questions!",
        agent_name="SupportBot",
        agent_platform="OpenAI",
        agent_version="1.0.0",  # Required: Agent version 
        reply_message_id=human_response.messageId,
        rag_context="Retrieved context from knowledge base..."
    )

    # 4. Get analytics
    dashboard = await client.analytics.get_dashboard()
    print(f"Total users: {dashboard.totalUsers}")

    # 5. Close client
    await client.close()

asyncio.run(main())
```

This example imports and runs immediately when the SDK source is copied into any Python project with httpx installed.

## API Reference

### Platform API

#### `await platform.register(project_name, metadata=None)`
Register a new project and get API key.

**Parameters:**
- `project_name` (str, **required**): Unique name for the project/platform (e.g., "my-chatbot", "customer-support-app")
- `metadata` (dict, **optional**): Additional project metadata (e.g., `{"environment": "production", "version": "1.0"}`)

**Return Type:** `PlatformRegistrationResponse`

**Example:**
```python
response = await client.platform.register(
    project_name="MyProject",
    metadata={"environment": "production"}
)
print(f"API Key: {response.apiKey}")
```

### Messages API

#### `await messages.send_human_message(...)`
Send a human message with automatic user/agent creation.

**Parameters:**
- `username` (str, **required**): User identifier (e.g., "john_doe", "user123")
- `message` (str, **required**): The actual message content (e.g., "Hello, how can I help you?")
- `agent_name` (str, **required**): Target agent name (e.g., "SupportBot", "GPT-4")
- `agent_platform` (str, **required**): Agent platform/provider (e.g., "OpenAI", "Azure", "Anthropic")
- `user_email` (str, **required**): User's email address for identification (e.g., "john@example.com")
- `user_metadata` (dict, **optional**): Custom user attributes (e.g., `{"role": "premium", "subscription": "gold"}`)
- `intent` (str, **optional**): Message intent classification (e.g., "question", "complaint", "request")
- `entities` (dict, **optional**): Extracted named entities (e.g., `{"person": "John", "location": "New York"}`)
- `annotations` (dict, **optional**): Additional message annotations (e.g., `{"priority": "high", "tags": ["urgent"]}`)
- `source_event` (dict, **optional**): Original event data from source system
- `agent_version` (str, **optional**): Agent version/model (e.g., "gpt-4", "claude-2") - **Required in database**
- `agent_metadata` (dict, **optional**): Agent configuration data (e.g., `{"temperature": 0.7, "max_tokens": 1000}`)
- `mode` (str, **optional**): Mode identifier for the message. Allowed values: `"SIMPLE"` or `"EXPAND"`

**Return Type:** `PlatformMessageSubmissionResponse`

#### `await messages.send_bot_message(...)`
Send a bot response to a human message.

**Parameters:**
- `username` (str, **required**): User identifier (must match the human message sender)
- `message` (str, **required**): Bot response content (e.g., "I can help you with that!")
- `agent_name` (str, **required**): Agent name (must match the human message agent)
- `agent_platform` (str, **required**): Agent platform (must match the human message platform)
- `reply_message_id` (UUID, **required**): ID of the human message being replied to
- `rag_context` (str, **required**): RAG context used for generating the response
- `user_email` (str, **required**): User's email address for identification
- `user_metadata` (dict, **optional**): User metadata
- `intent` (str, **optional**): Response intent
- `entities` (dict, **optional**): Extracted entities from response
- `annotations` (dict, **optional**): Response annotations
- `source_event` (dict, **optional**): Source event data
- `agent_version` (str, **optional**): Agent version/model - **Required in database**
- `agent_metadata` (dict, **optional**): Agent configuration
- `mode` (str, **optional**): Mode identifier for the message. Allowed values: `"SIMPLE"` or `"EXPAND"`

**Return Type:** `PlatformMessageSubmissionResponse`

#### `await messages.submit(request)`
Low-level message submission with full control.

**Parameters:**
- `request` (PlatformMessageSubmissionRequest, **required**): Complete message request object

**Return Type:** `PlatformMessageSubmissionResponse`

#### `await messages.get_all()`
Get all messages for the authenticated project.

**Return Type:** `List[PlatformMessage]`

#### `await messages.get_by_id(message_id)`
Get a specific message by ID.

**Parameters:**
- `message_id` (UUID, required): Message identifier

**Return Type:** `PlatformMessage`

#### `await messages.get_by_agent(agent_id)`
Get all messages sent by a specific agent.

**Parameters:**
- `agent_id` (UUID, required): Agent identifier

**Return Type:** `List[PlatformMessage]`

### Users API

#### `await users.create(username, email, metadata=None)`
Create a new user.

**Parameters:**
- `username` (str, **required**): Unique username (e.g., "john_doe", "user123")
- `email` (str, **required**): User's email address (e.g., "john@example.com")
- `metadata` (dict, **optional**): Custom user attributes (e.g., `{"role": "premium", "subscription": "gold", "preferences": {"theme": "dark"}}`)

**Return Type:** `User`

**Example:**
```python
user = await client.users.create_user(
    username="john_doe",
    email="john@example.com",
    metadata={"role": "premium"}
)
print(f"Created user: {user.username}")
```

### Agents API

#### `await agents.create(name, platform, version=None, metadata=None)`
Create a new AI agent.

**Parameters:**
- `name` (str, **required**): Display name for the agent (e.g., "CustomerSupportBot", "CodeAssistant")
- `platform` (str, **required**): Platform/provider (e.g., "OpenAI", "Azure", "Anthropic")
- `version` (str, **optional**): Model version (e.g., "gpt-4", "claude-2", "gpt-3.5-turbo")
- `metadata` (dict, **optional**): Agent configuration (e.g., `{"temperature": 0.7, "max_tokens": 2000, "system_prompt": "You are a helpful assistant"}`)

**Return Type:** `Agent`

**Example:**
```python
agent = await client.agents.create_agent(
    name="ChatGPT-4",
    platform="OpenAI",
    version="4.0",
    metadata={"model": "gpt-4", "temperature": 0.7}
)
print(f"Created agent: {agent.name}")
```

### Analytics API

#### `await analytics.submit_feedback(message_id, like=None, dislike=None, feedback=None, regeneration=None)`
Submit user feedback on a bot message.

**Parameters:**
- `message_id` (UUID, **required**): ID of the bot message receiving feedback
- `like` (bool, **optional**): User liked the response (true/false)
- `dislike` (bool, **optional**): User disliked the response (true/false)
- `feedback` (str, **optional**): Text feedback or comments (e.g., "Too verbose", "Perfect answer")
- `regeneration` (bool, **optional**): User requested regeneration (true/false)

**Return Type:** `FeedbackSubmissionResponse`

#### `await analytics.get_dashboard()`
Get project dashboard metrics.

**Return Type:** `DashboardMetricsDTO`

#### `await analytics.get_top_agents(limit=5)`
Get top-performing agents by usage.

**Parameters:**
- `limit` (int, **optional**): Maximum number of results (default: 5, max: 100)

**Return Type:** `List[TopAgentDTO]`

#### `await analytics.get_top_users(limit=5)`
Get most active users.

**Parameters:**
- `limit` (int, **optional**): Maximum number of results (default: 5, max: 100)

**Return Type:** `List[TopUserDTO]`

#### `await analytics.get_user_analytics()`
Get analytics for all users.

**Return Type:** `List[UserAnalyticsDTO]`

#### `await analytics.get_project_data(top_limit=10)`
Get project-level analytics data.

**Parameters:**
- `top_limit` (int, **optional**): Limit for top results (default: 10, max: 100)

**Return Type:** `ProjectAnalyticsResponseDTO`

#### `await analytics.get_all(top_limit=5)`
Get comprehensive analytics data.

**Parameters:**
- `top_limit` (int, **optional**): Limit for top results (default: 5, max: 100)

**Return Type:** `Dict[str, Any]`

#### `await analytics.initialize()`
Initialize analytics for the project.

**Return Type:** `Dict[str, Any]`

### Conversations API

#### `await conversations.get_messages_by_conversation_id(conversation_id)`
Get all messages in a conversation.

**Parameters:**
- `conversation_id` (UUID, required): Conversation identifier

**Return Type:** `List[ConversationMessageResponse]`

#### `await conversations.get_all_conversations()`
Get all conversations for the project.

**Return Type:** `List[ConversationSummaryResponse]`

#### `await conversations.get_user_conversations(username)`
Get all conversations for a specific user.

**Parameters:**
- `username` (str, required): Username

**Return Type:** `List[ConversationSummaryResponse]`

## Error Handling

The SDK surfaces HTTP errors as typed exceptions:

```python
from shiftai.http import (
    ApiException,
    UnauthorizedException,
    BadRequestException,
    NotFoundException,
    ServerException
)

try:
    response = await client.messages.send_human_message(
        username="user",
        message="Hello",
        agent_name="Bot",
        agent_platform="OpenAI"
    )
except BadRequestException as e:
    print(f"Invalid request: {e}")
except UnauthorizedException as e:
    print("Invalid API key")
except ApiException as e:
    print(f"API error {e.status_code}: {e}")
```




## Why This SDK Is Safe to Use

### No Hidden Dependencies
- **Explicit dependency list**: Only 1 external library needed
- **No transitive dependencies**: No "dependency hell"
- **Standard async library**: httpx is the de facto async HTTP library for Python

### Proven Portability
- **Minimal setup**: Just add httpx to requirements.txt
- **No configuration**: No complex setup or initialization

This SDK is built to enable developers to easily integrate and use the Shift AI Agentic Infra in their own applications



