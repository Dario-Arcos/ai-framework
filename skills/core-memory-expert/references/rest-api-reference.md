# Core REST API Reference

Complete reference for RedPlanet Core REST API endpoints, authentication, and programmatic access patterns.

## Base URL

```
https://core.heysol.ai
```

Self-hosted instances use custom domain or `http://localhost:3000`.

## Authentication

### Bearer Token (Recommended for API)

**Obtain API Key:**
1. Visit https://core.heysol.ai → Settings → API Keys
2. Generate new API key
3. Store securely in environment variable

**Usage:**
```bash
curl -X POST https://core.heysol.ai/api/v1/search \
  -H "Authorization: Bearer $CORE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "preferences"}'
```

### OAuth2 Scopes

**Available scopes:**
- `read` - Read access to user data
- `write` - Write access to user data
- `mcp` - Model Context Protocol access
- `integration` - Access to integrations
- `oauth` - OAuth client management

**OAuth Flow:**
```
1. GET /oauth/authorize?client_id=X&scope=read+write
2. User grants permissions
3. POST /oauth/token with authorization code
4. Receive access token
```

### Session Cookies

Web interface uses session-based authentication automatically.

---

## Memory Operations

### Add Data (Ingest)

**Endpoint:** `POST /api/v1/add`

**Purpose:** Queue data for ingestion and fact extraction into knowledge graph.

**Authentication:** Bearer token with `write` scope

**Request:**
```json
{
  "data": "Project uses TypeScript with strict mode. Rationale: better type safety.",
  "source": "conversation",
  "metadata": {
    "project": "TaskMaster",
    "topic": "coding-standards"
  }
}
```

**Response (202 Accepted):**
```json
{
  "episodeId": "ep_abc123",
  "status": "queued",
  "message": "Data queued for processing"
}
```

**Process:**
1. Data queued in ingestion pipeline
2. Normalization → Extraction → Resolution → Graph Integration
3. Check status: `GET /api/v1/logs` or `GET /api/v1/episodes/{episodeId}/facts`

---

### Search Knowledge Graph

**Endpoint:** `POST /api/v1/search`

**Purpose:** Semantic search with graph traversal, temporal filtering, and entity type filtering.

**Authentication:** Bearer token with `read` scope

**Request:**
```json
{
  "query": "TypeScript coding standards",
  "spaceIds": ["space-work"],
  "limit": 10,
  "filters": {
    "temporal": "last_month",
    "entityTypes": ["Technology", "Practice"],
    "minRelevance": 0.7
  }
}
```

**Parameters:**
- `query` (required): Search query string
- `spaceIds` (optional): Filter to specific spaces **⚠️ NOT WORKING (verified 2025-11-03)**
- `limit` (optional): Max results (default: 10)
- `filters` (optional): Temporal, entity type, relevance filters

**⚠️ KNOWN ISSUE:** `spaceIds` parameter is documented but currently ignored by API. See `spaces-and-privacy.md` for details and workarounds.

**Response (200 OK):**
```json
{
  "results": [
    {
      "id": "fact_xyz789",
      "content": "Project uses TypeScript with strict mode enabled",
      "relevance": 0.95,
      "timestamp": "2025-10-31T12:00:00Z",
      "entities": ["TypeScript", "strict-mode"],
      "spaceId": "space-work"
    }
  ],
  "total": 1,
  "query": "TypeScript coding standards"
}
```

**Search Methods:**
- **Keyword**: Exact string matching
- **Semantic**: Conceptual similarity via embeddings
- **Graph traversal**: Following entity relationships

---

### Retrieve Extracted Facts

**Endpoint:** `GET /api/v1/episodes/{episodeId}/facts`

**Purpose:** Get facts extracted from specific ingestion episode.

**Authentication:** Bearer token with `read` scope

**Request:**
```bash
curl https://core.heysol.ai/api/v1/episodes/ep_abc123/facts \
  -H "Authorization: Bearer $CORE_API_KEY"
```

**Response (200 OK):**
```json
{
  "episodeId": "ep_abc123",
  "facts": [
    {
      "id": "fact_1",
      "subject": "TaskMaster",
      "predicate": "uses",
      "object": "TypeScript",
      "timestamp": "2025-10-31T12:00:00Z",
      "confidence": 0.98
    }
  ],
  "total": 1
}
```

---

## Spaces Management

### List Spaces

**Endpoint:** `GET /api/v1/spaces`

