# Table of Contents

- MCP server
- MCP server
- AI Agents
- Triage Intelligence

---

# MCP server

Source: https://linear.app/docs/mcp

---

# MCP server

![Abstract image of a drive with Linear's logo and the words "Remote MCP server"](https://webassets.linear.app/images/ornj730p/production/54373418b3cb31208f112cd8137d7dd825d1b7c0-3600x1800.png?w=1440&q=95&auto=format&dpr=2)

The Model Context Protocol (MCP) server provides a standardized interface that allows any compatible AI model or agent to access your Linear data in a simple and secure way.

Connect to our MCP server natively in Claude, Cursor, and other clients or use the   mcp-remote module for backwards compatibility with clients that do not support remote MCP.

Linear's MCP server follows the authenticated remote MCP spec, so the server is centrally hosted and managed. The Linear MCP server has tools available for finding, creating, and updating objects in Linear like issues, projects, and comments — with more functionality on the way, and feedback on its functionality is welcomed.

## Setup Instructions⁠

### General⁠

Our MCP server supports both Server-Sent Events (SSE) and Streamable HTTP transports. Both transports use OAuth 2.1 with dynamic client registration for authentication at the following addresses:

- HTTP: https://mcp.linear.app/mcp
- SSE: https://mcp.linear.app/sse

We recommend using the streamable HTTP endpoint where supported for increased reliability. For instructions for specific clients, read on…

### Claude⁠

Team, Enterprise (Claude.ai)

- Navigate to Settings in the sidebar on web or desktop
- Scroll to Integrations at the bottom and click Add more
- In the prompt enter:Integration name: LinearIntegration URL: https://mcp.linear.app/mcp
- Make sure to enable the tools in any new chats

Free, Pro (Claude desktop)

- Open the file ~/Library/Application Support/Claude/claude_desktop_config.json
- Add the following and restart the Claude desktop app:

```
{
  "mcpServers": {
    "linear": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.linear.app/mcp"]
    }
  }
}
```

Claude Code

```
claude mcp add --transport http linear-server https://mcp.linear.app/mcp
```

Then run /mcp once you've opened a Claude Code session to go through the authentication flow.

### Codex⁠

The setup steps for the MCP server are the same regardless of whether you use the IDE Extension or the CLI since the configuration is shared.

Configuration via CLI:

Run the following command in Terminal:

```
codex mcp add linear --url https://mcp.linear.app/mcp
```

This will automatically prompt you to log in with your Linear account and connect it to your Codex.

Note: If this is the first time you are using an MCP in Codex you will need to enable the rmcp feature for this to work. Add the following into your ~/.codex/config.toml:

```
[features]
experimental_use_rmcp_client = true
```

Configuration through environment variables:

- Open the ~/.codex/config.toml file in your preferred editor
- Add the following:

```
[features]
experimental_use_rmcp_client = true
 
[mcp_servers.linear]
url = "https://mcp.linear.app/mcp"
```

Run codex mcp login linear to move through the authentication flow.

### Cursor⁠

To add the MCP to Cursor, you can install by clicking here, or searching for Linear from Cursor's MCP tools page.

![C](https://webassets.linear.app/images/ornj730p/production/7ff4a8f3f3f95e1a25a241c49f5d46c66e17b80a-760x343.png?w=1440&q=95&auto=format&dpr=2)

### Visual Studio Code⁠

```
{
  "mcpServers": {
    "linear": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.linear.app/mcp"]
    }
  }
}
```

- CTRL/CMD  P and search for MCP: Add Server.
- Select Command (stdio)
- Enter the following configuration, and hit enter.

npx mcp-remote https://mcp.linear.app/mcp

- Enter the name Linear and hit enter.
- Activate the server using MCP: List Servers and selecting Linear, and selecting Start Server.

### v0 by Vercel⁠

To add the MCP to v0, you can install from the connections page.

### Windsurf⁠

- CTRL/CMD  , to open Windsurf settings.
- Under Scroll to Cascade -> MCP servers
- Select Add Server -> Add custom server
- Add the following:

```
{
  "mcpServers": {
    "linear": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.linear.app/mcp"]
    }
  }
}
```

### Zed⁠

- CMD  , to open Zed settings.
- Add the following:

```
{
  "context_servers": {
    "linear": {
      "source": "custom",
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.linear.app/mcp"],
      "env": {}
    }
  }
}
```

### Others⁠

Hundreds of other tools now support MCP servers, you can configure them to use Linear's MCP server with the following settings:

- Command: npx
- Arguments: -y mcp-remote https://mcp.linear.app/mcp
- Environment: None



## FAQ⁠

[](https://linear.app/docs/mcp#collapsible-8953739bc544)Enter the following in the Terminal to clear saved auth info: rm -rf ~/.mcp-auth then try again to connect.Additionally you may need to update to a newer version of node if required.

[](https://linear.app/docs/mcp#collapsible-9290c8c40a39)Try instead to connect using: {"mcpServers": {"linear": {"command": "wsl","args": ["npx","-y","mcp-remote","https://mcp.linear.app/sse","--transport sse-only"]}}}

[](https://linear.app/docs/mcp#collapsible-5e63b34a22cc)Yes, at the https://mcp.linear.app/mcp endpoint

[](https://linear.app/docs/mcp#collapsible-28a2f832a8df)The MCP server now supports passing OAuth token and API keys directly in the Authorization: Bearer <yourtoken> header instead of using the interactive authentication flow.

You can use this to interact with the MCP server as an app user, provide read-only access through a restricted API key, or integrate with an existing Linear OAuth application without an extra authentication hop.



[PreviousAI Agents](https://linear.app/docs/agents-in-linear)[NextTriage Intelligence](https://linear.app/docs/triage-intelligence)# AI Agents

Source: https://linear.app/docs/agents-in-linear

---

# AI Agents

Build and deploy AI agents that work alongside your team

![list of agents in assignee menu, Charlie and ChatPRD are visible](https://webassets.linear.app/images/ornj730p/production/68c955d01e0e45b23747e8cd7362b018b06a6655-2880x1768.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Agents, also known as "app users", behave similar to other users in a workspace. They can be @-mentioned, delegated issues through assignment, create and reply to comments, collaborate on projects and documents, etc. App users are installed and managed by workspace admins.

Agents are not traditional assignees. Assigning an issue to an agent triggers delegation—the agent acts on the issue, but the human teammate remains responsible for its completion.

## Adding Agents⁠

Workspace admins can install agents by following the setup instructions provided by the agent developer. Find available agents in the Integrations Directory.

During installation, you’ll be prompted to choose which teams the agent has access to.

[](https://linear.app/docs/agents-in-linear#collapsible-c52dc8cc0210)![Installing the codegen agent into Linear permissions modal](https://webassets.linear.app/images/ornj730p/production/9a11b2deb2fd1f6b5649f00ebaa928124f061099-1292x1019.png?w=1440&q=95&auto=format&dpr=2)



Once installed, any user with access to the selected teams can interact with the agent.

Agents can be uninstalled or managed by admins from Settings > Applications or suspended from Settings > Administration > Members.

## Using Agents in Linear⁠

Agents are designed to work seamlessly alongside human teammates:

- Delegate issues to them by assigning the issue to the agent. This triggers the agent to take action based on its programmed behavior.The human assignee remains responsible for the issue, even after delegation to an agent.
- @mention them in comments or descriptions to trigger their functions.

If you're not sure how to interact or what they're able to help with, you can try @mentioning the agent to ask for help.

## Guiding Agents⁠

Agent guidance lets you provide instructions that agents will automatically receive when they work on issues in your workspace.

![Screenshot of the Additional guidance panel showing repository instructions for agents](https://webassets.linear.app/images/ornj730p/production/d9cb1836286c78822dddee0e6e9ec3c67a1c10a9-1570x788.png?w=1440&q=95&auto=format&dpr=2)

Agent guidance provides instructions that help agents work within your team’s conventions. Guidance can specify which repository to use for certain code changes, how to reference issues in commits or pull requests, and what review process to follow, so agents align with your existing workflows.

Note: All guidance is passed to the agent, but how it is interpreted or applied depends on the specific agent integration. If an agent doesn’t appear to follow the guidance, please share feedback with the team responsible for that agent directly.

Workspace guidance applies across the entire organization, while team-specific guidance can be used to include additional instructions unique to that team. When both exist, team guidance takes priority.

Guidance is authored in a markdown editor with full history, so instructions can be formatted clearly and reviewed or updated over time.

To edit your workspace-level agent guidance, navigate to Settings > Agents > Additional guidance. For team-level guidance, navigate into your parent or sub-team's settings > Agents > Additional guidance. Both workspace and team level guidance may not exist in all agent contexts.

## Viewing Agent Activity⁠

You can track what an agent has done in the same ways you track other teammates:

- Agent user pages show issue activity and contributions.
- In the My issues view, issues that you’ve delegated to agents will still appear—so you maintain visibility and control over the work in progress.
- Custom views filtered by Delegate to monitor agent involvement on specific types of issues or workflows.
- Use Insights sliced or segmented by Delegate to measure how much work is being directed to and handled by agents.

## Building Your Own Agent⁠

Developers can build custom agents using Linear’s developer platform. Documentation on agent APIs, authentication, and behavior can be found in our Developer Docs.

## FAQs⁠

[](https://linear.app/docs/agents-in-linear#collapsible-b67b2255d99c)Agents are not counted as billable seats in Linear. The services that provide the agent may have their own pricing structure, and you should refer to their documentation before installing.

[](https://linear.app/docs/agents-in-linear#collapsible-15c9dc4be206)Linear does not train on customer's data. We use models from common model providers, a complete list is available in our DPA.

Agents themselves would be 3rd party integrations approved by your workspace, in which case we can't speak to how the agent provider operates and you'd have to refer to the agent service provider.

[](https://linear.app/docs/agents-in-linear#collapsible-65a3c67ef5c9)Agents cannot sign in to the app, access admin functionality or manage users.



[](https://linear.app/docs/agents-in-linear#collapsible-2f97af0c8fbc)In the event that you have a member on your workspace with the same name as an Agent, the Agent's username will simply append a number at the end to keep it unique.

For example, Charlie would become Charlie1.

## ⁠

[PreviousFavorites](https://linear.app/docs/favorites)[NextMCP server](https://linear.app/docs/mcp)# Triage Intelligence

Source: https://linear.app/docs/triage-intelligence

---

# Triage Intelligence

Route issues by using LLMs to infer issue properties and relationships.

Available to workspaces on Business and Enterprise plans

![Hero image showing the product intelligence pane underneath issue title](https://webassets.linear.app/images/ornj730p/production/02067ce6f9065399e26861ebb5db223bdc0c897e-1494x584.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Triage Intelligence automates the time consuming assessment and routing steps required when triaging issues.

When enabled, issues in your workspace are analyzed by agentic models. Every future issue that enters triage is assessed against the rest of your data. This allows Triage Intelligence to proactively surface suggested issue properties and relationships. Accept, decline, or view more information about why a suggestion was made before making a decision. Issue properties suggested include teams, projects, assignees, and labels, and can be configured to auto-apply when suggested.

## Configure⁠

Enable Triage Intelligence by navigating to Settings > AI and toggling the feature on; this will enable the feature for every team. Taking this action requires admin permissions.

In teams where the functionality won't be useful, turn it off in that team's individual  triage suggestions settings. Or, if the scope of suggestions should be limited to that team and its sub-teams (don't suggest related issues in other teams, for example), set that behavior in the "Include suggestions from" menu.

### Issue property suggestions⁠

![Assignee suggestion detail explaining why the suggestion was made](https://webassets.linear.app/images/ornj730p/production/048e6fa94fdd12e50f05a37a4772354b73c5295d-1596x1034.png?w=1440&q=95&auto=format&dpr=2)

As organizations scale, questions like "who should work on this" or "what labels are usually applied in these scenarios" become harder to answer. Triage Intelligence uses historical trends evaluated against the current issue's content to proactively surface these suggestions. These suggestions appear alongside suggested duplicates and when issues are in Triage.

### Issue property suggestion automation⁠

![Image displays show, auto-apply, and hide options in team settings for product intelligence](https://webassets.linear.app/images/ornj730p/production/e073228328f5928cafd819cfddc2ec4a61674a85-1206x610.png?w=1440&q=95&auto=format&dpr=2)

In each team where Triage Intelligence is on, customize whether issue property suggestions appear, are hidden, or are auto-applied for different property types. Optionally, filter to specific values to suggest or auto-apply. Sub-team rules are inherited from the parent team by default, but can be overridden in sub-team settings.

### Duplicate and relationship detection⁠

![suggested related issue](https://webassets.linear.app/images/ornj730p/production/ec52900779f7dd8bdaceb6eb19c5564333dce947-1618x1146.png?w=1440&q=95&auto=format&dpr=2)

When Triage Intelligence determines there is a strong semantic similarity between an issue in Triage and an existing issue, a suggestion appears to accept the relation. Hover over the suggestion to see why it's appearing, and optionally accept it, dismiss it, or follow the reference to the secondary issue to analyze further.

### Refine suggestion behavior⁠

In Triage Intelligence settings at any level (sub-team, parent team, or workspace) you can provide additional guidance to refine suggestion behavior. This is best used reactively (for example, if you're seeing persistent suggestion themes that are incorrect) rather than as part of initial configuration for Triage Intelligence. When additional guidance is set at multiple levels like team and workspace, all are considered but the most local guidance is considered first and weighted most heavily.

### Triggering on issues outside Triage⁠

Triage Intelligence can still be run on issues in other statuses (if you're looking at a backlog issue for instance, and would like to double-check for duplicates).

To do so, use the Cmd / Ctrl + K menu to search for Find Suggestions. This will run in the background and enrich the issue with suggestions when available.

### FAQ⁠

[](https://linear.app/docs/triage-intelligence#collapsible-ba77def1bf1a)Linear does not utilize your data to train its own AI models. Any data processed to enable Linear’s AI features is shared with our trusted partners (AI subprocessors, see our DPA) exclusively to deliver those AI functionalities to you without permission to train on provided data.

To provide features powered by AI and large language models (LLMs), Linear utilizes voluntary data provided by the user in terms of labeling feature outputs (thumbs up/down) or in other opt-in ways. If you have any questions or concerns, please let us know at security@linear.app.

For further information, please see AI Security FAQ in our Trust Center.

[](https://linear.app/docs/triage-intelligence#collapsible-43590e26ceb6)Yes! Click on the Triage Intelligence window in an issue in Triage while it's processing, or on the suggestion overflow menu once suggestions have been made.

![Expanded reasoning for Product Intelligence suggestion](https://webassets.linear.app/images/ornj730p/production/1ebe7390a9bb84355abb0e761696b5712df3bcde-1600x1718.png?w=1440&q=95&auto=format&dpr=2)

[](https://linear.app/docs/triage-intelligence#collapsible-af6f47a10749)Quick suggestions in the issue composer and property menus are available in all plans in Linear. These leverage search, so they're faster but much less thorough than Triage Intelligence's suggestions.

[](https://linear.app/docs/triage-intelligence#collapsible-ba4cd7ec848a)Processing new issues in Triage is expected to take 1-4 minutes to generate high-quality suggestions. Because most issues aren’t triaged this quickly, we make a tradeoff here with spending more time to yield better results. We do expect speed improvements over time as models improve.







[PreviousMCP server](https://linear.app/docs/mcp)[NextAirbyte](https://linear.app/docs/airbyte)