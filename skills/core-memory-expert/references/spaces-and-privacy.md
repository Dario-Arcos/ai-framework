# Spaces & Privacy Model

Complete guide to Core's privacy architecture, data sharing capabilities, and organizational model using Spaces.

## Core Privacy Philosophy

**Default stance:** Private by default, explicit sharing via OAuth scopes and Space organization.

**Key principle:** User owns their memory graph. Data is isolated per user account unless explicitly shared through OAuth client applications.

---

## What Are Spaces?

**Definition:** Spaces are organizational containers for grouping related memory within a single user's knowledge graph.

**Think of Spaces like:**
- Folders in a file system
- Labels in Gmail
- Projects in task managers
- Workspaces in Slack

**Purpose:**
- Organize memory by context (Work, Personal, Projects)
- Filter searches to relevant subset
- Bulk manage related statements
- Enable focused retrieval

**NOT for:**
- Sharing between users (no multi-user spaces)
- Access control between team members
- Permissions hierarchy

---

## Privacy Model

### Data Ownership

**All data belongs to the authenticated user:**
- Knowledge graph is user-scoped
- No cross-user search
- No "public" or "shared" spaces natively

**Isolation:**
```
User A's memory  →  Completely separate  ←  User B's memory
```

Even if both use same Core instance, data never crosses user boundaries.

---

### What Is Private

**Always private (no sharing mechanism):**

| Data Type | Privacy Level | Accessible By |
|-----------|---------------|---------------|
| User profile (email, name) | 🔒 Private | User only |
| Integration credentials | 🔒 Private | User only |
| Ingestion logs | 🔒 Private | User only |
| Webhook secrets | 🔒 Private | User only |
| API keys | 🔒 Private | User only |

**Cannot be shared:** These data types have no sharing endpoints or mechanisms.

---

### What Can Be Shared

**Conditionally shareable via OAuth:**

| Data Type | Privacy Level | Sharing Mechanism |
|-----------|---------------|-------------------|
| Space data (facts/statements) | 🟡 Conditional | OAuth client with scopes |
| Search results | 🟡 Conditional | OAuth client with `read` scope |
| Memory additions | 🟡 Conditional | OAuth client with `write` scope |

**How sharing works:**
1. User authorizes OAuth application
2. Application receives scoped access token
3. Application can read/write user's memory within granted scopes
4. User can revoke access anytime

**Example:**
```
User authorizes "Task Manager App"
  → Grants: read + write scopes
  → App can:
      ✅ Search user's memory
      ✅ Add tasks to user's memory
      ❌ Access other users' data
      ❌ Modify user profile
```

---

## OAuth Scopes (Permission Model)

Core uses OAuth2 scopes as permission system.

### Available Scopes

**`read`** - Read access to user data
- Search memory (`POST /api/v1/search`)
- List spaces (`GET /api/v1/spaces`)
- View logs (`GET /api/v1/logs`)
- Get facts (`GET /api/v1/episodes/{id}/facts`)

**`write`** - Write access to user data
- Ingest data (`POST /api/v1/add`)
- Create spaces (`POST /api/v1/spaces`)
- Update spaces (`PUT /api/v1/spaces/{id}`)
- Delete data (`DELETE /api/v1/logs/{id}`)

**`mcp`** - Model Context Protocol access
- Use MCP tools (memory_search, memory_ingest)
- Required for Claude Code, Cursor integration

**`integration`** - Access to integrations
- Connect external services (`POST /api/v1/integration_account`)
- List integrations (`GET /api/v1/integrations`)
- Disconnect services

**`oauth`** - OAuth client management
- Create OAuth clients (`POST /api/oauth/clients`)
- Manage client credentials
- Advanced: for platform builders

---

### Scope Combinations

**Read-only app:**
```
Scopes: read
Can: Search memory, view spaces
Cannot: Add data, modify spaces
```

**Full access app:**
```
Scopes: read, write, mcp
Can: Everything except integration/oauth management
```

**Platform integration:**
```
Scopes: read, write, integration
Can: Sync data with external services (GitHub, Linear)
```

---

## Spaces Management

### Creating Spaces

**When to create:**
- New project starts
- Different client/context
- Separating work/personal
- Organizing by topic

**Best practices:**
```
✅ Clear naming: "Project Alpha - Client Work"
✅ Descriptive: "Personal learning and preferences"
✅ Focused: One context per space
❌ Generic: "Stuff", "Misc", "Other"
❌ Overlapping: "Work" + "Office" (redundant)
```