**Purpose:** List all spaces (organizational containers for memory).

**Authentication:** Bearer token with `read` scope

**Request:**
```bash
curl https://core.heysol.ai/api/v1/spaces \
  -H "Authorization: Bearer $CORE_API_KEY"
```

**Response (200 OK):**
```json
{
  "spaces": [
    {
      "id": "space-personal",
      "name": "Personal",
      "description": "Personal projects and preferences",
      "createdAt": "2025-10-01T00:00:00Z",
      "statementCount": 247
    },
    {
      "id": "space-work",
      "name": "Work",
      "description": "Work-related context",
      "createdAt": "2025-10-15T00:00:00Z",
      "statementCount": 1523
    }
  ],
  "total": 2
}
```

---

### Create Space

**Endpoint:** `POST /api/v1/spaces`

**Purpose:** Create new organizational space.

**Authentication:** Bearer token with `write` scope

**Request:**
```json
{
  "name": "Client Project Alpha",
  "description": "Memory for Alpha project work",
  "metadata": {
    "client": "Acme Corp",
    "project_code": "ALPHA-2025"
  }
}
```

**Response (201 Created):**
```json
{
  "id": "space-alpha",
  "name": "Client Project Alpha",
  "description": "Memory for Alpha project work",
  "createdAt": "2025-10-31T15:00:00Z",
  "statementCount": 0
}
```

---

### Get Space Details

**Endpoint:** `GET /api/v1/spaces/{spaceId}`

**Purpose:** Retrieve specific space details.

**Authentication:** Bearer token with `read` scope

**Request:**
```bash
curl https://core.heysol.ai/api/v1/spaces/space-work \
  -H "Authorization: Bearer $CORE_API_KEY"
```

**Response (200 OK):**
```json
{
  "id": "space-work",
  "name": "Work",
  "description": "Work-related context",
  "createdAt": "2025-10-15T00:00:00Z",
  "updatedAt": "2025-10-31T14:00:00Z",
  "statementCount": 1523,
  "metadata": {}
}
```

---

### Update Space

**Endpoint:** `PUT /api/v1/spaces/{spaceId}`

**Purpose:** Update space metadata.

**Authentication:** Bearer token with `write` scope

**Request:**
```json
{
  "name": "Work - Updated",
  "description": "Professional work context",
  "metadata": {
    "team": "Engineering",
    "department": "Product"
  }
}
```

**Response (200 OK):**
```json
{
  "id": "space-work",
  "name": "Work - Updated",
  "description": "Professional work context",
  "updatedAt": "2025-10-31T15:30:00Z"
}
```

---

### Delete Space

**Endpoint:** `DELETE /api/v1/spaces/{spaceId}`

**Purpose:** Delete space and optionally reassign or delete statements.

**Authentication:** Bearer token with `write` scope

**Request:**
```bash
curl -X DELETE https://core.heysol.ai/api/v1/spaces/space-old \
  -H "Authorization: Bearer $CORE_API_KEY"
```

**Response (204 No Content)**

**Warning:** Deleting a space may orphan or delete statements. Reassign important data first.

---

### Bulk Space Operations

**Endpoint:** `PUT /api/v1/spaces`

**Purpose:** Perform bulk operations on spaces and statements.

**Authentication:** Bearer token with `write` scope

**Assign Statements to Space:**
```json
{
  "intent": "assign_statements",
  "spaceId": "space-work",
  "statementIds": ["stmt_1", "stmt_2", "stmt_3"]
}
```

**Remove Statements from Space:**
```json
{
  "intent": "remove_statements",
  "spaceId": "space-work",
  "statementIds": ["stmt_4", "stmt_5"]
}
```

**Initialize Space IDs (Migration):**
```json
{
  "intent": "initialize_space_ids",
  "defaultSpaceId": "space-default"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "modified": 3,
  "message": "Statements assigned to space-work"
}
```

---

## Monitoring & Logs

### Ingestion Queue Status

**Endpoint:** `GET /api/v1/ingestion-queue/status`

**Purpose:** Check processing queue status.

**Authentication:** Bearer token with `read` scope

**Request:**
```bash
curl https://core.heysol.ai/api/v1/ingestion-queue/status \
  -H "Authorization: Bearer $CORE_API_KEY"
```

**Response (200 OK):**
```json
{
  "queued": 5,
  "processing": 2,
  "completed": 1247,
  "failed": 3
}
```

---

### List Ingestion Logs

**Endpoint:** `GET /api/v1/logs`

