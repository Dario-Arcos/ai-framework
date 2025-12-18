# Table of Contents

- API and Webhooks
- Audit log
- Billing and plans
- Exporting Data
- Get login events for an user
- Importer
- Invite members
- Members and roles
- Private teams
- SAML
- SCIM
- Security
- Simple query to get last 250 events
- Sub-teams
- Teams
- Workspaces

---

# Workspaces

Source: https://linear.app/docs/workspaces

---

# Workspaces

The first step to using Linear is to create a workspace for your team.

![Linear workspace switcher](https://webassets.linear.app/images/ornj730p/production/978e5db54e597de0441d6a8cf8e6dd650a237aed-1264x673.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

A workspace is the home for all issues and interactions for an organization. We recommend organizations staying within a single workspace as this is the conceptual model we use when designing the product.

When a workspace is created, Linear automatically creates a default Team with the same name.

## Workspace Settings⁠

To navigate to your workspace settings click your workspace name in the upper left and select Settings.

Members will see settings relating to Issues, Projects and Features.

Admins will see an additional "Administration" section in their Workspace settings that is not viewable by members or guests.

![Administration settings](https://webassets.linear.app/images/ornj730p/production/903aa378bb458c634ef798c0aff3dda591da05ea-2344x1694.png?w=1440&q=95&auto=format&dpr=2)

From the Settings > Administration section, admins will be able to:

- Update a Workspace name and URL
- Manage login preferences
- Turn on/off third-party app review requirements (Enterprise feature)
- Set up Project Updates
- Turn on/off the Initiatives feature
- Add or remove members to the Workspace
- Import or export issues
- Change plans
- View or update billing information

Admins and Members will be able to:

- Create workspace-level labels
- Create custom project statuses
- Create workspace-level templates for issues, projects, and documents
- Apply SLA rules (paid feature)
- Customize Asks templates (paid feature)
- Add custom emojis
- View your plan type
- Configure workspace-specific integrations like GitHub and GitLab, Slack, Figma, and Sentry. Integrations can be configured by anyone in your workspace as long as they have the required permissions from the integrated service.

### Delete workspace⁠

Deleting a workspace includes deleting user and issue data. Admins can delete a workspace under Settings > Workspace > General. Please note this action is not reversible.

## Multiple workspaces⁠

You can create multiple workspaces in Linear under a single account (e.g. tied to a specific email). Each workspace will have distinct member lists and separate billing plans, even if you connect to them from the same account.

If you are using Linear for both work and personal purposes, we recommend you create multiple Linear accounts with separate email addresses.

To add a workspace from another email account:

- Click on your workspace name in the top left corner
- Hover over Switch workspace.
- Select Create or join a workspace.
- If you have other workspaces associated with your user account, you will see a list of those workspaces to select.

You can also switch workspaces by typing  O then W.

[PreviousPull Request Reviews](https://linear.app/docs/pull-request-reviews)[NextLogin methods](https://linear.app/docs/login-methods)# Teams

Source: https://linear.app/docs/teams

---

# Teams

Create teams in your workspace to organize different types of work functions.

Different plans support different numbers of teams: details available below.

![linear app showing teams page](https://webassets.linear.app/images/ornj730p/production/2aa78477eeb62feb13b2bc41395ee5c69464a763-1771x948.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

A workspace is composed of one or many teams. Teams typically represent groups of people who work together frequently, though in some cases you may choose to structure teams as parts of a product. Teams contain issues, and can have team-specific projects (though projects can also be shared between teams).

By default, when you create a workspace we'll generate a team for you with the same name. It's up to you how to split up teams and users can be part of one or many teams.

Consider grouping teams by:

- Teammates who work together frequently.
- Areas of work such as marketing, mobile app, etc.
- Keeping everyone on one team is the simplest approach (best for small teams).

![image](https://webassets.linear.app/images/ornj730p/production/c377a88c314fd6d0ceacf255f927c3220f1d9a07-16x16.svg?q=95&auto=format&dpr=2)

If you aren't sure how to split up your teams, start with one or two. It's easy to add more teams in the future, copy settings from existing teams, and move issues from one team to another.

## Your teams⁠

Teams you have joined will appear in your sidebar.

Each team has the following pages to organize your work:

- Triage* Newly created issues to be reviewed, assigned or prioritized before entering the team's workflow
- Issues  Default views of all issues in this team
- Cycles* Review current, past and upcoming cycles to plan and schedule your team's workload
- Projects Default views of all projects linked to this team, along with custom views of projects that you can add and edit.
- Views Custom views filtered to this team's issue, visible to members of the team

Sections marked with an * are opt-in and need to be enabled in team settings.

### Team settings⁠

Team settings allow you to configure each team differently to support different workflows.

To access your team's settings:

- From the app sidebar, hover over the team name, click the three dots ··· menu, and select "Team settings."
- From Settings, find the team you want to update from Your teams and select it. It'll take you to the team's unique settings page.

From the team's settings page, you can update the name, icon, and identifier for the team. Changing the issue identifier is a safe action to take -- old URLs containing the original identifier will automatically redirect to the new issue URL.

You can also configure the following settings:

## Working with other teams⁠

### View other teams⁠

Teams you navigate that you are not a member of will show up in your sidebar under a temporary Exploring section.

You can search for and view issues, projects, and documents from other teams, too, as long as those teams are not private.

### Access control⁠

All members of a workspace can view and join teams as long as the team is not private.

Anyone in the workspace can create issues for other teams or be assigned issues in other teams, too. You don't have to join teams to collaborate with others unless you use them frequently and want them to show up in your sidebar.

## Create teams⁠

To join other teams or create a new one, navigate to settings and select "Join or create a team" from the bottom of the settings sidebar.

- In Settings below the list of your existing Teams, click the + "Add team"
- From command bar Cmd/Ctrl + K, select "Create new team"
- Admins can create teams from their Teams page in settings

### Team limits⁠

The number of teams that can be created is dependent on a workspace's subscription:

### Team creation settings⁠

Private teams: During team creation, you'll have the option to copy over settings from an existing team and make the team private.

Copy team settings: If you want to copy an existing team's settings when creating a team, use the "Copy team settings..." option when creating a new team.

Restrict team creation: Admins can restrict team creation to only admin users under Settings > Administration > Security.

### Tips on structuring teams⁠

Keep these tips in mind when deciding how to structure your workspace's teams:

- Issues are tied to teams. Think about how you prefer to manage your work and interact with features such as the backlog and archive.
- Workflows can be customized per team. Different work areas or internal teams (e.g. engineering, design, marketing, sales) may require different statuses.
- Cycles are team-specific. You can set up cycles so that all teams follow the same schedule, but you can't view more than one team's cycles at once. Think about how you manage your work, run meetings, measure progress, and whose work you'll want to oversee as a manager.
- Projects can belong to a single team or be shared across many teams (but issues can only be tied to one team)
- Sub-issues can be assigned to any team or member in the workspace, not just the parent issue's team.
- Other features are team-specific but also easy to copy over to another team, such as pull request automation and issue templates. Labels are team-specific but you can create views that show issues from multiple teams as long as the label has the same name across them.

## Manage teams⁠

### Make a team private⁠

Business and Enterprise support private teams. To make an existing team private, go to Settings > Your teams > Team and then scroll down to the Danger Zone.

### Join / leave / invite teams⁠

Admins can add users to a team in Settings > Administration > Members.

Members can join and leave teams on their own, by hovering over the team name, then clicking the ··· and selecting to Join team or Leave team... To join a private team, members must be invited by the team owner.

### Sub-teams⁠

On Business and Enterprise plans, you can organize teams in a hierarchy (for instance, Mobile might be the parent team of iOS and Android). Learn more about sub-teams here.

### Delete a team⁠

Deleting the team will also permanently delete its issues. Once the grace period ends, this can't be undone and your data cannot be recovered by Linear.

You will have 30 day grace period to restore the team under Recently deleted teams. Access this by opening Settings > Teams and selecting the Recently deleted option in the menu. Restore a team through its overflow menu on the far right of its row.

![Recently deleted teams under Settings > Teams](https://webassets.linear.app/images/ornj730p/production/a62173417d0271899459246defc61f4adda4d536-1526x748.png?w=1440&q=95&auto=format&dpr=2)

If you may need the data in the future, consider making the team private, exporting the team's issues as a CSV before deleting, or moving the issues to a different team.

### ⁠



[PreviousExporting Data](https://linear.app/docs/exporting-data)[NextPrivate teams](https://linear.app/docs/private-teams)# Private teams

Source: https://linear.app/docs/private-teams

---

# Private teams

Create private teams for issues that should only be accessed by certain workspace members.

Available to workspaces on our Business and Enterprise plans.

![Linear app showing a private team called Private Team.](https://webassets.linear.app/images/ornj730p/production/7c81aa05636cdf517bf18dd134a24077ce4e1f7a-1310x1064.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

If you want a team to be public to all but a particular set of users, consider using the Guest role instead of making the team private.

This feature is available on Linear's Business and Enterprise plans. Anyone in the workspace can create a private team or make an existing team private.

Private teams are helpful in cases where:

- Work is sensitive and should be limited to only some team members (e.g. HR, customer data, founders or exec team).
- You want a personal team to keep track of issues.

## Visibility⁠

Private team: Workspace admins can see all private teams in settings under Settings > Administration > Teams, update team settings, or join a private team by adding themselves as a member. If an admin attempts to join a team, they will receive a pop-up warning before confirming.

![Pop-up when an admin attempts to join a private team](https://webassets.linear.app/images/ornj730p/production/1fb4d5a858c6cbd4313e4b17c057bab9c325610f-1014x960.png?w=1440&q=95&auto=format&dpr=2)

Issues: Those who are not a member of the private team will not be able to see issues associated with the team. You cannot @ mention a member in an issue in the private team if they are not already a member of the private team.Projects created under public teams: Projects created under public teams can also be shared with private teams. Only private team members will be able to see that the project has been associated with their team. Similarly, project issues related to the private team will only be visible to members of that team. If all public teams are removed from the project, it will become private and only visible to members of the private team from then on.

Projects created under private teams: Projects created under private teams are visible to the private team members only. If the project is shared with a public team later on, the project will become visible to others. The name of the private team or issues from that team do not become visible to non-members.

Initiatives: Members of a private team can see its projects on the associated initiatives but those projects won't be visible to others.

## Configure⁠

When creating teams from workspace settings, toggle the option Make team private.

!["Make team private" option when creating a team](https://webassets.linear.app/images/ornj730p/production/acb8f03aac5717df21fd3465d2a4c8f124cac9ef-1378x226.png?w=1440&q=95&auto=format&dpr=2)

To make an existing team private or vice versa, go to your team's settings (right-click on the team from your sidebar) and then scroll down on the team's settings page to the Danger Zone to make the team private.

Any assignees that are not members of the private team will be removed and any subscribers to issues in the newly private team will be unsubscribed.

!["Change team visibility" section in Team settings.](https://webassets.linear.app/images/ornj730p/production/c9db20ba59b05ea9adada48c845e717ce600ef6a-1462x418.png?w=1440&q=95&auto=format&dpr=2)

## Private team members⁠

The person who creates a private team or converts an existing team to private becomes the default owner of the private team.

Owners of a private team can go to Members (from the team's settings page) to invite other workspace members to the team or promote an existing team member to team owner (admins can search for the team from Settings > Administration > Teams and then select the three dot menu to access this page).

Members of a private team can leave the team on their own, but they won't be able to re-join the team without an explicit invite.

## Exports⁠

When exporting issues from the workspace using our Export tool, admins can choose to include issues from any private team.

![Option to include private teams in an export.](https://webassets.linear.app/images/ornj730p/production/db2c52ae1cbf88d897d62d65ac4a88da316e7f72-1426x544.png?w=1440&q=95&auto=format&dpr=2)

## API Security Considerations⁠

If your workspace has set up custom integrations or apps or is working with third party integrations, please consider their behavior and who has access to their output when adding private team data to Linear issues.

The API, webhooks, and integrations such as Zapier can expose a user's private team and issue titles. It's possible to access private issue data with the API if you are using a personal API key of a user that has access to private teams. Webhooks can also expose data from private teams as webhooks for private teams can be set up by team owners and workspace admins.

## Integrations⁠

Some existing integrations have limitations to account for private data, while others will have more complete access to all workspace contents.

[PreviousTeams](https://linear.app/docs/teams)[NextSub-teams](https://linear.app/docs/sub-teams)# Sub-teams

Source: https://linear.app/docs/sub-teams

---

# Sub-teams

Group sub-teams underneath a parent team. Feature settings configured in the parent team drive alignment throughout the group.

Available to workspaces on our Business and Enterprise plans.

![Shows a mobile parent team with nested ios and android teams in Linear's sidebar](https://webassets.linear.app/images/ornj730p/production/8f60bea54b24eabdcf5877bba111161c744ef805-1072x749.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Sub-teams allow you to reflect your organization's structure in Linear, making it easier to understand and manage work across different levels of your company. Create new sub-teams to organize work into specialized units as your organization scales while keeping existing workflows standard within the group.

Concepts like cycles and labels set in a parent team are inherited by its sub-teams, allowing sub-teams to operate well both as individual units and as a unified whole.

## Basics⁠

### Update an existing team to a sub-team⁠

Go to Settings > Teams > Team hierarchy and select another existing team as its parent. Taking this action requires admin permissions. To protect the privacy of private teams, a private parent team may have only private sub-teams.

![Shows selecting a parent team under Team settings > Team hierarchy](https://webassets.linear.app/images/ornj730p/production/c954ed27ec8cbb0f86a1cf8308feda3938447985-2104x1009.png?w=1440&q=95&auto=format&dpr=2)

### Create a new sub-team⁠

When creating a new team, optionally designate it as a sub-team at creation. To protect the privacy of private teams, a private parent team may have only private sub-teams.

![Selecting team hierarchy when creating a new team](https://webassets.linear.app/images/ornj730p/production/560c41f14b0a6a1a18aa982097c82d3cbd7fe67c-1866x1448.png?w=1440&q=95&auto=format&dpr=2)

### Configure a sub-team ⁠

Once you've created a sub-team, a wizard will take you through any conflicts that need to be resolved. Common tasks include normalizing statuses between parent and sub-teams and resolving duplicate label conflicts.

After configuring a sub-team, check its settings to customize features unique to that team (GitHub PR automations, for instance) to ensure they meet the sub-team's needs.

### Private parent and sub-teams⁠

If a parent team is private, its sub-teams must also be private. If a parent team is public, its sub-teams may be public or private.

As with all private teams in Linear, a user can see private team-specific data only when they belong to the private team themselves.

As an example, given a private parent team A with private sub-teams B and C, a user belonging to A and C cannot see issues belonging to B, even if those issues are in a project or view shared with teams A and C. If there is a project shared between teams B and C, this user would only see issues belonging to team C in the project.

### Un-nesting a sub-team⁠

Navigate to the sub-team's settings and click Remove from parent... under the "Team hierarchy" section. Once removed, you can expect:

- Labels, issue status, cycles, and members will no longer be inherited by the sub-team. We have a warning about this when you start to un-nest the team. Broadly speaking, inherited items that are not currently in use will be permanently removed, while anything actively used will be converted into independent copies so issues remain fully intact.
- Specifically, any inherited labels or templates that weren't used in the old sub-team are not carried over. Those that are used become standalone versions for that team.

## Parent and sub-team settings⁠

### Parent team feature settings inherited by sub-teams⁠

Certain settings from a parent team are enforced throughout all sub-teams.

### Parent team feature settings accessible to sub-teams⁠

Sub-teams benefit from other features used in the parent team, and retain the flexibility to create similar entities scoped to the sub-team.

### Independent feature settings in sub-teams⁠

Other features in sub-teams have no relation to the parent team and should be customized to meet the needs of the sub-team specifically. These include:

- Team timezone
- Recurring issues
- Team Slack notifications
- GitHub/GitLab automations

[PreviousPrivate teams](https://linear.app/docs/private-teams)[NextIssue status](https://linear.app/docs/configuring-workflows)# Members and roles

Source: https://linear.app/docs/members-roles

---

# Members and roles

Linear provides several role types to help you control access and permissions across your workspace. Each role gives team members the right level of access—from full administrative control to limited guest visibility.

## Overview⁠

Administrative roles can manage workspace members and their from Settings > Administration > Members. This page lists all active and suspended members and allows filtering by role or status (Pending invites, Suspended, or users who have left the workspace).

On Enterprise plans with SCIM enabled, some or all member management will be accomplished through your IdP instead of the Members settings page.

## Managing user roles⁠

### Changing a member's role⁠

To update a user’s role:

- Go to Settings > Administration > Members page
- Hover over a member’s row
- Click the overflow menu (⋯)
- Select the Change role...

### Suspend a member⁠

Administrative roles can suspend a member from the workspace:

- Go to Settings > Administration > Members
- Hover over a member’s row
- Click on the overflow menu (⋯)
- Select Suspend user...

Suspended users lose all access immediately and are removed from your next billing cycle. They remain visible in the members list for historical purposes—for example, when viewing issues they created or were assigned to.

To view issue activity for a suspended user, visit their profile page at:linear.app/<workspace-name>/profiles/<username>

Admins can access this link from the user’s avatar or by filtering the Members page for Suspended users.

### Viewing workspace admins⁠

Any member who needs to quickly identify workspace administrators can:

- Open Command menu Cmd/Ctrl K and select View workspace admins
- Navigate directly to linear.app/settings/view-admins

## Role types⁠

### Workspace owner⁠

The workspace owner role is only available on Enterprise plans

Workspace owners have full administrative control, including access to the most sensitive settings such as billing, security, audit log, workspace exports, and approvals and team access management for OAuth applications. Admins in these workspaces, by contrast, have more limited permissions—ideal for routine workspace management.

In workspaces that need more flexibility, workspace owners can configure which roles can perform certain workspace-level actions via Settings > Administration > Security under the "Workspace restrictions" section.

SCIM-managed workspaces

Enterprise workspaces with brand new SCIM setups should create a linear-owners group to manage workspace owners, in addition to any other role groups described here.

If you are upgrading an existing workspace that uses SCIM to the Enterprise plan, please look at this article to understand what actions you need to take.

### Admin⁠

Admins have elevated permissions to manage routine workspace operations. This role is well-suited for managers, team leads, and operations-focused members.

Free plan behaviorAll workspace members become admins automatically

Basic and Business plan behaviorThe user who upgrades the workspace is granted the admin role

Enterprise plan behaviorAdmins will have limited permissions

### Team owner⁠

Available on Business and Enterprise plans

Delegated control over how individual teams are run, without routing every change through workspace owners or admins.

Configure team owners

- Go to Team settings > Access and permissions and adjust settings to be restrictive to team owners only
- Navigate to Team settings > Members to promote members to team owners

There is no limit to the number of team owners a team can have, and teams are not required to have a team owner.

Who are team owners?

- Workspace admins and owners are automatically team owners for all teams they can access. For any newly created team, the creator becomes a team owner by default
- Any team member can be promoted to team owner by an existing team owner or a workspace admin/owner
- Team owners in the parent team are team owners in the sub-teams
- Guests cannot be team owners

Team owner only operations

Certain critical actions are restricted to team owners only:

- Deleting a team
- Making a team private
- Changing a team's parent

Configurable permissions

![Team permissions](https://webassets.linear.app/images/ornj730p/production/2dfa78eee5af719095be345826537353c6d8f27b-1414x748.png?w=1440&q=95&auto=format&dpr=2)

From Team settings > Access and permissions, team owners can choose whether to allow all members or only team owners to manage the following:

- Issue Label Management - Control who can create and edit team issue labels.
- Template Management - Control who can create and edit team templates.
- Team Settings Management - Control who can manage workflow statuses, cycles, triage rules, agent guidance, and other team settings.
- Member Management - Control who can add new users to the team. Note: Only team owners can add guest users, regardless of this setting.

Permission settings are not inherited from parent team to sub-team.

Team access

From Team settings > Access and permissions, team owners can also choose to restrict how members can join your team. By default, any member of your workspace can join a non-private team. Team owners now have the option to restrict access to only members they add or invite.

![Team access](https://webassets.linear.app/images/ornj730p/production/10c484efbd8dc5bfd8906dbf176ee9bf046a75e9-1368x496.png?w=1440&q=95&auto=format&dpr=2)

### Member⁠

Members can collaborate across teams they have access to and use all standard workspace features. They cannot access workspace-level administration pages

### Guest⁠

Guest accounts are only available on Business and Enterprise plans, and are billed as regular members.

Guest accounts grant restricted access to specified teams—ideal for contractors, clients, or cross-company collaborators.

Guests can

- Access issues, projects, and documents for the teams they are explicitly added to
- Take the same actions as Members within those teams

Guests cannot

- View workspace-wide features such as workspace views, customer requests, or initiatives
- Access settings beyond their own Account tab

Sharing projects with guests

If a project spans multiple teams:

- Guests will only see issues belonging to the teams they’re part of
- They will still see the project shell, but only with their allowed team’s issues visible

Integration security

Integrations enabled for the workspace will be accessible to guest users, which could potentially allow them to access Linear data from teams outside those they're invited to join. To prevent data leakage:

- For Linear-built integrations (GitHub, GitLab, Figma, Sentry, Intercom, Zapier, Airbyte): Ensure guest users don't have access to your accounts on those services
- For integrations requiring email authentication (Slack, Discord, Front, Zendesk): These should automatically limit access to only issues and data in invited teams
- For third-party integrations: review access individually or contact the integration provider in the Integrations directory.

## FAQ⁠

[](https://linear.app/docs/members-roles#collapsible-a8e38cc23b72)If a user is in two groups, they will get the permission of the most recent group that was pushed.



[PreviousInvite members](https://linear.app/docs/invite-members)[NextSecurity](https://linear.app/docs/security)# Invite members

Source: https://linear.app/docs/invite-members

---

# Invite members

Invite and manage members of your workspace.

![Linear app settings page showing the Manage members settings](https://webassets.linear.app/images/ornj730p/production/24df0e4ada358c601233c729518f9d91c04b5663-2160x1327.png?w=1440&q=95&auto=format&dpr=2)

## Send an invitation⁠

To send an invitation:

- Go to the Settings > Administration > Members
- Click the Invite button.
- Enter the invitee(s) email address. To add multiple invitees, separate each email by commas.
- Under Invite as..., select the role you want the invitee(s) to have when joining the workspace (paid plans)
- You can select the team(s) you want your invitee(s) to automatically join.
- Click Send invites. New members will receive an invite link via email along with steps to join the workspace.

In case an email server is filtering out invitation emails, we recommend adding notifications@linear.app and/or pm_bounces@pm-bounces.linear.app to your allowlist as trusted senders in email settings.

### Email Options by Plan⁠

All members of a workspace on the Free plan are considered an Admin, thus anyone can send invitations to new members.

By default, only Admins can invite members on paid plans. Admins can allow all users to invite members by toggling on Allow users to send invites within Settings > Workspace > Security.

For SAML-enabled workspaces, ensure that members are given access in your identity provider (IdP) before inviting them, depending on your login requirements.

Users who have access to Linear through your IdP may login to the workspace without needing an invitation. If no account existed for this user before, one will be created through Just-In-Time (JIT) provisioning. The user will show up as a member in Linear from this point on.

Reach out to support@linear.app if a new user's email does not match other emails in your workspace, as it will have to be added to the SAML configuration as an approved domain.

When SCIM is enabled for your workspace, you can no longer manually invite users from the Linear members page.

Learn how adding or removing users affects billing.

## Approved email domains⁠

![Approved email domains](https://webassets.linear.app/images/ornj730p/production/68acab16d4f74f4a6c694d2f6f934fe544c41699-1392x296.png?w=1440&q=95&auto=format&dpr=2)

To save time from manually inviting new members, Admins can navigate to  Settings > Administration > Security and add allowed email domains. Once set up, anyone with the matching email domain can join the workspace without an invitation or approval. This is only designed to streamline the joining process and does not prevent users from creating new workspaces with that domain email.

Users who are creating new accounts will see a prompt to join the workspace during the onboarding flow.

For members with existing accounts, click on your current workspace icon, hover over Switch workspace, select Create or join a workspace. The workspace with the allowed email domain should show up under available workspaces.

![image](https://webassets.linear.app/images/ornj730p/production/95a933639d33ab31c5ac1c56744755344279f769-16x16.svg?q=95&auto=format&dpr=2)

Please review this list regularly to ensure it is up to date.If you ever cancel your domain or transfer control of a domain to another organization, you'll need to remove this domain from your approved email domains in Linear to prevent unwanted access to the workspace.

## Invite links⁠

Navigate to Settings > Administration > Security to generate a unique link that allows for anyone with the URL to join your workspace. If enabled, please ensure this link is only shared internally with your organization.

Invite links are persistent and reusable. They can be set to a new unique value with the "Reset invite link" button.

## Invite & Assign⁠

Invited users can be assigned issues or marked as project leads before they accept their invitation.

- On any issue or project, open the assignee selection menu and choose "Invite and assign…". After inviting them, search for them in assignee/lead menus to continue to allocate work.
- Or, when sending an invite from the workspace settings members page, click on the invited user and create new issues from their user page. These will automatically be assigned to them.

## FAQ⁠

[](https://linear.app/docs/invite-members#collapsible-c7f9fd96c1e9)The API tokens will be revoked and invalidated.





[PreviousLogin methods](https://linear.app/docs/login-methods)[NextMembers and roles](https://linear.app/docs/members-roles)# Security

Source: https://linear.app/docs/security

---

# Security

Learn more about our data security practices and compliance measures.

![Lock icon for the security page](https://webassets.linear.app/images/ornj730p/production/0f55ef41e6ad21c246445ed595e65a966851aa51-2160x1327.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Linear is built with best-in-class security practices to keep your work safe and secure at every layer. This includes state-of-the-art encryption, safe and reliable infrastructure partners, and independently verified security controls.

Refer to our Data Processing Agreement (DPA) for specific details.

## Shared responsibility⁠

Under our shared responsibility model, Linear secures the components that we control, including the application layer, underlying platform, and cloud infrastructure. This includes protecting against threats targeting these components through security controls, monitoring, and incident response.

Customers are responsible for how they use Linear. This includes configuring workspace security and access, determining what data they store and retain, managing API keys and integrations, and monitoring their audit log.

## Certifications⁠

Linear is compliant with GDPR, SOC 2 Type II, and HIPAA.

For HIPAA compliance, we offer a Business Associate Agreement (BAA) to customers on our Enterprise plan. Please contact us at sales@linear.app for more information.

To request other security and compliance documents for Linear, please visit our Trust Center. If you have further questions about any of our certifications, please let us know at support@linear.app.

## Data regions⁠

When creating a new workspace, you have the option to select the region where you want your data to be stored. The available options are:

- United States
- European Union

Your data region selection chosen at workspace creation is permanent, and cannot be updated at a later date.

Most of the data associated with the workspace — including issue descriptions and uploaded attachments—will only be stored in the selected region. Regardless of the region you select for your workspace, the following data is always stored in the United States:

- Information about the workspace, all user account information and user created API keys, used to authenticate users and direct them to the right region.
- Notification emails that are sent to workspace users will be stored in the U.S. for 7 days by our email sending partner.
- Usage data, used for analytical purposes.
- Workspace data and user account information used for analytical purposes. This data has been stripped of any information that might be confidential, including issue titles and descriptions, comment content, project names, team names, and document content and initiative names among others.
- User account information associated with any crashes that happen on the client or when processing a client or API request, in order to be able to debug crashes.

## Report a vulnerability⁠

You can read more about reporting any suspected security issues, what's in scope for reports, and other guidelines on our report a vulnerability page.

## FAQ⁠

[](https://linear.app/docs/security#collapsible-36d9b53c6e46)All communication outside our cloud environment is encrypted. In addition, our databases are encrypted at rest.

[](https://linear.app/docs/security#collapsible-08333af9d37c)Contact us at support@linear.app and we can help.

[](https://linear.app/docs/security#collapsible-0ca3ad76b0e0)For HIPAA compliance, we offer a Business Associate Agreement (BAA) to customers on our Enterprise plan. Contact us at sales@linear.app.



[PreviousMembers and roles](https://linear.app/docs/members-roles)[NextSAML](https://linear.app/docs/saml-and-access-control)# SAML

Source: https://linear.app/docs/saml-and-access-control

---

# SAML

Customers can opt to enable SAML for their workspace to manage logins through an Identity Provider.

Available to workspaces on our Enterprise plan

![Login screen on the Linear desktop app](https://webassets.linear.app/images/ornj730p/production/8f3cc06f38271644cc9bbe3868f3c18e66b09807-2160x1327.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

We support most identity providers (Okta, Entra, OneLogin, LastPass, Auth0, Bitum, etc.)

Once SAML is enabled, members on SAML-approved domains will be required to login via SAML by default, while you can allow other login types for users on other domains.

User sessions won't be logged out or notified at the time of enabling, but affected users will need to sign in with SAML from that point on.

Members can login via your identity provider's website or by clicking the option to Continue with SAML SSO on the login page.

Guests are an exception, and will be able to sign in by selecting Continue via email.

Admins and Owners can log in through any method to prevent lockouts.

## Configure⁠

- Navigate to Settings > Administration > Security.
- Under the "Authentication methods" section, click Configure next to "SAML & SCIM".
- Enter the requested details from Linear into your IDP and press "Continue"
- You can paste in an XML URL or the raw XML text to complete the configuration with your identity provider. If you're not sure where to find this in your identity provider, take a look at their documentation or reach out to us for help.

You can make changes to your configuration later on from ... > Edit Configuration within the SAML authentication & SCIM provisioning settings page.

If you want to add our logo in your Identity Provider, our Brand Assets are available for download here.

## Multi-SAML Setup⁠

If you're working with multiple IDPs, you can add additional configurations from the + Icon beside Connected identity providers in your SAML settings. Each IDP can be associated with 1 or more domains to determine which IDP each user need to authenticate with.



## Just-in-Time Provisioning⁠

When a new user signs in via SAML for the first time, Linear creates the account using the data provided by your IDP. After the account exists, later SAML logins won’t overwrite profile details.

The following properties are set during account creation:

- Name: taken from name attribute if it exists. If not, created from firstName and lastName attributes combined or else drawn from displayName.
- Email: taken from the SAML NameID which must be a valid email address
- Avatar (profile image): taken from any of  avatarurl || photo || picture || profilepicture || profilephoto
- Username: Generated from the supplied Name (as detailed above) or email address if no name is provided. This value must be unique and numbers will be appended if an existing user has this username already.

User profile fields are only populated during initial account creation. Subsequent SAML logins do not update the user’s profile automatically; changes can be made in Linear or via SCIM provisioning if enabled.



## Domain Management⁠

### Allowed domains⁠

Once you have configured your settings for an IDP, you'll need to add approved domains for this IDP under the settings for SAML-approved email domains. You will need to add a TXT code to your DNS record to claim this domain.

Please reach out to support@linear.app if you have any trouble claiming a domain, or if you are working across multiple workspaces.

### Other auth methods for other domains⁠

You can choose to allow non-SAML logins only for other email domains, if you are working with contractors or other members that don't have accounts in your IDP.

### Disable new workspace creation⁠

Once SAML is enabled, you have the option to prevent non-admins from creating new Linear workspaces with their email credential from the domain you claimed during setup. This can be useful to make sure all work is consolidated in a single Linear workspace.

## FAQ⁠

[](https://linear.app/docs/saml-and-access-control#collapsible-9d482fded492)If SAML is enabled for your workspace, you must login via your SAML service's website or by selecting the "Continue with SAML SSO" option on the Linear login page.

If you're getting an error about the workspace not being accessible and it is your first time logging into Linear with SAML, please try logging out of the SAML provider and then logging in.

If you get repeated errors, then please contact support.

[](https://linear.app/docs/saml-and-access-control#collapsible-1f5fd84e52c5)For SAML-enabled Workspaces, you can still invite Members as normal from Linear's side. However, you'll need to make sure that members are given access in your identity provider(IdP) in order to log in. New members who login successfully with SSO will be automatically provisioned using Just-In-Time (JIT) provisioning and an account will be created for them.

[](https://linear.app/docs/saml-and-access-control#collapsible-c8723a1108d8)We support enabling SCIM 2.0 for you on the Enterprise plan if you have SAML enabled. More details here.

[](https://linear.app/docs/saml-and-access-control#collapsible-9837f0bfad68)Guests must be invited over email to make sure they're permissioned appropriately. In order to invite them, enable a login method for users outside of your claimed domain as pictured, then choose "Invite" in Settings > Administration > Members to invite your Guests.



![Security > Allow other authentication methods for all additional email domains > On](https://webassets.linear.app/images/ornj730p/production/c85fef522711eac3e180daedcb57d89c4767625b-797x528.png?w=1440&q=95&auto=format&dpr=2)

![Security > Allow other authentication methods for all additional email domains > On](https://webassets.linear.app/images/ornj730p/production/c85fef522711eac3e180daedcb57d89c4767625b-797x528.png?w=1440&q=95&auto=format&dpr=2)



[PreviousSecurity](https://linear.app/docs/security)[NextSCIM](https://linear.app/docs/scim)# SCIM

Source: https://linear.app/docs/scim

---

# SCIM

SCIM, or System for Cross-domain Identity Management allows for the automation of user provisioning for your Linear workspace.

Available to workspaces on our Enterprise plan

![Security Settings page for SCIM in the Linear app](https://webassets.linear.app/images/ornj730p/production/de09045809402f74f116b880078a1b7b4b774bb4-2160x1326.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

With SCIM enabled, user accounts can be automatically created, updated, and suspended based on your IDP settings—eliminating the need for manual account management in Linear. This integration helps ensure that your team's access stays in sync with your organization’s directory.

## Configure⁠

### Enable and test⁠

- Navigate to Settings > Administration > Security.
- Under the "Authentication" section, click Configure next to "SAML & SCIM".
- Toggle the option to enable SCIM
- Click "View configuration" to get your SCIM base connector URL and Bearer Auth token. Keep these values at hand as you will need them to configure SCIM in your Identity provider.

Once enabled, Admins will not be able to manage users from within Linear as they will be kept up to date through your identity provider.If necessary, you can temporarily enable a manual override to allow user suspension. This may be useful if you need to remove members or Guests that were added to Linear before you enabled SCIM.

- In OneLogin's Admin panel > Applications, click Add App
- Search for the "SCIM Provisioner with SAML (SCIM v2 Enterprise, full SAML)" app and add
- Click on the Configuration tab and add your SCIM base URL and Bearer token
- Click on the Provisioning tab and Enable Provisioning
- Save your App

- In the Okta admin pages, open the Linear application you have for SAML 2.0
- In the General tab, click Edit and choose SCIM in the Provisioning section and Save
- In the Provisioning tab, enter the SCIM Base connector URL you generated from Linear
- For the Unique identifier field for users section enter email
- For Supported provisioning actions you can enable "Import New Users and Profile Updates", "Push New Users" and "Push Profile Updates". Also select "Push Groups" if you are planning to sync selected Okta groups with Linear teams. "Import Groups" is optional, but can be selected to import existing Linear teams to be later linked to Okta groups.
- For Authentication mode field, choose HTTP Header and enter your Bearer token generated from Linear. You can now test the configuration and save
- Lastly, return to the Provisioning tab in Okta and edit your settings under "To App" to enable the SCIM functionality needed for your Linear application (Create, Update and Deactivate users)

![Okta settings with provisioning options checked for Linear app](https://webassets.linear.app/images/ornj730p/production/d5c19b976eca09f26ecea5eea1d19c63c0b67a82-1076x902.png?w=1440&q=95&auto=format&dpr=2)

## Group push⁠

Linear's SCIM integration also supports group push. From your side all you have to do is start pushing groups from your Identity provider to Linear. These will then map 1:1 with teams in Linear.

To link an existing team to a Group, you first need to import teams from Linear. These teams will be recognized as groups by your Identity provider. Once imported, you can then select the appropriate team when configuring group push.

Once a team is linked to a Group, this team's membership is solely managed through your identity provider and not in Linear directly.

If you choose to disconnect the Push group from Linear in the future, you may see different options offered by your IDP:

- Opting to delete the group on Linear's side will remove all members from the Linear team and convert the team to private. Issues will remain unchanged.
- Disconnecting the group without sending a delete request will leave the team unchanged and not sync any changes to the team on Linear's side. From the team Settings > Danger Zone you can then unlink SCIM manually to resume managing the team as normal.

![Unlink from SCIM option in Linear team settings](https://webassets.linear.app/images/ornj730p/production/3c82a6bf3de2d2fdf814e9f9c721cb6c0f229d28-915x274.png?w=1440&q=95&auto=format&dpr=2)

## Provisioning Roles⁠

By default, all accounts created via SCIM via individual assignment or group push are provisioned as Members. You can also choose to provision specific users into Owner (if on an Enterprise plan), Admin and Guest roles directly from your IDP.

To do this, you need to create linear-owners (only if on an Enterprise plan), linear-admins and linear-guests as push groups on the IDP side and sync their members with Linear.

Once these have been connected to Linear, any users added to the group will be given the corresponding role in Linear.

- These particular groups do not create Teams in Linear or sync membership with existing teams.
- You can rename these groups from your IDP after you've pushed them at first as linear-owners (if applicable), linear-admins and linear-guests
- You will not be able to assign or edit admin or guest roles manually when this link is in place.

If your workspace already uses SCIM and is now migrating to an Enterprise plan for the first time, follow this migration guide to make sure both Owner and Admin roles get provisioned correctly going forward.

![image](https://webassets.linear.app/images/ornj730p/production/18d51ecafdddceacba1197df01bb1334ef8dfd91-16x16.svg?q=95&auto=format&dpr=2)

You may prefer to invite external Guests to your workspace manually, without adding them through your IDP.

The Invite menu in Settings > Members will allow you to invite Guests only, even with SCIM enabled.

For Guests added before this was an option, you can use the ... menu on the Members page to unlink their account from your identity provider and manage them in Linear.

## SCIM Sync⁠

Linear keeps the following user and team properties in Linear up to date in near real time when we receive SCIM updates from your IDP.

Users

- Email (userName): primary identifier; must be a valid email. SCIM updates are accepted when the email domains are claimed by your workspace.
- Full Name: resolved in order: name.formatted → name.givenName + name.familyName → displayName
- Username/Nickname: updated from displayName. Linear ensures uniqueness by appending a number when needed.
- Active:  active: false suspends the user; active: true unsuspends.
- Avatar: updated from avatarUrl or photos[].value

Teams

- Name (displayName): updates the team name; uniqueness enforced with a suffix if needed (e.g., “Engineering (2)”).
- Members (members): add/replace/remove members to SCIM-managed teams via user references (value = user ID).

## Disabling SCIM⁠

Once SCIM is disabled on Linear side:

- SCIM requests coming from your Identity provider will be rejected on Linear side.
- Any team that was linked to a Group will be unlinked.
- All SCIM restrictions will stop being enforced.

This does mean that if SCIM is re-enabled on Linear side, any changes or member removals that happened on your Identity provider will have to be pushed again to Linear. Refer to your Identity provider documentation for more information on accomplishing this.

If you need to remove some Linear accounts that are not part of your IDP, we recommend enabling the temporary override from your Linear SCIM settings, rather than disabling SCIM. You'll find the option for this at the bottom of your SCIM settings page.

![SCIM Manual overrides button with "Enable override" option](https://webassets.linear.app/images/ornj730p/production/e48d8a73d4a1ede5965682104bc1f5581966a1b4-2058x562.png?w=1440&q=95&auto=format&dpr=2)

## FAQ⁠

[](https://linear.app/docs/scim#collapsible-91f51cef6dc7)Yes, we support setting default public teams for SCIM provisioned users.

[](https://linear.app/docs/scim#collapsible-6ec73b6c82bb)SCIM should work with most identity providers though we have only tested with Okta and OneLogin.

[](https://linear.app/docs/scim#collapsible-cc15bbb03bbd)We support SCIM 2.0 (not SCIM 1.1.)

[](https://linear.app/docs/scim#collapsible-c0b2f96ac56e)As of August 14th 2025, SCIM-created users are billable only after they've logged on for the first time, not at time of creation.



[PreviousSAML](https://linear.app/docs/saml-and-access-control)[NextAPI and Webhooks](https://linear.app/docs/api-and-webhooks)# API and Webhooks

Source: https://linear.app/docs/api-and-webhooks

---

# API and Webhooks

Linear's GraphQL API and webhooks lets you extend Linear's functionality beyond what we provide out of the box.

![Linear logo and a logo representing the API](https://webassets.linear.app/images/ornj730p/production/c944abb65e6b46b14d2666d88f8d390699ffd265-2880x1620.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Linear's public API is built using GraphQL. It's the same API we use internally for developing our applications.

Linear's webhooks allow you to receive HTTP(S) push notifications whenever data is created or updated. This allows you to build integrations on top of Linear.

## Basics⁠

### API⁠

You own your data in Linear and our GraphQL API lets you query that data. In addition to querying, Linear has full support for mutating all entities. Any mutations you make via the API are observed in real-time by all clients.

Go to the API section under Account > Security & Access settings and read the linked API documentation for more information. Our GraphQL schema is available here.

![image](https://webassets.linear.app/images/ornj730p/production/ea822173f6bf2d9383d19105d9ecaa6693492aca-16x16.svg?q=95&auto=format&dpr=2)

For more in depth documentation visit developers.linear.app. If you have a question the docs don't answer, post it in the #api channel in our Slack community.

### API Keys⁠

Admins can choose whether or not Members can create their own API keys from Settings > Administration > API > Member API keys. This setting will not apply to Admins who can always create API keys.

![Member API Key permission toggle](https://webassets.linear.app/images/ornj730p/production/91976e7722c04bf16f048765228587c090b0bd96-974x303.png?w=1440&q=95&auto=format&dpr=2)

Existing API keys for your workspace can be viewed from the same menu and revoked if needed.

Admins and permitted Members can create personal API keys from Settings > Account > Security & Access. For each key you create, you can choose to give it full access to the data your user can access, or restrict it to certain permissions (Read, Write, Admin, Create issues, Create comments). You can also limit an API key's access to specific teams in your workspace.

### Webhooks⁠

Our webhooks support data change events for Issues, Comments, Issue attachments, Documents, Emoji reactions, Projects, Project updates, Cycles, Labels, Users and Issue SLAs.

Consider using webhooks to trigger CI builds, perform calculations on issue data or send messages on specific conditions. Creating and managing webhooks requires admin permissions. Read more in our webhook documentation.

The configured URL will be called whenever any issue or comment in that team is created or updated. You'll receive the entire data object as the payload. We'll also let you know what the previous values for all changed properties were.

### Create a webhook⁠

Create and manage webhooks and OAuth applications in Settings > Administration > API. Admin permissions in your workspace are necessary to view this page.

### Third-party apps⁠

Third-party integrations created for Linear can be found on our integrations directory.

[PreviousSCIM](https://linear.app/docs/scim)[NextThird-Party App Approvals](https://linear.app/docs/third-party-application-approvals)# Billing and plans

Source: https://linear.app/docs/billing-and-plans

---

# Billing and plans

We offer a free plan and different paid plans to suit your needs.

Please see Pricing for rates and a feature-by-feature comparison by plan.

![Billing icon](https://webassets.linear.app/images/ornj730p/production/23421ff71eab7797eae4d5921cbc8b3df72b191a-2160x1327.png?w=1440&q=95&auto=format&dpr=2)

## How our plans and billing works⁠

### Plans⁠

Refer to our pricing page for the most up-to-date information on our plans offering.

### Billing⁠

Customers are billed for the number of unsuspended users within a workspace. Thus, your paid plan only applies to the single workspace associated with it.

For billing frequency, we offer either monthly or yearly options. On our Enterprise plan, we exclusively offer a yearly option.

Your account is charged on a monthly basis for the number of unsuspended users in any role on your workspace.

Adding users mid-month will not result in a charge until the following month. Similarly, removing a user mid-month will not result in a credit for the remainder of the month.

When you upgrade to a yearly plan, Linear charges for the total number of unsuspended users in your workspace at that time. This establishes your subscription year and billing cycle.



If you add or suspend users during that year, your account automatically adjusts to reflect those changes:

- Adding users → generates a pro-rated charge for the remaining time in your subscription year.
- Suspending users → generates a pro-rated credit for the remaining time in your subscription year.



All adjustments are fully automated — there’s no need to request manual changes. Credits are automatically applied toward future invoices or renewals (they aren’t refunded).



Linear reconciles these adjustments on your monthly billing cycle, which is tied to your annual plan’s start date (not the calendar month).



- If additional users were added during the past monthly billing cycle, a true-up invoice is created and charged automatically or sent by email.
- If users were suspended, a credit is automatically issued and applied to future invoices.

#### Example⁠



Your annual plan starts on February 10 and renews the following year.



Each change — adding or suspending users — is billed or credited based on the exact date it happens. Invoices only ever reflect past activity, and we don’t edit or cancel them once issued.



This ensures your account stays accurate and that all future prorations calculate correctly. Any new user changes are automatically included in your next billing cycle — no manual action or adjustments needed.



#### Key things to know⁠

- “Billing month” refers to your plan’s recurring monthly cycle, not the calendar month.
- Annual subscriptions are charged once for the base year, with automated monthly true-ups for user changes.
- Invoices are final once issued. Future user changes are automatically included in upcoming invoices.
- Credits are automatically applied to future charges or renewals.



## Manage your billing⁠

Navigate to Settings > Workspace > Billing to access your plan information and make changes. From here, you can:

- View and change your plan.
- Update your payment information.
- Update the billing email.
- View billing history — past invoices and charges.
- We will also show if a charge is failed or past due.

### Change or Cancel a subscription⁠

Workspace admins can change or cancel a subscription from Settings > Workspace > Plans. Subscription updates take effect at the end of the subscription period. If you are on a monthly plan, this will be at the end of the billing month. If you are on a yearly plan, this will be at the end of the billing year.

We do not provide refunds for cancellations mid-subscription. If you are uncertain you are ready to commit to a full year, we recommend starting on a monthly plan first. You can switch to yearly at a later date when you are ready to commit longer term and take advantage of the discounted rates.

When cancelling a subscription:

- Nothing will be deleted.
- If you have over 250 issues, you will no longer be able to create new issues.
- Members will become Admins of the workspace, as all users are Admins on free plans.

### Add a VAT number⁠

To add a VAT number, choose the I'm purchasing as a business option on the checkout page when upgrading.

To add a VAT number for an existing subscription, go to Settings > Billing > Billing Details > Edit.

## Sales tax⁠

In certain areas Linear is required to apply sales tax. The billing address you provide is used to determine whether tax must be applied, and if so the applicable rate.

Areas in which Linear must apply sales tax as of October 1st, 2025 include the following. We anticipate this list will grow over time, and we will keep it updated with new additions.

- Arizona
- Chicago, Illinois (PPLT Tax)
- Colorado
- Connecticut
- District of Columbia
- Maryland
- Massachusetts
- New York
- Ohio
- Pennsylvania
- Tennessee
- Texas
- Utah
- Washington

If needed, you can revise your billing address in Settings > Workspace > Billing.

## Special pricing programs⁠

### Education program⁠

We review eligible applicants for a discounted education rate on our Basic and Business paid plans.

Please reach out to support@linear.app from your .edu email, proof of employer/student ID or letter showing your status where possible to expedite your application.

This discount is only available for college or higher-level educational institutions. High schools and for-profit, online-only educational institutions are not eligible.

### Non-profit program⁠

We offer 75% off our Basic and Business paid plans to eligible charities (otherwise known as NonProfits). Please reach out to us at support@linear.app to apply and provide proof of nonprofit status.

The organizations that are not eligible for this discount are the following:

- A legislative or political organization
- A church, association of churches or other religious organization
- A school, college or related organization
- A government office
- An organization that attempts to influence public opinion
- A hospital, an organisation involved with health insurance or group health plans or a related organisation
- A private grant-making, independent or operating foundation

Please note: Eligibility is determined at our sole discretion. We reserve the right to approve or deny access to this discount program at any time, for any reason, and to update our eligibility guidelines as needed.

### Linear for Startups program⁠

The Linear for Startups program is designed to help early-stage startups discover a better, faster way to build and ship great products. Startups affiliated with a partner in Linear’s Startup Program receive up to 6 months of free access to Linear’s Basic or Business plans. For more information, visit https://linear.app/startups.

[PreviousThird-Party App Approvals](https://linear.app/docs/third-party-application-approvals)[NextAudit log](https://linear.app/docs/audit-log)# Audit log

Source: https://linear.app/docs/audit-log

---

# Audit log

Audit logs show you a record of workspace events over the last 90 days.

Available to workspaces on our Enterprise plan

![Audit log page in Linear](https://webassets.linear.app/images/ornj730p/production/9d0afc74a9a0ed53d8370f87cb109ea4eb297125-2160x1327.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Linear automatically tracks events related to account access, subscriptions, and settings changes including the IP and country of the actor. All audit logs are retained for 90 days. You can browse recent events and filter them by event type. For more complex queries, we recommend you access the audit log through the API.

## Configure⁠

Only workspace administrators can access audit logs given the sensitive nature of the information. You can find them under Workspace Settings > Administration > Audit Log

## Access via API⁠

To perform complex queries based on type, actor, and other metadata, we recommend that you access the audit log through Linear's GraphQL API. Visit our API documentation to read more about making GraphQL API requests.

```
# Simple query to get last 250 events
query {
  auditEntries(first: 250) {
    nodes {
      id
      type
      createdAt
      actor {
        id
        name
      }
      metadata
    }
  }
}
```

You can utilize the advanced filtering capabilities of our API to narrow down your query.

```
# Get login events for an user
query {
	auditEntries(filter: {type: {eq: "login"}, actor: {email: {eq: "user@company.app"}}}) {
	  nodes {
	    id
	    type
	    createdAt
	    actor {
	      email
	    }
			ip
	    metadata
	  }
	  pageInfo {
	    endCursor
	    hasNextPage
	  }
	}
}
```

You can also get the list of all the available log entry types from our API.

```
query {
  auditEntryTypes {
    type
    description
  }
}
```

### Webhook and SIEM support⁠

Audit logs can be streamed to a webhook and configured for SIEM data ingestion. To enable the audit log webhook, visit the Audit Log under workspace settings and enable Stream logs. To learn more about securing your webhook using a signing secret, visit our API documentation.

#### Sample responses⁠

User joins a team:

```
{
  "action": "create",
  "actor":
    {
      "id": "8e03f2cf-e644-4d68-a7cc-f834ad2f43b4",
      "name": "Miha Rebernik",
      "email": "miha@linear.app",
      "avatarUrl": "https://public.linear.dev/8e03f2cf-e644-4d68-a7cc-f834ad2f43b4/d3c0a4bf-51a7-41cc-ade7-0f61f9d4f886",
      "type": "user",
    },
  "createdAt": "2025-03-28T19:46:01.382Z",
  "data":
    {
      "id": "4b0186dc-a464-4330-9d4b-f4fc8f01db5b",
      "createdAt": "2025-03-28T19:46:01.382Z",
      "type": "userJoinedTeam",
      "organizationId": "5a3b982d-8f04-4971-956c-fbcb2c68642a",
      "actorId": "8e03f2cf-e644-4d68-a7cc-f834ad2f43b4",
      "metadata":
        {
          "teamName": "New team",
          "teamKey": "NEW",
          "teamId": "7586c601-2c9f-4764-bbc5-6132791c68c9",
          "owner": false,
        },
      "requestInformation": {},
    },
  "type": "AuditEntry",
  "organizationId": "5a3b982d-8f04-4971-956c-fbcb2c68642a",
  "webhookTimestamp": 1743191166416,
  "webhookId": "f1d0caa0-a974-4604-a300-a4edbba66803",
}
```

A webhook is created:

```
{
  "action": "create",
  "actor": {
    "id": "8e03f2cf-e644-4d68-a7cc-f834ad2f43b4",
    "name": "Miha Rebernik",
    "email": "miha@linear.app",
    "avatarUrl": "https://public.linear.dev/8e03f2cf-e644-4d68-a7cc-f834ad2f43b4/d3c0a4bf-51a7-41cc-ade7-0f61f9d4f886",
    "type": "user"
  },
  "createdAt": "2025-03-28T19:46:18.441Z",
  "data": {
    "id": "e78bfecd-53a6-4197-8a71-f614b187553a",
    "createdAt": "2025-03-28T19:46:18.441Z",
    "type": "webhookCreated",
    "organizationId": "5a3b982d-8f04-4971-956c-fbcb2c68642a",
    "actorId": "8e03f2cf-e644-4d68-a7cc-f834ad2f43b4",
    "ip": "::ffff:127.0.0.1",
    "metadata": {
      "id": "53188995-5f3b-44a9-993b-9bb0d37136a5",
      "url": "https://webhook.site/399c1880-02e6-4a2b-8b62-6f2ea5c8cc7e/123",
      "label": "A new webhook",
      "enabled": true,
      "resourceTypes": ["Issue"],
      "allPublicTeams": true
    },
    "requestInformation": {
      "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
      "authMethod": "jwt",
      "authService": "google"
    }
  },
  "type": "AuditEntry",
  "organizationId": "5a3b982d-8f04-4971-956c-fbcb2c68642a",
  "webhookTimestamp": 1743191178476,
  "webhookId": "f1d0caa0-a974-4604-a300-a4edbba66803"
}
```



[PreviousBilling and plans](https://linear.app/docs/billing-and-plans)[NextImporter](https://linear.app/docs/import-issues)# Importer

Source: https://linear.app/docs/import-issues

---

# Importer

Learn best practices for importing to Linear. Select the tool you're importing from in the table of contents for specific instructions.

![Image of migration assistants](https://webassets.linear.app/images/ornj730p/production/d2f61b4eeb982988a066a5416eaa81bb547178b3-2880x1769.png?w=1440&q=95&auto=format&dpr=2)

## Linear Concepts⁠

A Linear workspace is our top level concept, which contains one or many teams. We recommend that each company using Linear uses only one workspace.

Issues and projects are the core entities used to manage work in Linear. Each issue belongs to a single team, while projects can belong to one or many teams. Other concepts in Linear can be scoped to a team or a workspace like Views (filter based groups of issues or projects), Initiatives (hand-picked groups of projects) and more.

When you import from another service to Linear, we'll attempt to match data from the source tool with the closest concept in Linear. If a concept from the source tool does not translate well to Linear, it may not be imported; please see details on your individual service for further details.

## Pre-import best practices⁠

Consider the below before starting your first import for a smoother experience.

### Which data is worth importing?⁠

If there is data that is no longer relevant to your organization's day to day work, consider whether it needs to be in Linear at all (perhaps a CSV of exported data from long-resolved issues is sufficient). Some organizations choose to use Linear as a "clean break" from their legacy tool and import only where absolutely necessary so they can start fresh with minimal clutter. Others prefer to maintain as full a historical record as possible in one place.

If you're importing when evaluating Linear instead of transitioning all at once, you may wish to run a pilot by importing just a few teams. We also have a resource for switching tools in our switch instruction manual.

### Choose an import method⁠

We offer two main methods of importing to Linear; our dedicated import assistants in-product and a CLI import tool. We recommend using the former whenever possible as they retain much more data from the original source, are easier to use, and provide the option to delete an import in bulk if desired.

Use the CLI importer when importing from a service that we don't have a dedicated import assistant for. Import assistants are available for Jira, GitHub Issues, Asana, Shortcut and Linear. More information about the CLI importer can be found here.

### Understand the import process⁠

You'll first need to have an Admin role in Linear in order to access our import tools. You may also need high permissions in the tool you're importing from in order to access the data. In general, the import assistants follow this path:

## How to import⁠

Find instructions on importing from your source tool below:

### Jira⁠

Find instructions here

### GitHub Issues⁠

Find instructions here

### Asana⁠

- Navigate to Settings > Administration > Import/Export. You must be an admin in Linear to access this page.
- Click on the button for Asana.
- Enter your Asana personal access token. You can obtain your personal access token by navigating to your Asana developer console.
- Enter your Asana team name.
- Select which Linear team to import issues into.
- Click Next to start importing.

An issue cannot belong to multiple projects in Linear, so one project will be chosen if issues are assigned to multiple Asana projects.

![image](https://webassets.linear.app/images/ornj730p/production/26a20abf3ac08770181e1bf23c25c65ff03d777d-16x16.svg?q=95&auto=format&dpr=2)

We currently only support in app importing from Asana organizations. Make sure your Asana workspace is an organization before beginning an import, or convert your Asana workspace to an organization if it is not. If you do not want to convert your Asana workspace to an organization, use the CLI importer.

We'll map fields in Asana to these fields in Linear:

### Shortcut⁠

- Navigate to Settings > Administration > Import/Export. You must be an admin in Linear to access this page.
- Click on the button for Shortcut.
- Enter your Shortcut personal access token.
- Enter your Shortcut team name.
- Select which Linear team to import issues into.
- Click Next to start importing.

We'll map fields in Shortcut Issues to these fields in Linear:

### Trello, Pivotal Tracker, GitLab Issues⁠

To import issues from these services, use our open source CLI importer.

For Trello, please note that imports must be run from individual board exports, not from the overall workspace.

While CLI imports can also be used to customize imports for services with an import assistant, we don't recommend this as the CLI importer will not import data supported by the import assistant like comments or projects.

Our Command Line interface (CLI) tool uses CSV exports from the source tool and requires some technical expertise. Access it at the link or from Settings > Workspace > Import/Export. For those unfamiliar with the command line, this video may help with getting started with a CLI import.

### Linear⁠

To import data from one Linear workspace to another, first ensure that you have an admin account in both workspaces using the same email login credential.

If there isn't already an admin using the same email credential in both source and destination workspaces, invite an admin from the destination workspace to the source workspace (or vice versa) and have them run the import. For best results, avoid creating multiple accounts on the same workspace under different emails.

- Navigate to Settings > Administration > Import/Export. You must be an admin in Linear to access this page.
- Click on the "Linear to Linear import" button.
- Select the workspace you would like to import. We will only show workspaces under the same email address where you are an admin member.
- Select the teams you would like to import from this workspace.
- Choose how to map members from the workspace you are importing from to your current workspace.
- Review a summary of the import.
- Click "Start import".

This import will not carry over all data associated with your source workspace. Please note that the data below will not transfer.

- Custom views / view preferences / views attached to projects or initiatives
- Favorites / reminders / drafts / inbox notifications
- Integrations* / webhooks / OAuth clients / API keys (Integrations will need to be installed on the new workspace and will not resume notifications or automations for imported issues in most cases.)
- Billing/plans* (please contact support@linear.app for assistance with billing transfers)
- Workspace URL (you can switch this manually after import)
- Personal and Workspace settings
- Roles (current admins will be imported as members, you will initially be the only admin. Guests will carry over with the same permissions.

### Other⁠

If you'd like to import from a tool not listed here, you can still do so using our CLI importer and the CSV file of your exported data.

First, you'll want to generate a Linear export file from Settings > Administration > Import/Export > Export CSV. Remove any exported text but leave the headers of each column. This will give a CSV in the format that the CLI importer expects for a Linear import.

In the fields below, paste data from your source tool's export file, and save the CSV.

- Title - Issue title
- Description - Issue description
- Priority - Issue priority
- Status - Issue state (workflow)
- Assignee - Issue assignee (user's full name)
- Created - Issue created date
- Completed - Issue completed timestamp: please note that this will not appear in issue activity log, but will be stored on the issue.
- Labels - Added as a label (separate by commas for multiple labels)
- Estimate - Issue estimate: please note that these values only appear on the issue after enabling estimates on the imported issue's team.

Once the above data is in the attached format, you can import the CSV using the CLI and selecting the "Linear" CSV option when prompted.

For those unfamiliar with the command line, this video may help with getting started with a CLI import.

### Troubleshooting⁠

If something did not import as you expected, please check the section for your specific service to confirm whether we support importing that property. If the property is supported but didn't import as documented, please let us know at support@linear.app.

If you need to delete an import in order to re-import once more, you can do so through Import/Export settings, on the overflow menu on a specific import.  If no overflow menu appears, please contact Linear support for assistance deleting it.

Reimporting from the same external source to the same Linear team without deleting the initial import first will skip any already-imported issues.

[PreviousAudit log](https://linear.app/docs/audit-log)[NextExporting Data](https://linear.app/docs/exporting-data)# Exporting Data

Source: https://linear.app/docs/exporting-data

---

# Exporting Data

Export your workspace data using built-in tools, integrations, or the API

![Export issues as CSV option displayed after clicking on the overflow menu on a custom view](https://webassets.linear.app/images/ornj730p/production/8467997bef5508113d3245730f68905602daebc2-1186x687.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Export data from your workspace to build custom reports, keep records, or input into LLMs.

### Workspace CSV exports⁠

Admins can export a workspace's issue data in CSV format from Settings > Administration > Import Export and click Export data at the bottom. There is a toggle option to include private teams, if any. This export action is recorded in the audit log.

This export contains the following fields for each issue: ID, Team, Title, Description, Status, Estimate, Priority, Project ID, Project, Creator, Assignee, Labels, Cycle Number, Cycle Name, Cycle Start, Cycle End, Created, Updated, Started, Triaged, Completed, Canceled, Archived, Due Date, Parent issue, Initiatives, Project Milestone ID, Project Milestone, SLA Status

## Member list CSV exports⁠

Admins can export the list of members in CSV format from your Settings > Administration > Members and click Export CSV button.

## Issue view CSV exports⁠

Export a CSV of issues from any issue view, project or issue list using the Ctrl/CMD + K menu. In projects and custom views, this action is also accessible through the dropdown menu pictured.

Members can export up to 250 issues at a time while Admins can export views with up to 2,000 issues.

Guest users cannot export issues from a Linear workspace.



![Export issues as CSV on the command menu](https://webassets.linear.app/images/ornj730p/production/8464b391e1fac11411e5269b47710611af695c60-1476x786.png?w=1440&q=95&auto=format&dpr=2)



- When in projects or custom views, click the the project/view name and choose "Export issues as CSV…" from the dropdown

![Export issues as a CSV option selected on overflow menu of a project](https://webassets.linear.app/images/ornj730p/production/24537d04edd782a6d2ccc69516ee9c1dc522a815-1106x1586.png?w=1440&q=95&auto=format&dpr=2)

This export contains the following fields for each issue: ID, Team, Title, Description, Status, Estimate, Priority, Project ID, Project, Creator, Assignee, Labels, Cycle Number, Cycle Name, Cycle Start, Cycle End, Created, Updated, Started, Triaged, Completed, Canceled, Archived, Due Date, Parent issue, Initiatives, Project Milestone ID, Project Milestone, SLA Status

## Copy issues as markdown for LLMs⁠

Copy issues and documents as Markdown with Cmd Opt C, or from the command menu. When copying an issue, this command captures its full context — including title, description, comments, and customer requests — in a structured format for use in AI chat tools.

Copy multiple issues at once by selecting them on a list or a board and using the same command.

## Export individual issues as PDFs⁠

If you need to save individual issues as PDFs, use the Print dialog (Cmd/Ctrl + P) while looking at an individual issue to save an file in that format. On doing this, we'll automatically change the timestamps on each issue event from relative to absolute, which can be helpful if your auditors require seeing precise timestamps for each event on an issue.

## Project and Initiative list CSV exports⁠

Export a project or an initiative view as a CSV. This export type is available to members and admins. Please note if you attempt to export from the issues page of a project you will be exporting issues, not the project itself.

To export only one project or initiative, select just that single project before opening the Cmd + K menu.

![Export projects as CSV through the command menu](https://webassets.linear.app/images/ornj730p/production/2fb7d05534506c42b04b097f7ccd2923fbf9dcfa-1158x556.png?w=1440&q=95&auto=format&dpr=2)





![dropdown menu on a project view showing export projects as csv](https://webassets.linear.app/images/ornj730p/production/bace1f1cbbfd97b043e57d17ccf95074468e3ed9-884x562.png?w=1440&q=95&auto=format&dpr=2)



For projects, CSV exports contain: Name, Summary, Status, Milestones, Creator, Lead, Members, Created At, Started At, Target Date, Completed At, Canceled At, Teams, Initiatives

For initiatives, CSV exports contain: Name, Description, Details, Status, Creator, Owner, Target Date, Created At, Started At, Completed At, Projects, Teams, Health, Latest Update, Latest Update Date

## Integrations⁠

Our Airbyte and Google sheets integrations offer ways to export and sync your workspace data to those platforms so you can build your own custom reports. If you're interested in exporting data for analysis, consider using Insights as well for in-product reporting.

## API⁠

You can also export data from issues, projects and more using our API, or work with Linear data using webhooks.

## FAQ⁠

[](https://linear.app/docs/exporting-data#collapsible-df6b9bb698cf)Teams can be imported from one Linear workspace to another. Please find steps to accomplish this here.

[PreviousImporter](https://linear.app/docs/import-issues)[NextTeams](https://linear.app/docs/teams)