**Example structure:**
```
Personal
  ↳ Coding preferences
  ↳ Learning notes

Work
  ↳ Current sprint context
  ↳ Team decisions

Client: Acme Corp
  ↳ Project requirements
  ↳ Technical decisions
```

---

### Assigning Statements to Spaces

**Automatic assignment:**
When ingesting data via `POST /api/v1/add`, include space metadata:

```json
{
  "data": "Acme Corp prefers React over Vue",
  "metadata": {
    "spaceId": "space-acme"
  }
}
```

**Bulk reassignment:**
Move existing statements between spaces:

```json
PUT /api/v1/spaces
{
  "intent": "assign_statements",
  "spaceId": "space-work",
  "statementIds": ["stmt_1", "stmt_2", "stmt_3"]
}
```

**Use case:** You ingested data without space, now want to organize.

---

### Filtering Searches by Space

**Search specific spaces:**
```json
POST /api/v1/search
{
  "query": "database schema",
  "spaceIds": ["space-work", "space-acme"]
}
```

**Benefits:**
- Faster searches (smaller dataset)
- More relevant results (contextual)
- Avoid noise from unrelated contexts

**Example:**
```
Query: "authentication approach"

Without spaceIds:
  → Returns: personal learning + work project + client project (mixed)

With spaceIds: ["space-work"]:
  → Returns: only work-related auth decisions (focused)
```

---

## Sharing Scenarios

### Scenario 1: Solo Developer

**Setup:**
- Single user account
- Multiple spaces (Personal, Project A, Project B)
- No sharing needed

**Privacy:**
- All data private to user
- No OAuth clients needed
- Direct API access via personal API key

---

### Scenario 2: Team Collaboration (Indirect)

**Problem:** Core doesn't support native team sharing.

**Workaround:**
1. Create shared OAuth application
2. Team members individually authorize app
3. App aggregates data from multiple users

**Example:**
```
Team Dashboard App
  ↳ User A authorizes (grants read scope)
  ↳ User B authorizes (grants read scope)
  ↳ App queries both users' memories
  ↳ Displays aggregated insights
```

**Limitations:**
- Each user sees only their data in Core
- Aggregation happens in external app
- No "shared space" natively

---

### Scenario 3: Service Integration

**Use case:** Sync Core with external service (Notion, project manager)

**Setup:**
1. Create OAuth client for integration
2. Request `read` + `write` + `integration` scopes
3. Sync bidirectionally

**Privacy:**
- User controls which integrations connect
- User can disconnect anytime
- Integration accesses only user's data

---

## Data Lifecycle & Privacy

### Ingestion

**What gets stored:**
- Normalized text
- Extracted entities and relationships
- Temporal metadata (when, who)
- Provenance (source, conversation ID)

**What doesn't get stored:**
- Raw credentials or secrets (filtered)
- Full code blocks (summary only)
- Temporary data (expired automatically)

**Privacy during ingestion:**
- Data processed server-side
- Encrypted in transit (TLS 1.3)
- Encrypted at rest (AES-256)

---

### Search

**Query privacy:**
- Search queries not logged publicly
- Results filtered by user authentication
- No cross-user leakage

**Search scope:**
```
User's query → Core checks auth → Filters to user's graph → Returns results
```

**Cannot search:**
- Other users' data
- Public knowledge base (Core is personal, not Wikipedia)

---

### Deletion

**What happens when you delete:**

**Delete log (`DELETE /api/v1/logs/{id}`):**
- Removes ingestion log
- Cascades to episode
- Cascades to extracted facts
- Cascades to entities (if orphaned)

**Delete space (`DELETE /api/v1/spaces/{id}`):**
- Removes space metadata
- Statements become orphaned (unless reassigned first)
- **Best practice:** Reassign statements before deleting

**Account deletion:**
- Contact support (manik@poozle.dev)
- All data permanently deleted
- OAuth clients revoked
- Integrations disconnected

---

## Security Best Practices

### API Key Management

**Do:**
- ✅ Store in environment variables
- ✅ Rotate every 90 days
- ✅ Use separate keys for dev/staging/prod
- ✅ Revoke immediately if compromised

**Don't:**
- ❌ Commit to git
- ❌ Share in Slack/email
- ❌ Hardcode in scripts
- ❌ Use same key across projects

---

### OAuth Application Security

**When building OAuth apps:**
- ✅ Request minimum necessary scopes
- ✅ Implement PKCE for public clients
- ✅ Store refresh tokens securely
- ✅ Handle token expiration gracefully
- ✅ Provide clear privacy policy

**When authorizing apps:**
- ✅ Review requested scopes
- ✅ Verify app legitimacy
- ✅ Revoke unused apps quarterly
- ✅ Monitor app activity

---