**Purpose:** View ingestion processing history.

**Authentication:** Bearer token with `read` scope

**Request:**
```bash
curl "https://core.heysol.ai/api/v1/logs?limit=20&status=completed" \
  -H "Authorization: Bearer $CORE_API_KEY"
```

**Query Parameters:**
- `limit` (optional): Max results (default: 50)
- `status` (optional): Filter by status (queued, processing, completed, failed)
- `offset` (optional): Pagination offset

**Response (200 OK):**
```json
{
  "logs": [
    {
      "id": "log_abc",
      "episodeId": "ep_xyz",
      "status": "completed",
      "createdAt": "2025-10-31T12:00:00Z",
      "completedAt": "2025-10-31T12:00:15Z",
      "factsExtracted": 5
    }
  ],
  "total": 1247,
  "limit": 20,
  "offset": 0
}
```

---

### Get Specific Log

**Endpoint:** `GET /api/v1/logs/{logId}`

**Purpose:** Retrieve detailed log information.

**Authentication:** Bearer token with `read` scope

**Response (200 OK):**
```json
{
  "id": "log_abc",
  "episodeId": "ep_xyz",
  "status": "completed",
  "input": "Original data that was ingested...",
  "factsExtracted": 5,
  "errors": [],
  "createdAt": "2025-10-31T12:00:00Z",
  "completedAt": "2025-10-31T12:00:15Z"
}
```

---

### Delete Log

**Endpoint:** `DELETE /api/v1/logs/{logId}`

**Purpose:** Delete log and associated episode, statements, and entities.

**Authentication:** Bearer token with `write` scope

**Request:**
```bash
curl -X DELETE https://core.heysol.ai/api/v1/logs/log_abc \
  -H "Authorization: Bearer $CORE_API_KEY"
```

**Response (204 No Content)**

**Warning:** This cascades deletion to associated facts and entities.

---

## Webhooks

### Create Webhook

**Endpoint:** `POST /api/v1/webhooks`

**Purpose:** Register webhook for real-time notifications.

**Authentication:** Bearer token with `write` scope

**Request:**
```json
{
  "url": "https://your-app.com/webhook",
  "events": ["fact.created", "ingestion.completed"],
  "secret": "webhook_secret_for_verification"
}
```

**Events:**
- `fact.created` - New fact extracted
- `fact.updated` - Fact modified
- `ingestion.completed` - Ingestion finished
- `ingestion.failed` - Ingestion error

**Response (201 Created):**
```json
{
  "id": "webhook_123",
  "url": "https://your-app.com/webhook",
  "events": ["fact.created", "ingestion.completed"],
  "createdAt": "2025-10-31T15:00:00Z",
  "active": true
}
```

---

### List Webhooks

**Endpoint:** `GET /api/v1/webhooks`

**Authentication:** Bearer token with `read` scope

**Response (200 OK):**
```json
{
  "webhooks": [
    {
      "id": "webhook_123",
      "url": "https://your-app.com/webhook",
      "events": ["fact.created"],
      "active": true
    }
  ],
  "total": 1
}
```

---

### Update Webhook

**Endpoint:** `PUT /api/v1/webhooks/{webhookId}`

**Authentication:** Bearer token with `write` scope

**Request:**
```json
{
  "active": false,
  "events": ["ingestion.completed"]
}
```

---

### Delete Webhook

**Endpoint:** `DELETE /api/v1/webhooks/{webhookId}`

**Authentication:** Bearer token with `write` scope

**Response (204 No Content)**

---

## Integration Accounts

### List Integrations

**Endpoint:** `GET /api/v1/integrations`

**Purpose:** List connected external services.

**Authentication:** Bearer token with `read` scope

**Response (200 OK):**
```json
{
  "integrations": [
    {
      "name": "github",
      "connected": true,
      "lastSync": "2025-10-31T10:00:00Z",
      "activityCount": 523
    },
    {
      "name": "linear",
      "connected": true,
      "lastSync": "2025-10-31T11:00:00Z",
      "activityCount": 147
    }
  ]
}
```

---

### Connect Integration Account

**Endpoint:** `POST /api/v1/integration_account`

**Purpose:** Link external service account.

**Authentication:** Bearer token with `integration` scope

**Request:**
```json
{
  "provider": "github",
  "credentials": {
    "access_token": "ghp_..."
  }
}
```

**Response (201 Created):**
```json
{
  "id": "account_123",
  "provider": "github",
  "status": "connected",
  "connectedAt": "2025-10-31T15:00:00Z"
}
```

---

### Disconnect Integration

**Endpoint:** `POST /api/v1/integration_account/disconnect`

**Purpose:** Remove external service connection.

**Authentication:** Bearer token with `integration` scope

**Request:**
```json
{
  "provider": "github"
}
```

**Response (200 OK):**
```json
{
  "provider": "github",
  "status": "disconnected"
}
```

---

## User Profile

### Get Profile

**Endpoint:** `GET /api/profile`

**Purpose:** Retrieve authenticated user profile.

**Authentication:** OAuth2 token

**Response (200 OK):**
```json
{
  "user": {
    "id": "user_abc",
    "email": "user@example.com",
    "name": "John Doe",
    "picture": "https://..."
  },
  "client": {
    "clientId": "client_xyz",
    "name": "Claude Code"
  },
  "scopes": ["read", "write", "mcp"]
}
```

---

## Activity Tracking

### Create Activity

**Endpoint:** `POST /api/v1/activity`

**Purpose:** Record activity with optional webhook notifications.

**Authentication:** Bearer token with `write` scope

**Request:**
```json
{
  "type": "code_commit",
  "description": "Committed feature X to repository",
  "metadata": {
    "repo": "my-project",
    "branch": "feature-x",
    "commit": "abc123"
  },
  "notify": true
}
```

**Response (201 Created):**
```json
{
  "id": "activity_456",
  "type": "code_commit",
  "createdAt": "2025-10-31T15:30:00Z",
  "webhooksSent": 2
}
```

---

## Error Responses

### Common Error Codes

**401 Unauthorized:**
```json
{
  "error": "unauthorized",
  "message": "Invalid or missing Bearer token"
}
```

**403 Forbidden:**
```json
{
  "error": "forbidden",
  "message": "Insufficient scope: requires 'write'"
}
```

**404 Not Found:**
```json
{
  "error": "not_found",
  "message": "Space 'space-xyz' not found"
}
```

**422 Validation Error:**
```json
{
  "error": "validation_error",
  "message": "Invalid request format",
  "details": {
    "field": "query",
    "error": "required"
  }
}
```

**500 Internal Server Error:**
```json
{
  "error": "internal_error",
  "message": "Processing failed, try again"
}
```

---

## Rate Limiting

**Limits:**
- Free tier: 100 requests/hour
- Pro tier: 1000 requests/hour
- Max tier: 10000 requests/hour

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1699012345
```

**429 Too Many Requests:**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Retry after 3600 seconds",
  "retryAfter": 3600
}
```

---

## Best Practices

**Authentication:**
- Use API keys for server-to-server
- Use OAuth2 for user-facing applications
- Store tokens in environment variables
- Rotate API keys quarterly

**Search Optimization:**
- Use `spaceIds` to filter searches
- Set appropriate `limit` to avoid large responses
- Use temporal filters for recent data
- Cache search results when possible

**Spaces Strategy:**
- Create spaces per project/client
- Use descriptive names
- Assign statements immediately on ingestion
- Review and prune obsolete spaces monthly

**Error Handling:**
- Implement exponential backoff for retries
- Log error details for debugging
- Handle rate limits gracefully
- Validate requests before sending

**Performance:**
- Batch operations when possible
- Use webhooks instead of polling
- Monitor ingestion queue status
- Set up alerts for failed ingestions

---

## Python Example

```python
import os
import requests

BASE_URL = "https://core.heysol.ai"
API_KEY = os.getenv("CORE_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def search_memory(query, space_ids=None):
    """Search Core memory"""
    payload = {"query": query}
    if space_ids:
        payload["spaceIds"] = space_ids

    response = requests.post(
        f"{BASE_URL}/api/v1/search",
        headers=HEADERS,
        json=payload
    )
    response.raise_for_status()
    return response.json()

def create_space(name, description=""):
    """Create new space"""
    payload = {
        "name": name,
        "description": description
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/spaces",
        headers=HEADERS,
        json=payload
    )
    response.raise_for_status()
    return response.json()

# Usage
results = search_memory("TypeScript preferences", space_ids=["space-work"])
new_space = create_space("Project Alpha", "Client project memory")
```

---

## Further Reading

- Spaces & Privacy Model: spaces-and-privacy.md
- Core Concepts: core-concepts.md
- MCP Configuration: mcp-configuration.md
- Troubleshooting: troubleshooting.md