### Space Organization for Privacy

**Sensitive data separation:**
```
Space: Work (client data)
  ↳ Restricted: never share with personal apps

Space: Personal
  ↳ Safe: can share with productivity apps
```

**Strategy:**
1. Create separate spaces for different sensitivity levels
2. Filter searches to appropriate spaces
3. Configure OAuth apps with space-specific access (if app supports)

---

## Privacy Comparison

### Core vs Traditional Cloud Services

| Feature | Core | Dropbox | Google Drive |
|---------|------|---------|--------------|
| Default privacy | Private | Private | Private |
| Sharing mechanism | OAuth apps | Links + invites | Links + invites |
| Multi-user spaces | ❌ No | ✅ Yes | ✅ Yes |
| Public sharing | ❌ No | ✅ Yes | ✅ Yes |
| Data encryption | ✅ AES-256 | ✅ AES-256 | ✅ AES-256 |
| User owns data | ✅ Yes | ⚠️ Limited | ⚠️ Limited |

**Key difference:** Core is designed for AI memory, not file sharing. Privacy model reflects this.

---

## Compliance & Data Sovereignty

**Data location:**
- Core Cloud: Hosted in Germany (EU)
- Self-hosted: Your infrastructure (full control)

**GDPR compliance:**
- ✅ Right to access (API endpoints)
- ✅ Right to deletion (account deletion)
- ✅ Right to portability (export via API)
- ✅ Data minimization (only essential stored)

**Self-hosting benefits:**
- Full data sovereignty
- Custom compliance requirements
- Air-gapped deployments
- Complete audit trail

---

## Troubleshooting Privacy Issues

### "Data appearing in wrong context"

**Cause:** Statements not assigned to correct space

**Solution:**
```bash
# Reassign to correct space
PUT /api/v1/spaces
{
  "intent": "assign_statements",
  "spaceId": "space-correct",
  "statementIds": ["stmt_xyz"]
}
```

---

### "Sensitive data in memory"

**Cause:** Accidentally ingested credentials/PII

**Solution:**
```bash
# Find log ID
GET /api/v1/logs?limit=50

# Delete log (cascades to facts)
DELETE /api/v1/logs/{logId}
```

---

### "OAuth app has too much access"

**Cause:** Granted excessive scopes

**Solution:**
1. Visit core.heysol.ai → Settings → Connected Apps
2. Revoke app authorization
3. Re-authorize with minimal scopes

---

### "Want to share memory with team"

**Core limitation:** No native team sharing

**Workarounds:**
1. **Shared OAuth app:** Build app that aggregates multiple users
2. **Export/import:** Export via API, share export file
3. **Screen sharing:** Collaborative viewing (not editing)
4. **Self-hosted:** Custom implementation for team features

---

## Future Privacy Features

**Planned (check roadmap):**
- Shared spaces (multi-user collaboration)
- Granular permissions (read-only, comment, edit)
- Time-limited sharing
- Anonymous sharing (no user association)

**Not planned:**
- Public memory graphs
- Anonymous accounts
- Cross-instance federation

---

## FAQ

**Q: Can others see my memory?**
A: No. All data is private to your account unless you authorize an OAuth application.

**Q: What happens if I authorize a malicious app?**
A: App can access data within granted scopes. Revoke immediately and rotate API keys.

**Q: Can I share specific facts with collaborators?**
A: Not natively. Export via API and share manually, or build custom OAuth app.

**Q: Are my searches private?**
A: Yes. Queries are not logged publicly and only search your data.

**Q: Can Core admins see my data?**
A: Self-hosted: No (you control infrastructure). Cloud: Only for support/debugging with explicit consent.

**Q: How do I completely delete my account?**
A: Contact manik@poozle.dev. All data permanently deleted within 30 days.

**Q: Can I migrate data between accounts?**
A: Export via API from old account, import to new account via `POST /api/v1/add`.

---

## Best Practices Summary

**Organization:**
- Create spaces per context
- Assign statements immediately
- Review and prune quarterly

**Privacy:**
- Use OAuth, not API keys for apps
- Grant minimum necessary scopes
- Revoke unused authorizations
- Separate sensitive data into dedicated spaces

**Security:**
- Rotate API keys every 90 days
- Monitor integration usage
- Review logs monthly
- Enable 2FA on Core account

**Compliance:**
- Document data retention policies
- Implement deletion workflows
- Audit access logs
- Self-host if sovereignty required

---

## Further Reading

- REST API Reference: rest-api-reference.md
- Core Concepts: core-concepts.md
- MCP Configuration: mcp-configuration.md
- Official privacy policy: https://heysol.ai/privacy
