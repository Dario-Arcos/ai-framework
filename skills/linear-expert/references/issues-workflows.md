# Table of Contents

- Assign and delegate issues
- Comments and reactions
- Create issues
- Delete and archive issues
- Due dates
- Edit issues
- Estimates
- Issue relations
- Issue status
- Issue templates
- Labels
- Parent and sub-issues
- Priority
- SLAs
- Select issues
- Triage

---

# Issue status

Source: https://linear.app/docs/configuring-workflows

---

# Issue status

Set statuses that your issues will move through on each team.

![Image showing the workflow settings in a Linear workspace and the workspace statuses.](https://webassets.linear.app/images/ornj730p/production/c52f79b144c3ed5ed124e85d02e619b3429b1395-1922x1350.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Issues statuses define the type and order of states that issues can move through from start to completion. These workflows are team-specific and come with a default set and order: Backlog > Todo > In Progress > Done > Canceled.

## Configure⁠

Add or edit statuses in a team from Settings -> Teams -> Issue statuses & automations. You will see a list of all statuses in that team and their order. Click the three dots next to each status and select Edit to make changes to the name, color, or description. Create statuses by clicking the + button, or remove statuses (as long as at least one status exists in each category).

Statuses can be rearranged within a category but categories cannot be moved around. To change the order of a status, drag it to a new position.

![Image showing 4 existing workflow statuses and a new custom one about to be added.](https://webassets.linear.app/images/ornj730p/production/1430c24b2218f7c515d2d9c067c66458abe5b0a4-1754x672.png?w=1440&q=95&auto=format&dpr=2)

![image](https://webassets.linear.app/images/ornj730p/production/fe28ec4f7bbfbb43fa8aa5431c4cbef8158cc0d3-16x16.svg?q=95&auto=format&dpr=2)

How we work at LinearWe have the following workflow set up for our product team: Backlog: Icebox, BacklogUnstarted: TodoStarted: In Progress, In Review, Ready to MergeCompleted: DoneCanceled: Canceled, Could not reproduce, Won't Fix, Duplicate

### Default status⁠

The default status defines the workflow status that will be applied to newly created issues in your team. This can be overridden by the user when creating an issue, but makes it a lot easier to track and organize new issues that come in. By default, your first Backlog status will be the default status. To change that, hover over a different status in the Backlog or Todo categories and then select Make default.

### Duplicate issue status⁠

When you mark an issue as a duplicate of another, its status will change to Canceled. You can create a custom status in the Canceled category (e.g. Duplicate) and then configure workflow settings so that the custom status is applied instead.

### Triage⁠

Triage is an additional status category that acts as an Inbox for your team. Triage is particularly powerful when combined with other integrations like Asks, Slack, or our support ticketing integrations. Learn more here.

## Auto-close and auto-archive⁠

When enabled, auto-close will close issues that have not been updated in a set period of time.

Auto-archive controls when issues in the team will be archived. When an issue archives, its creator will be notified—this is an opportunity to unarchive if the issue is still relevant. Archived issues are still searchable and restorable in the future.

Archiving is only automatic and is not available as a manual action. More information about archiving is available here.

The auto-archive setting also controls when projects and cycles will archive.

![Auto-close and auto-archive settings](https://webassets.linear.app/images/ornj730p/production/0a606026aaf048903bfb7b86585b5fecf24cb033-1418x968.png?w=1440&q=95&auto=format&dpr=2)

## ⁠

[PreviousSub-teams](https://linear.app/docs/sub-teams)[NextCreate issues](https://linear.app/docs/creating-issues)# Create issues

Source: https://linear.app/docs/creating-issues

---

# Create issues

Creating issues is the most common action taken in Linear.

![issue creation dialogue box](https://webassets.linear.app/images/ornj730p/production/25ae979891503f4780b6e837aaa71b5027c67281-1224x534.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Issues are always linked to a single team. They have an issue ID (team's issue identifier and unique number) and are required to have a title and a status—all other properties and relations are optional.

## Create an issue⁠

- Use the keyboard shortcut C to open up an issue creation modal
- Use V to create an issue in full screen mode.
- Click the Create new issue icon in the upper left of the app.
- To create an issue from a template use Option/Alt C, or hold Option/Alt and click the Create new issue icon.
- Enter https://linear.new into your browser URL bar to create new a issue. It will redirect you to the new issue creation page as long as you are logged into your Linear account.
- Issues can be created using our GraphQL API. Many integrations in our directory allow creating issues from other services using this functionality.
- If you have text highlighted when you go to create an issue, this will pre-fill in the issue title.

Changes made to an issue's properties in the first 3 minutes are considered part of the issue creation process, and won't be added to the activity log as changes to the issue.

## Create an issue via email⁠

Issues can be created by sending an email to a unique intake email address that routes to a team. You can also create an issue via email based off a template.

A link to the original email will be included as an attachment on the Linear issue. Attachments will be synced over, though email attachments are limited to 25 MB.

The sender of the email will not be notified when the issue is updated or resolved.

Refer to the Linear Asks feature for the ability to:

- Customize the email address you want requesters to send to
- Reply to customer emails from Linear
- Customize response emails

#### Create an email address⁠

To create a email address for a Linear team, navigate to Settings > Teams > General > Create by email and enable the toggle.

#### Create an email address for a template⁠

To create an email addresses for a team template:

- Navigate to Settings > Teams > Select Team > Templates
- Click the three dots on the right of the template.
- Select Configure email address.
- Enable the toggle in the pop-up.
- Click Continue.

When a team template is used, the issue's title and description will be overwritten by the email contents, but the properties of the template will be applied to the new issue. Replies sent on the original email to the forwarding address will not create additional issues.

## Create recurring issues⁠

You can create recurring issues to automate your repeated tasks on a cadence of your choosing.

### Create a recurring issue⁠

When creating a new issue, you can choose to make it into recurring in the issue composer using the …  menu and choosing "Make recurring…"

[](https://linear.app/docs/creating-issues#collapsible-2de248468918)![Creating a recurring issue from the issue composer](https://webassets.linear.app/images/ornj730p/production/7d4cb7c61fa50aad11ca1bca4e9844ec6bd98489-1091x944.png?w=1440&q=95&auto=format&dpr=2)

### Convert an existing issue into a recurring issue⁠

To convert any issue into a recurring issue, open the issue and in the …  menu choose Convert into > Recurring issue…You can also use the Cmd/Ctrl + K menu by typing "Convert into recurring issue".You can then choose your first due date, and the cadence at which it repeats.

### Create recurring issues in team settings⁠

Navigate to Team settings > Recurring issues.To create a new recurring issue, click the  icon and set your chosen schedule of recurrence.

### Create recurring issues from templates⁠

If you have an existing issue template you want to turn into a recurring issue you can do so.

First create your issue and apply your chosen template. Once created, choose the options to convert to a recurring issue from the … menu or command menu. This issue will now turn into a recurring issue, and include any properties that were in the template, including sub-issues.

Recurring issues can easily be found from your Team settings > Recurring issues, or filtering your views using the Recurring issues filter.

### Cadence of recurring issues⁠

Once you create a recurring issue, future issues in the cadence are expected to be created once the due date passes (00:01 the following day in your team’s timezone.)

Changes to a template in future will not affect recurring issues that were created from this template. You will need to edit the recurring issue directly or recreate it from your updated template.

## Create a new issue URL⁠

The following links trigger the creation of a new Linear issue in any browser and you can add query parameters after any of them to pre-fill issue fields.

- http://linear.app/team/<team ID>/new
- http://linear.app/new
- http://linear.new

To pre-fill issue fields and/or properties:

- Add a ? at the end of the link.
- Include the field or issue property you want to pre-set.
- Add =.
- Add the parameter you are setting.
- Use & between each field or issue property when creating a string of pre-settings.

### Apply pre-set properties⁠

We support the following query parameters:

title and description:

- Use + to indicate empty space in the keyword, or fully url encode content if more complex as description can be a markdown document.
- For example, https://linear.new?title=My+issue+title&description=This+is+my+issue+description

status

- Can be set by UUID or name of the workflow status
- For example, https://linear.new?status=Todo

priority

- Can be set by Medium, Urgent, Medium or Low
- For example: https://linear.new?priority=urgent

assignee

- Can be set by UUID, display name/name of the user, or assignee=me to assign the creator
- For example, https://linear.new?assignee=john or https://linear.new?assignee=Erin+Baker or https://linear.new?assignee=me.

estimate

- Can be set by their point number e.g. estimate=4
- T-shirt sizes have the following point values: No priority (0), XS (1), S(2), M (3), L (5), XL (8), XXL (13), XXXL (21)
- For example, https://linear.app/team/LIN/new?estimate=2

cycle

- Can be set by UUID, cycle number of a name of a cycle
- For example, https://linear.app/team/MOB?cycle=36 or https://linear.new/team/EU/new?cycle=focus+on+bugs

label

- Use a comma between each label you want to apply
- For example, https://linear.new/team/LIN/new?label=bug or https://linear.new?labels=bug,android,comments

project

- Can be set by UUID or the name of the project
- For example, https://linear.new/team/LIN/new?project=Project+page+improvements

milestone (a project must be defined)

- Can be set by UUID or the name of the project milestone
- Project milestone can be read only if project is also passed in the URL
- For example, https://linear.app/team/LIN/new?project=Project+page+improvements&projectMilestone=Beta

links

- URL encoded comma delimited urls with optional title, in format url|title . These will be attached to the issue as link attachments.
- For example: https://linear.new/team/LIN/new?links=https%3A%2F%2Flinear.app%2Chttp%3A%2F%2Fgoogle.com%7CGoogle

### Create a URL from a template⁠

- Go to Settings > Team > Templates.
- Click the three dots to the right of the template.
- Select Copy URL to create issue from template.

### Copy a URL from an issue⁠

While on an issue's view, or an issue is highlighted or selected, open command bar by typing Cmd/Ctrl + K and select Copy pre-filled create issue URL to clipboard.

## Drafts⁠

When writing an issue and navigating away to another part of the app, Linear will hide the issue modal and keep a temporary draft. The next time you go to create an issue, the editor will re-open with the previous content draft. This type of draft is saved locally and only available on the client used to create it. Logging out, restarting, or resetting Linear will clear this type of draft.

If you use Esc or click on the close button, a pop-up modal will appear giving you the option to save the issue as a draft. This draft type persists across clients and will not clear on logout or reset. To access your saved drafts, open the Drafts page in your sidebar.

Drafts are stored for 6 months before being deleted automatically

## FAQ⁠

[](https://linear.app/docs/creating-issues#collapsible-2d4de9b5f74e)If Safari is stealing your focus when hitting tab during issue creation, enable this Safari advanced preference: Safari > Preferences > Advanced > Enable "Press tab to highlight each item on a webpage".

![Safari accessibility preferences modal showing press tab](https://webassets.linear.app/images/ornj730p/production/d1b238d1514c7004f9e3b3d9f4431d4bb27a8a38-992x622.png?w=1440&q=95&auto=format&dpr=2)

[](https://linear.app/docs/creating-issues#collapsible-df924442dd3b)Email routing does not support sending messages with file sizes greater than 25MB. If you have attachments exceeding that, it will fail to deliver. Message body must also be less than 250,000 characters.



[PreviousIssue status](https://linear.app/docs/configuring-workflows)[NextEdit issues](https://linear.app/docs/editing-issues)# Edit issues

Source: https://linear.app/docs/editing-issues

---

# Edit issues

Making changes to an issue.

![issue creation dialogue box](https://webassets.linear.app/images/ornj730p/production/d8f7b8a4591344aa7946960fc408d1fa05044b4c-1256x402.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

All workspace members will be able to edit an issue's title and description, regardless of who is the original creator of an issue. For comments, only the creator of the comment will be able to perform additional edits.

## Edit issue title and description⁠

You can edit an issue title or description by clicking directly on the title or description and editing inline. You can also use the methods below when editing an issue.

## Revert/Restore issue description⁠

If changes have been made to an issue description and you would like to revert to the original issue description or view changes that have been made, open the command menu with Cmd K and search for Issue content history… or choose the "Show version history" option from the ... menu on an issue. The issue description history will be available in this option 10 minutes after a description has been modified.

## Move an issue to another team⁠

When work needs to be passed over to another team, or when you are consolidating teams, issues can be moved to the appropriate Linear team within the same workspace.

For a single issue, simply use Cmd/Ctrl Shift M to move an issue to a new team. To move issues in bulk while retaining as much data as possible, select issues manually or with filters before moving them. Use Cmd/Ctrl A to select all issues on the list or board.

Cmd/Ctrl Z will undo moving an issue if you moved it by accident, but it will not undo the removal of issue data.

### Old Issue IDs and URLS⁠

When you move an issue to a new team, we generate a new issue ID and unique URL for the issue. Old URLs will still work and redirect to the new issue URL. Searching for old issue IDs will also bring up the current issue (unfortunately, this doesn't work for old issue titles). Inline references to issues (like #ENG-123) will redirect when clicked, but won't update visually from the original issue ID they're associated with.

### Changes in issue properties⁠

[PreviousCreate issues](https://linear.app/docs/creating-issues)[NextAssign and delegate issues](https://linear.app/docs/assigning-issues)# Assign and delegate issues

Source: https://linear.app/docs/assigning-issues

---

# Assign and delegate issues



![Linear issue detail view showing an issue labeled 'In Progress' assigned to a teammate and delegated to an agent, with both assignee and delegated agent avatars shown in the properties sidebar.](https://webassets.linear.app/images/ornj730p/production/849fbda44425eeaac774029ed969ea3aaa395b3d-1561x1217.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Issues in Linear are assigned to a single person at a time, giving teams clear ownership and responsibility. Assignment helps teammates triage, track, and prioritize work.

Delegation is a form of assignment used with agents, allowing them to take action on an issue while the assigned teammate maintains ownership.

### Assigning issues⁠

You can assign issues at any point—while creating them, triaging new work, or reviewing and editing existing issues.

To assign an issue, open the issue and use the assignee field in the properties sidebar to choose a teammate or agent. You can also assign directly from cards in board views and issue list views by clicking the assignee avatar, or press A when viewing or hovering over an issue to open the assignment menu.

To assign yourself quickly, press I while viewing an issue or when hovering in list view.

You can also open the command menu (⌘K) and search for "Assign to..." to make updates via keyboard. For bulk assignment, use multi-select in list or board views by typing X when hovering over the issue, and right-click to update the assignee from the bulk action bar.

To remove an assignee, choose "No assignee" from the assignment menu.

#### Assignment permissions⁠

- Issues in public teams can be assigned to any workspace member
- Private team issues can only be assigned to members of the private team
- Issues cannot be assigned to guests and inactive users

### Delegating to agents⁠

To delegate work, you can assign an issue to an agent. When you delegate an issue to an agent, you remain the primary assignee and the agent is added as an additional contributor working on your behalf.

You can change the agent at any time or remove them by selecting "No agent" from the assignment menu.

To delegate an issue to an agent, make sure the agent has access to the team the issue belongs to. Team membership is set when the agent integration is added to a workspace and can be changed by an admin at any time.

### Managing assigned issues⁠

#### User views⁠

Assigned issues, even those delegated to an agent, appear in your My Issues default view, where you can review all issues you're responsible for across your workspace. This view updates automatically based on assignment changes to track the progress of your assigned and delegated work.

Assigned and delegated issues also appear in any custom views filtered by Assignee or Agent.



![Linear custom view titled 'Delegated issues' showing a filtered list of issues. Each issue displays both the assigned teammate and the delegated agent as separate avatars.](https://webassets.linear.app/images/ornj730p/production/d8227db82d75b51c911aa00d759ad527aecb0d82-2364x728.png?w=1440&q=95&auto=format&dpr=2)

#### History⁠

When viewing issues, the assignment and delegation history is tracked in its Activity feed, which shows changes over time and who made them.

#### Inbox⁠

You are automatically subscribed to issues that are assigned to you. You will be notified of any updates to your assigned issues in your Inbox. You can filter Inbox activity by assignment using the "Notification type" filter to focus on issues that have been assigned to you.

#### Search⁠

You can filter your searches by assignee or by the agent they've been delegated to through Search to locate relevant issues based on ownership or automation.

#### Insights⁠

Insights surface trends in how work is distributed across assigned teammates and agents. You can report on issues by assignee or by the agent they’ve been delegated to, helping teams understand ownership patterns and automation coverage.

Available to workspaces on our Business and Enterprise plans.

### Automation⁠

Linear supports automated issue assignment that helps teams route and manage issues with minimal input.

Optionally enable an automation to automatically assign yourself to issues you create. To set up this automation, refer to Preferences. If you choose not to enable this setting, you can still use the Create more button in an issue draft or press ⌘ + Shift + Enter when submitting an issue to quickly create another with the same assignee.

Linear doesn’t currently support auto-assigning issues to a specific teammate by default, but you can use templates to pre-fill the assignee field.

![Settings in preferences to optionally auto-assign yourself when creating new issues.](https://webassets.linear.app/images/ornj730p/production/4fc5803c93a3b6f9aecb4a7ddef902866ecf29dc-1524x298.png?w=1440&q=95&auto=format&dpr=2)

When a teammate creates a Git branch from an issue, it can automatically assign the issue to them and move it to a started status when you copy the git branch name. This is configurable in Preferences.

![Git-based automations include moving an issue to a started status when copying the Git branch name, and assigning the issue to yourself when moving it to started.](https://webassets.linear.app/images/ornj730p/production/50ce3460e0ae8bbc63f72473fda8908c8844a7aa-1564x762.png?w=1440&q=95&auto=format&dpr=2)

For custom rules to assign issues when they enter Triage, you can configure triage routing. Based on issue properties like team, status, or label, these rules route issues to a specific team and set an assignee. Rules can also delegate issues to an agent as part of the same flow for even greater automation during triage.

Triage routing is available on our Enterprise plan.

![Linear’s triage settings showing automated assignment and delegation setup. 'Triage responsibility' assigns new issues in triage to a specified teammate. Below, a 'Triage rule' is configured to delegate issues to an agent when assigned to that teammate.](https://webassets.linear.app/images/ornj730p/production/03af13eeca75035924fd384d380cf9827b8ceeb3-1532x1304.png?w=1440&q=95&auto=format&dpr=2)







[PreviousEdit issues](https://linear.app/docs/editing-issues)[NextSelect issues](https://linear.app/docs/select-issues)# Select issues

Source: https://linear.app/docs/select-issues

---

# Select issues

Take actions on groups of issues.

![Linear app showing multiple issues selected](https://webassets.linear.app/images/ornj730p/production/88dde87f01f1e2291aef98dc32bd916bea2cc3b9-1784x977.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Highlighting or selecting one issue both allow you to take actions on the issue using keyboard shortcuts, the command menu, or right-click to bring up the contextual menu. The two differentiates when it comes to multiple issues.

By default, no issue is selected when you open a board or list of issues.

## Highlight an issue⁠

- Hover over the issue with your cursor until the issue is highlighted
- Use ↑ / ↓ or J / K to navigate the page to the issue.

## Select issues⁠

- Once an issue is highlighted, press X shortcut.
- Hold Shift and click your mouse on the issue.
- Bring up a checkbox element by moving your cursor over the far left of any issue (near where the issue meets the sidebar).

### Select multiple issues⁠

Once an issue is selected, use the navigation to highlight another issue and press X.

To select multiple consecutive issues:

- Hold down Shift after selecting the first issue, then use the ↑ / ↓ keys to increase the selected range one issue at a time.
- Use filters to refine the issue list first, then use Cmd/Ctrl A to select all issues on a board or list.

### Clear selection⁠

Press Esc will clear selected issues on your list or board.

## Take actions⁠

Once an issue or set of issues are selected, use Cmd/Ctrl K to open the command bar and select the preferred action or right-click anywhere on the selected issue(s) to open the contextual menu for a list of available actions.

### Moving issues to top, bottom, or in increments⁠

To move an issue or issues up or down the list:

- In the Display Options, set the Grouping to No grouping.
- Set the Ordering to Manual.
- Select the issue(s) you want to move.
- Use the shortcut Option/Alt Shift ↑ or Option/Alt Shift ↓ to move an issue/issues in increments.

### Update multiple issues⁠

Select them with shortcuts or the mouse and then update the issue field like you would any issue. Common bulk actions will show up at the bottom.

- Select all keyboard shortcut: To change issue priority so all issues without a priority were assigned no priority, filter to no priority issues and then used Cmd/Ctrl A then P to update the priority.
- Use mouse to select multiple issues: To move some issues from Todo to backlog, select by hovering over them and individually marking the checkbox that popped up.
- Use keyboard to select multiple issues and bulk action toolbar: Holding down Shift while moving the up/down buttons to select multiple issues and choose a bulk action such as  Move to backlog.



[PreviousAssign and delegate issues](https://linear.app/docs/assigning-issues)[NextParent and sub-issues](https://linear.app/docs/parent-and-sub-issues)# Parent and sub-issues

Source: https://linear.app/docs/parent-and-sub-issues

---

# Parent and sub-issues

Use sub-issues to break down larger "parent" issues into smaller pieces of work.

![Linear app showing a parent issue with sub-issues](https://webassets.linear.app/images/ornj730p/production/a2c92123d2c244bb53f75e34970a5cb8417bd2c3-2340x1064.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Consider creating sub-issues when a set of work is too large to be a single issue but too small to be a project. Sub-issues are also ideal for splitting up work shared across teammates. When you add a sub-issue to another issue, the other issue becomes its "parent".

## Create a sub-issue⁠

Create a sub-issue by opening the parent issue and click the + Add sub-issues button below the issue description. This will launch the sub-issue editor. You can also use the shortcut Command Shift O to open the editor. You can also create sub-issues in the issue creation modal (C) by pressing Command Shift O to open the editor or under the ... menu and "Add sub-issue".

When you save a sub-issue, it will automatically launch the editor to create a new one. If you want to create a new one with the same values (labels/assignee etc.) you can press ⌘ Shift Enter or  Shift+ click the save button. Press Esc to exit the sub-issue editor and continue updating the parent issue.You can turn a comment under an issue into a sub-issue by hovering over a comment and clicking the … menu then "new sub-issue from comment". Selecting a comment's text and pressing  ⌘ Shift O will also create a sub-issue.If you have a list (bulleted, numbered or checklist) you can highlight the checklist and hit ⌘ Shift O to convert to sub-issues or choose the "Create sub-issues(s) from selection" item in the formatting toolbar.You can add a template using the templates icon when creating a sub-issue or using the command menu under "Create new sub-issue from template" when viewing the parent.

## Copy properties⁠

Sub-issues created in the editor automatically copy issue properties from the parent issue such as the project and cycle as long as those are set before you create the sub-issue.

Team, labels and assignees are not copied over. You can't create sub-issues while editing the parent issue, but the option will come up once you press save.You can duplicate a parent and its sub-issues from the Parent's ... menu under "Duplicate" and hit the toggle "Include sub-issues".

## Status automation⁠

Optionally, configure the following behaviors at the team level (Settings > Team > Workflow) to automate status relations between parent and sub-issues. Status changes triggered by Git integrations will also respect these automations.

Parent auto-close

When all sub-issues are marked as done, the parent issue will also be marked as done automatically.

Sub-issue auto-close

When the parent issue is marked as done, all remaining sub-issues will also be marked as done.

## Converting issues⁠

### Turn issues into sub-issues⁠

Turn an existing issue(s) into sub-issues of another issue by selecting one or multiple issues and then taking the action to set the parent issue. This action is accessible from the command menu or by pressing Cmd Shift P and selecting a parent issue.

### Turn issues into parent issues⁠

To make an existing issue a parent issue of another issue, hover over a sub-issue and take the action "Set Parent" in the contextual menu, command menu or ... menu.

### Turn sub-issues into issues⁠

You can turn a sub-issue into a regular issue again using the ⌘/ctrlK menu option "Remove parent".

### Turn issues into projects⁠

Sometimes an issue grows so large it's more appropriate to turn it into a project instead. To do so, hover over the parent's ... menu and choose "Convert to project." The project will inherit its details from the original parent issue, and former sub-issues will become standard issues in the project.

## Filter sub-issues⁠

You can usually set the view to show or hide sub-issues in Display Options. You can also use Filters to show only top-level (parent) issues, issues with sub-issues, or only sub-issues. If you use these filters frequently, consider creating a custom view.You can also hide completed sub-issues by default under the ... menu and toggling "Always hide completed sub-issues".You can also sort your sub-issues under an issue from the … menu and "Order by" though this only updates it for the current user, not globally.

## Display options⁠

When looking at sub-issues from the context of their parent issue, you can customize the order of the sub-issues and the properties that display.

![sub-issue display options menu](https://webassets.linear.app/images/ornj730p/production/66557cbd02b0b0d4b3dbbdcbcd1a42d1efbc677a-2856x1410.png?w=1440&q=95&auto=format&dpr=2)

[PreviousSelect issues](https://linear.app/docs/select-issues)[NextIssue templates](https://linear.app/docs/issue-templates)# Issue templates

Source: https://linear.app/docs/issue-templates

---

# Issue templates

Templates speed up issue creation, ensure properties are applied when necessary, and facilitate reporting.

![Form template exposed in the issue composer with fields title, repro steps, component](https://webassets.linear.app/images/ornj730p/production/5e1cb2f12b568848b2fabf98420b2a0639854858-1310x1092.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Templates help you file issues more quickly, and ensure desired issue properties are applied without having to add each one manually. When a template is set as default for a team, each new issue in that team will be created from that template unless manually changed.

## Create standard issue templates⁠

![The settings page for Templates showing a button on how to create a template](https://webassets.linear.app/images/ornj730p/production/7a91829a12a45a33528236cb58a98221b2737795-2414x817.png?w=1440&q=95&auto=format&dpr=2)

Create new templates by navigating to either Workspace settings > Templates or Team settings > Templates. Standard templates allow you set the properties of the issue, and provide some context in the description if desired.

Standard templates have the same formatting options of regular issues, with the addition of placeholder text. If you want to prompt the creator to input information in the issue's description, consider using this formatting in your template.

To format text as a placeholder, select text while editing your template and click the Aa icon on the formatting bar. This formatting type is only available when creating or editing templates.

You can create issues with a workspace template on any team in your workspace. Team specific properties like team labels or issue statuses cannot be preset in a workspace level template.

Use workspace templates for issue types that are likely to appear across different teams.

When a template is scoped to a particular team, it's available only when creating issues in that team. This template type has full access to team properties like team labels and issue statuses.

Team templates are commonly used in our Asks integration, or for types of issues should always be filed to only one team in your Linear workspace.

## Create form templates⁠

Form templates are more structured than standard issue templates and can be used when it's important that certain information is provided at issue creation. They support a set of generic form fields that the submitting user can fill out, as well as fillable fields that correspond to the issue's properties directly. Form templates can be triggered in the Slack integration and in Asks, and also directly in Linear by selecting the template. Any field can be required in a form template.

### Generic form fields⁠

### Property form fields⁠

You can also elect to include customer, a label group, priority, title, and due date. These fields are treated like generic fields as the user fills the form, but they correspond directly to an issue property rather than being a value input into the created issue's description.

### Default properties⁠

Like standard templates, some properties can be applied by default. These appear to the user when the form template is triggered in Linear, but not elsewhere. These fields are team, status, priority, assignee, project, label, and sub-issue.

## Use issue templates⁠

Create an issue from a template with the keyboard shortcut Option/Alt C. Alternatively, access templates directly from the issue creation modal by clicking on Template next to the team name.

If you don't see the template, check that you're creating the issue from the right team. In a sub-issue, only templates that do not themselves contain sub-issues are available.

## Default templates⁠

Default templates are templates that are automatically applied when creating a new issue, given the conditions are met. Configure default templates from a team's template settings page. You can configure defaults differently for members of your team or people who are not part of your team. Form templates are only available as default templates for non-team members.

![Default templates in Linear settings](https://webassets.linear.app/images/ornj730p/production/d6eebc35f66823df066e862e923953b55def74c7-1520x506.png?w=1440&q=95&auto=format&dpr=2)



## Templates in integrations⁠

Templates created in Linear can also be used in integrations to help save time and keep properties applied consistently where needed.

Add a template to a supported integration in that integration's settings page in Linear.

## Template based Insights⁠

Issues created by template are filterable by their template, regardless of where they were created. For example, for a template Bug Report, filtering for that template will return issues created with that template in created in Slack with our Slack or Asks integrations, Intercom/Zendesk, and Linear's interface. Questions like "What's our breakdown of bug reports vs. feature requests look like, and how many of them are solved" can be explored with Insights:

![Insights showing bugs/feature requests/quick wins/mobile feas, broken down by status](https://webassets.linear.app/images/ornj730p/production/590af179a56bf8e74f60838cbb9ff4a42cb759c9-1242x862.png?w=1440&q=95&auto=format&dpr=2)

Or, investigate the breakdown of template use by intake source:

![Insights sliced by source and segmented by template](https://webassets.linear.app/images/ornj730p/production/af3a7409ca32ae87de8a695ea54f2f3cfc687295-1247x925.png?w=1440&q=95&auto=format&dpr=2)

### FAQ⁠

[](https://linear.app/docs/issue-templates#collapsible-483fe2107c9e)All templates that used Asks fields have been migrated to form templates, as this feature replaces the former Asks fields functionality.

You can use this option to run a best effort conversion back from a form template to a standard issue template.

![Convert to standard template option in template overflow menu](https://webassets.linear.app/images/ornj730p/production/4dcf403e825728cfee0cedf0065fff6bee013bb9-1478x284.png?w=1440&q=95&auto=format&dpr=2)







[PreviousParent and sub-issues](https://linear.app/docs/parent-and-sub-issues)[NextIssue documents](https://linear.app/docs/issue-documents)# Comments and reactions

Source: https://linear.app/docs/comment-on-issues

---

# Comments and reactions

Leave comments or reactions on issues.

![comments and reactions on a Linear issue](https://webassets.linear.app/images/ornj730p/production/ec0d3a41ec497dbb27653e26110d8a3cac29b964-1203x796.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Comments and reactions allow for team collaboration within an issue.

All users with access to an issue can post comments and threaded replies. React with emoji on the issue description itself, or on individual comments or threads.

## Post a comment⁠

Comment on an issue by clicking into the "Leave a comment…" text box at the bottom of an issue. While issue description text is saved automatically, you will need to click the Comment button or ⌘/Ctrl  Enter to post the comment to the issue. Unsent comments are visible on the issue, and in Drafts in your sidebar.Attach files to a comment using the paperclip icon, ⌘/Ctrl Shift A, or drag and drop.

## Edit or manage a comment⁠

To edit an existing comment you wrote on an issue, click on the ... icon to the top right of the comment and select edit. Click save to save any changes you make.

Other options in this menu allow you to manage your subscription to that thread, copy a URL to the comment, create a new issue or sub-issue from the comment, or delete the comment.

## Threads⁠

![Thread comment on Linear issue](https://webassets.linear.app/images/ornj730p/production/b22cee655d066d6090a4e6bf6c1617516fc607eb-1104x326.png?w=1440&q=95&auto=format&dpr=2)

Threads allow you to continue on a topic mentioned in a comment. To create a threaded comment:

- Hover over the comment you'd like to respond to
- Click on the arrow icon for Reply to comment in the top right.

If a thread already exists, click into the text box at the bottom of this comment thread and start crafting your response. Send threads as you would a regular comment.

### Resolve threads⁠

Resolving threads clarifies when a question has been answered or a decision is made. This is particularly useful in longer threads to clearly identify the resolution.

Mark a thread as resolved through the overflow menu on the root message. To showcase a specific resolution, resolve a thread from a particular reply to expose that reply specifically.

With the setting Enable resolved thread AI summaries enabled, AI will generate summaries for resolved comment threads.

## Summaries⁠

Get up to speed on long discussions with AI-generated summaries.

Available to workspaces on our Business and Enterprise plans.

![Linear issue view with AI-generated discussion summary in the activity section.](https://webassets.linear.app/images/ornj730p/production/dac0580ba514fc3b2c6561c0094480a416178304-1682x1465.png?w=1440&q=95&auto=format&dpr=2)

### Issue discussion summaries⁠

Discussion summaries provide a condensed record of decisions, blockers, debates and their resolutions, and the people involved in those discussions. They update automatically as comments are added or removed, ensuring the content reflects the current state of the conversation.

![Issue activity view showing an AI-generated discussion summary and citations linking to source comments](https://webassets.linear.app/images/ornj730p/production/b889ddac395211b5304f7c31a2405f66c72419f6-1708x550.png?w=1440&q=95&auto=format&dpr=2)

These summaries are generated automatically when an issue contains at least 19 comments or 100 words of discussion. Each bullet point includes a citation linking back to its source comment, so you can see the exact quote and context.

As discussions evolve, summaries regenerate incrementally. The summary appears above the issue’s comments, giving a structured view without needing to read through the entire thread.

### Resolved comment thread summaries⁠

When a thread is resolved without a closing comment, Linear will generate a short summary of the discussion that appears on the resolved thread.

These summaries are visible only when the thread is collapsed, providing just enough context to understand what happened without reading the full thread. Enable this feature in a team's settings under General.

If the content of the thread changes, the summary will be updated automatically. If you resolve the thread with a reply comment, no summary is created. In this case, the resolving comment is treated as the final word in the conversation.

## Emoji react to issues and comments⁠

You can leave an emoji reaction on an issue or a comment by clicking the "Add reaction" icon visible at the bottom of any issue or when hovering a comment.

All official Unicode emojis are available by default. Custom emojis can be uploaded individually (JPG, GIF, and PNG formats are supported) or imported in bulk from your Slack workspace via the Emoji settings page.

[PreviousIssue documents](https://linear.app/docs/issue-documents)[NextEditor](https://linear.app/docs/editor)# Delete and archive issues

Source: https://linear.app/docs/delete-archive-issues

---

# Delete and archive issues

Linear archives issues automatically to keep your workspace uncluttered and easy to search.

![Linear settings showing the auto-archive preferences](https://webassets.linear.app/images/ornj730p/production/82132ce2f13a09b1638db646a8dc460416fe89c8-2160x1327.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Linear offers features that helps to manage backlog and stale items in your workspace to streamline your focus on what's current. We introduce our auto-close and auto-archive feature, and talk about deleted issues and the team archives.

## Delete issues⁠

Delete issues with the shortcut Cmd/Ctrl delete, from an issue's contextual menu, or use command bar Cmd K and select Delete issue.

If you accidentally delete an issue, the fastest way to restore it is to use Cmd/Ctrl Z. If that isn't an option (e.g. it wasn't the last action you took), go to your team's archives > Recently deleted issues and use the # shortcut to restore it. Recently deleted issues are stored in the archives for 30 days, after which they'll be permanently removed from your workspace. It is not possible to restore deleted issues after they have been permanently removed.

## Auto-close⁠

![Auto-close automations settings](https://webassets.linear.app/images/ornj730p/production/e3ab2a2dcae1e075aa611591cc07d4281723f239-1342x810.png?w=1440&q=95&auto=format&dpr=2)

Linear offers an option to close issues that have not been updated after a certain time period. This can be configured in Team settings > Workflows. When auto-closed, an issue is marked with one of the Closed statuses, we publish a history item to its Activity feed, and notify subscribers. You can re-open an auto-closed issue anytime by changing its status.Issues will not be auto-closed until the associated cycle and project are completed.

## Auto-archive⁠

Archiving happens automatically with no option to manually archive items.

![Auto-archive closed issues, cycles, and projects](https://webassets.linear.app/images/ornj730p/production/d65e6891b0933632dd09f3ddf3de9ede8f640b3a-1452x466.png?w=1440&q=95&auto=format&dpr=2)

You can adjust the auto-archive time period, after which closed issues are auto-archived in Team Settings > Issue statuses & automations. Changes made will apply within 24 hours, so if you have issues that have been completed for 2 months and change to a 1 month auto-archive schedule, you can expect to see those archive within the next day.

### Issues are not archiving⁠

- The parent issue is not closed
- Sub-issues are not all closed
- Sub-issues in another project is not closed
- The issue's project is not yet available to archive.

If a completed issue is blocked from auto-archiving by a project or another issue, it will still need to wait the necessary auto-archive time. For example, with a 1 month auto-archive period in place, an issue that's been done for 3 months in an active project will archive 1 month after the project has been completed.

### Projects are not archiving⁠

Scenarios that prevent a project from archiving:

- The project status is not closed (completed or cancelled category)
- Updates/changes have been made (e.g. renaming a project)
- All issues are not yet available to archive. A project's issues has to be available to archive in order for the project to archive. This helps to prevent missing data when looking at a project's graph or other calculations.

## The archives⁠

![Archives](https://webassets.linear.app/images/ornj730p/production/cd479f2a2c0fdb25c803ee5fa99738c254c13ca4-914x362.png?w=1440&q=95&auto=format&dpr=2)

Each team has its own archives page where you will find archived or deleted issues, initiatives, cycles, projects, and documents. Access it with the shortcut G then X or find it in the sidebar under the three dot menu beside each team name. To keep the app speedy, archived issues are loaded on demand rather than stored in the client, so you may find the issues load a little slower on this page than elsewhere in the app.

### Restore issues⁠

Restore issues, projects, or initiatives from the archive in order to edit them.

[PreviousEditor](https://linear.app/docs/editor)[NextCustomer Requests](https://linear.app/docs/customer-requests)# Due dates

Source: https://linear.app/docs/due-dates

---

# Due dates

Add due dates to issues to help your team keep track of time-sensitive work.

![Due date tooltip in Linear](https://webassets.linear.app/images/ornj730p/production/4219f69f2ea58b6e90454da2ec87b7483aa8e233-1356x833.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Issues with due dates display a calendar icon on the list or board with a color indication to quick understanding of an issue's status. The icon will be:

- Red if it's overdue
- Orange if it's due within the next week, or
- grey otherwise.

Hover over the icon to view the due date and how many days are remaining or have passed since it was due.

If you don't see the icon on your list or board view, open Display Options and make sure that Due Date is selected under Display properties.

## Add due date⁠

Use the shortcut Shift D when viewing or selecting an issue to set the due date. During issue creation, select the three dot menu to bring up the set due date option.

## Due date notifications⁠

Configure due date notifications in account settings. You will receive a notification when an issue's due date is near and/or if the issue is past due.

## Filter by due date⁠

Type F then search due or click the add filter button to apply the following related Filters to any issue view:

- Overdue
- 1 day from now
- 1 week from now
- 3 months from now
- Custom date or timeframe
- No due date

## Sort by due date⁠

On list views, open view options and select Ordering: Due date to sort issues by due date. Issues with a due date will show up at the top of each group.

[PreviousCustomer Requests](https://linear.app/docs/customer-requests)[NextEstimates](https://linear.app/docs/estimates)# Estimates

Source: https://linear.app/docs/estimates

---

# Estimates

Show how much effort each issue will take.

![Linear app showing an issue estimate being changed](https://webassets.linear.app/images/ornj730p/production/e1af0f17db6f9c374fb850cfbc0a59e4025f7f47-1114x668.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Use estimates to describe the complexity or size of an issue. Cycles and projects use estimates to calculate effort and related statistics. You'll opt into estimates on a team level as well as choose which estimate scale to use.

## Configure⁠

Go to Team Settings > General > Estimates to enable the feature. Teams can use different estimate scales and configurations, even if they're working together on the same project.

![estimate settings](https://webassets.linear.app/images/ornj730p/production/15930ec67ceb31085b1f70ccbaa735818560fcea-1400x962.png?w=1440&q=95&auto=format&dpr=2)

### Scale range options⁠

When T-Shirt sizes require translation to numerical values (for display in graphs, for instance,) they follow the Fibonacci scale.

### Extended estimate scales⁠

Enable the extended scale to add two additional values to your scale.

### Zero estimates⁠

Allow zero estimates by toggling this option on in estimate settings. By default, we count unestimated issues as one point but you can disable this in estimate settings as well.

## Add, edit, or remove estimates⁠

Add estimates when creating or updating issues with the keyboard shortcut Shift E. The same keyboard shortcut can be used to edit or remove the estimate.

## Filter for estimates⁠

Find issues with specific point values by filtering for estimates. The shortcut F will open the filter menu and you can select estimates from there. This is especially helpful when creating custom views and searching through the backlog.

## Analytics⁠

When you see the word effort, that refers to estimate. When estimates are not enabled, we calculate statistics using a default value of 1 estimate point per issue. T-shirt estimates map to the Fibonacci scale.

If you've enabled estimates, we'll use the estimate values to calculate percentage completion and effort in cycle and project graphs. The top bars on most views will show the total issues count or total estimate value next to the view's name. Hover over the number to see both values.

![image](https://webassets.linear.app/images/ornj730p/production/c377a88c314fd6d0ceacf255f927c3220f1d9a07-16x16.svg?q=95&auto=format&dpr=2)

When estimates are too large, refine issue scope Larger estimates usually mean that there is uncertainty about the issue's complexity. We find that breaking up issues into smaller ones is the best approach.



[PreviousDue dates](https://linear.app/docs/due-dates)[NextIssue relations](https://linear.app/docs/issue-relations)# Issue relations

Source: https://linear.app/docs/issue-relations

---

# Issue relations

Create relationships between issues such as blocking, related, and duplicate.

![Issue relations blocking and relating to other issues](https://webassets.linear.app/images/ornj730p/production/4d5b81c2af018955702e62e2e78d40cc620cc737-946x448.png?w=1440&q=95&auto=format&dpr=2)

## Overview ⁠

Tag issues with relations and dependencies to help your team identify and remove blockers and work on the most important issues. You can mark issues as blocked, blocking, related, and duplicate.

## Add relationships⁠

The issue and type of relationship will show up in the issue properties sidebar.

From the issue editor, add a relation using keyboard shortcuts or by selecting the overflow menu after saving the issue. From a list or board, use either the keyboard shortcut, command menu or contextual menu. You'll be prompted to find and select the related issue. You can add as many related, blocking, blocked, or duplicate flags as you like but will have to repeat the steps for each one.

## Related issue⁠

When you reference issues in a description or comment, they'll automatically become a related issue. Alternatively, use M + R to relate one issue to another. When viewing an issue you can open the command menu (⌘/CTRLK) and type "Create new issue related to…".

To remove a related issue, hover over the related issue and click the X. You can also select Remove relation from the command menu ⌘/Ctrl K. If you have more than one relation, you'll be prompted to select which relation to remove.

## Blocked / blocking⁠

Mark issues as blocked by other issues with M then B. If other issues are blocking the current issue, they'll show up in the issue sidebar with an orange flag under Blocked by.

Mark issues as blocking other issues with M then X. If the issue is blocking other work, the blocked issues show up in the issue sidebar with a red flag under Blocks.

Once the blocking issue has been resolved, the blocked issue flag turns green and moves under Related.

## Duplicate⁠

Merge duplicate issues into the canonical (saved) issue with the shortcut by pressing M and  M. This will mark the issue you are viewing or have selected as a duplicate issue and change the status to canceled. You cannot mark issues the other way around (e.g. view the canonical issue and mark other issues as duplicates of it). If you have more than one canceled status, you can specify which status to apply under Team Settings > Workflow.

[PreviousEstimates](https://linear.app/docs/estimates)[NextLabels](https://linear.app/docs/labels)# Labels

Source: https://linear.app/docs/labels

---

# Labels

Use labels to categorize issues.

![Linear app showing labels being added to an issue](https://webassets.linear.app/images/ornj730p/production/3a4ffc89117bc3bd582ef96ee1a120607adfa5ad-1688x1325.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

### Labels⁠

Labels allow you to organize issues. Create them scoped to the workspace or a specific team level, so they're available only where relevant. You should create labels that are used by all teams (e.g. "Bug") in the workspace-level, so they will be accessible to all teams.

### Label groups⁠

Label groups create one level of nesting in your workspace and team labels, giving you more options when organizing issues. Each label group is limited to 250 labels.

Please note that labels within groups are not multi-selectable, so when applying labels to issues only one label from each group may be applied.

## Create labels⁠

Create labels in Settings > Workspace > Labels page or Team settings > Labels.

### Create a label during add label workflow⁠

You can also create labels in the Add label flow. Take the action to apply a label, then type the name of the label you want to create. The label will be automatically be saved to your team's labels.

If you'd like to create a label or label group directly from the Add label flow, this is available with the syntax label group/label or label group:label . For example, using Type/Bug or Type:Bug  will create the label group "Type" and the label "Bug".

![Type/Bug syntax being used to create a label in the group "Type" with the label "Bug"](https://webassets.linear.app/images/ornj730p/production/9074377f9a2bda6f688ee1e008ea1c2249581aad-1312x238.png?w=1440&q=95&auto=format&dpr=2)

## Apply labels⁠

Apply labels to any issue with the shortcut L, or by clicking into the label property field in an issue's right sidebar.

## Manage labels⁠

Labels can be edited, merged, and deleted in issue label settings. Label data like SLA and Triage rules the label's used in, when it was last applied, and how many issues have that label appear in settings to guide your choices.

In workspace label settings, optionally select to display both all team and workspace labels on that page for ease of editing. Or, in larger workspaces, search for particular labels to assist in cleanup.

Edit label name or color by clicking on those properties in a label row. Or, right click on the row to see additional options like converting to a group, moving to workspace, or deleting the label.

Take bulk actions by selecting multiple labels (x or Shift + click), then right-clicking on any selected label to choose an action. You  can move rescope labels to and from the workspace level to a particular team, or change a label's team. If you find duplicates, merge multiple labels into a single label.

### Label descriptions⁠

Add brief label descriptions in label settings. These descriptions appear when you hover over an applied label anywhere in Linear. These descriptions give a consistent understanding of when a label should be applied. Triage Intelligence also considers label descriptions to inform whether to suggest a particular label.

### Archive labels⁠

Archiving a label keeps it on any issues where it's been applied, but stops people from using that label moving forward. Views, insights, filters and groups all respect archived labels. Take this option when you no longer need a label actively, but you want to retain historical context.

Archive labels in label settings, through the overflow menu on a particular label's row.

### Delete labels⁠

If you're sure a label no longer needs to exist, you can also delete it. Deleting labels is not reversible (including by Linear support) and will remove it from issues where it's applied, so please proceed with caution.

Delete labels in label settings, through the overflow menu on a particular label's row.

## Filtering and views⁠

Team-specific labels "act" like workspace labels when filtering all teams or multi-team views. As long as labels in different teams share the same name, filtered results will show all issues across all teams that match the label. This holds true in custom views, my issues, project all team views, and general search (/). It does not extend to the API (you'll have to use the unique identifier for each team's label).

If you only want to see results for a specific team's labels in a multi-team view, add a team filter on top of the label filter. Creating a workspace label with the same name as existing team label(s), will present the option to convert the team label(s) to the workspace level.

Learn more about Label views and how to filter for labels.

## Reserved label names⁠

We reserve the following label names that are duplicative of existing features to not cause confusion:

"assignee", "cycle", "effort", "estimate", "hours", "priority", "project", "state", "status",

[PreviousIssue relations](https://linear.app/docs/issue-relations)[NextPriority](https://linear.app/docs/priority)# Priority

Source: https://linear.app/docs/priority

---

# Priority

Set issue priority to indicate which issues to complete first.

![Linear app showing the priority menu on an issue](https://webassets.linear.app/images/ornj730p/production/cf0e427cf3138f660c031595d5fdd4f95637e3c9-1752x1028.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Priority is an optional property for Linear issues to signify to your team the urgency of the issue. You can add the following priorities to issues: low, medium, high, and urgent.

We don't have the option to set custom priorities or more granular priorities since it's easy to get carried away with specificity. Adding too many options makes it harder to set priority and leads to diminishing returns. If more granularity is needed, the best workaround is to create additional workflow statuses or use labels.

## Set priority⁠

Select an issue or issues or from the issue view, type P and then select the issue priority. Use the shortcut again to change or remove the priority.

## Priority ordering⁠

On any view ordered by priority, simply drag & drop an issue or project above other ones to indicate it is more important. The exact position will be saved globally across your workspace, so that anyone else looking at a view ordered by priority will see these issues or projects in the same relative positions. By default, items without an assigned priority level are now always sorted last.

## Urgent Notifications⁠

When you set issues to have Urgent priority, we'll send a notification to the issue assignee and immediately send an email notification if they have those enabled.

[PreviousLabels](https://linear.app/docs/labels)[NextSLAs](https://linear.app/docs/sla)# SLAs

Source: https://linear.app/docs/sla

---

# SLAs

Automate SLAs for issues that should be completed within a certain amount of time.

Available to workspaces on Business and Enterprise plans

![Issue screen showing medium risk SLA](https://webassets.linear.app/images/ornj730p/production/4a4f4ec90f50960a3dee7dc7211d4e013c2a67e1-1652x895.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

SLAs (Service-level agreements) automatically apply deadlines to issues when they match your defined parameters. While traditionally used to describe service level agreements with your customers, SLAs can also be used to maintain internal standards for how quickly bugs will be fixed and time-sensitive issues will be resolved.

## Configure⁠

Enable the feature in settings under Workspace > SLAs, then use the workflow builder to create rules for when to apply an SLA to a newly created issue.

SLAs won't be applied to existing issues that have already been prioritized. Changing the priority of an existing issue will trigger SLAs however once the change matches your SLA rules.

## Basics⁠

SLAs appear on issues as a fire icon which transitions from gray > yellow > orange > red as an issue nears and breaches the SLA. Once the issue is completed, the SLA field remains and indicates completion time down to the minute and whether the SLA was achieved early or failed.

SLAs are automatically created on any issue that matches the rules set in SLA settings. You can also manually add SLAs to issues if desired.

### Default SLAs⁠

When you enable SLAs, you'll enable a set of default rules:

- When Priority is Urgent, add a 24 hour SLA
- When Priority is High, add a 1 week SLA
- When Priority is Medium, Low, or No Priority, remove the SLA

You can edit, delete or create new SLA rules as desired.

### Create new SLA Rules⁠

Select New Rule to create a new SLA rule.

Set the time interval to any of the following durations:

- 12 hours
- 24 hours
- 48 hours
- 1 week
- 2 weeks
- 4 weeks
- Custom time: Hour, Day, Business day and Week

You can filter by almost any field to specify when SLAs should be applied, including Team, Status, Assignee, Creator, Priority, Labels, Project, Project Status, and Initiative, and filters can be combined.

### Business Day SLAs⁠

When configuring an SLA with a custom time period, you can choose business days as your unit of time to exclude days that are not a part of your work week.By default Business days are considered Monday through Friday.On the SLA settings page, you can choose optionally to set your work week to  Sunday > Thursday. This will affect your SLA calculations and other features that  skip working days, like nudges on project reminder updates. When setting an SLA manually on an issue, you can choose business days or standard days when choosing a duration.

![Business day SLAs settings](https://webassets.linear.app/images/ornj730p/production/e283f7d5b724f3799af272452405906eda894830-1776x696.png?w=1440&q=95&auto=format&dpr=2)

### Remove SLAs⁠

Linear's default SLA rules contain conditions to remove SLAs when priority is marked as Medium, Low, or No priority. These "removal" rules are helpful to maintain data hygiene, so that if an issue's priority is downgraded, SLAs which are no longer relevant will be removed. We recommend keeping these in the workspace.

### SLA status and filtering⁠

Linear groups SLAs into different SLA statuses. You will be able to filter and organize views of issues by their SLA status, and the different statuses will be indicated by the color of the SLA icon.

### SLA notifications⁠

Subscribers to an issue with an SLA receive notifications in their Inbox when SLAs are 24 hours away from being breached as well as when SLAs are breached. Individuals can opt in to receive notifications whenever any issue in their Team has an SLA, too. Manage these notifications in settings under Account > Notifications.

### Viewing SLA issues⁠

You can filter any view to see issues according to SLA status: Breached, High Risk, Medium Risk, Low Risk, Achieved, Failed, and No SLA.

Insights offers a helpful way to evaluate how well you're meeting your SLAs. Filter a view by SLA, set Insight parameters to Issue count (measure) and SLA status (dimension) to see a clear breakdown of how well you're meeting your SLAs.

### Manually apply SLAs⁠

You can add SLAs to issues even when they don't apply to a predefined rule. Select the three dot menu from the issue creation modal to apply an SLA.

Note that if you create an SLA that conflicts with a "removal" rule, the SLA will automatically be removed after the issue is created. In these cases, you can override the rule but only if you add the SLA by editing the issue after it's created (not during issue creation). Do so from the issue view by selecting the three dot menu, then Set SLA.

## FAQ⁠

[](https://linear.app/docs/sla#collapsible-be162c0b23a9)We recommend creating a custom view filtered down to issues that contain SLAs. You can group the view by SLA status and also use Insights to explore the data.

[](https://linear.app/docs/sla#collapsible-78ea0d71c908)No, we do not offer custom naming for SLAs.

[](https://linear.app/docs/sla#collapsible-ab474e1e2710)Subscribers will be notified 24 hours prior to a potential SLA breach.

[](https://linear.app/docs/sla#collapsible-72937d97f114)An issue may use either due dates or an SLA, but not both. If an issue has a due date and then has an SLA applied, the due date will be replaced by the SLA





[PreviousPriority](https://linear.app/docs/priority)[NextProjects](https://linear.app/docs/projects)# Triage

Source: https://linear.app/docs/triage

---

# Triage

Manage issues created by other teams and customer support integrations.

![Triage](https://webassets.linear.app/images/ornj730p/production/30183e73c9ef009bb8cb14adbe97d9f34a5b9a69-2352x1632.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Triage is a special inbox for your team. When an issue is created by integration or by a workspace member not belonging to your specific Linear team, it will appear here. Triage offers a opportunity to review, update, and prioritize issues before they are added to your team's workflow. Consider using Triage responsibility to set a rotating schedule of ownership for monitoring incoming issues.

## Configure⁠

Go to your Team Settings > Triage. Once you toggle it on, Triage will appear under the team name in the sidebar.

## Basics⁠

Navigate to Triage with G then T. If you are in another team's views, use O then T to open the team you want to view first.

### Create issues⁠

New issues will default to Triage status if they are created through an integration (e.g. Slack, Sentry), created when inside of the Triage view, or if members outside of your specific team create the issue.

Setting default templates in Team Settings > Templates can override the triage status.

### Take actions⁠

Open the issue to review it and take one of the following issue actions: accept with 1, mark as duplicate with 2, decline with 3, or snooze with H.

Accepting an issue will offer the option to leave a comment and then move the issue to your team's default status.

To ask for more information from the user who created the issue, comment on the issue and keep it in Triage or snooze it until you're ready to take an action.

Marking as duplicate will offer a choice of which existing issue to merge the duplicate into. Taking this action will also move the new issue's attachments to the canonical issue, including customer requests and attachments. Once selected, the new issue is updated to a Canceled status type. The shortcut MM also triggers the mark as duplicate action.

Declining will update the issue to a Canceled status type and present the option of adding a comment with an explanation.

Snoozing will hide the issue from the triage queue to return at a time of your choosing, or when there's new activity on that issue: whichever comes first. See snoozed Triage issues by toggling the preference in View Options. Snoozing hides the issue in Triage from other users by default as well.

### Triage Intelligence⁠

On Business and Enterprise plans, our Triage Intelligence feature allows LLMs to analyze every new issue in triage against your existing issues to suggest properties like assignee and label, and pro-actively surface likely related issues or duplicates based on the analysis of the issue's content against historical behavior in your workspace. Learn more about Triage Intelligence here.

### Triage rules⁠

Triage rules functionality is supported on our Enterprise plan.

On Enterprise plans, configure custom rules to take automated actions on issues when they enter Triage. Triggered on filterable properties, triage rules can update an issue's team, status, assignee, label, project and priority.

Once configured, rules are executed in order from the top down. When moving issues to another team's Triage via rule, the new team's rules are applied to the issue as well. If rules conflict, this is surfaced in the interface.

Consider combining triage routing with custom Asks fields to create a scalable system to intake issues from Slack. Users fill out what they know and automations send the issue to the right team or assignee.

![two triage rules; if any of three customers set priority to high, and if labeled iOS move to team Mobile](https://webassets.linear.app/images/ornj730p/production/f41716bdc477cee4fadc5fabeff3bf47c09f27bc-1832x934.png?w=1440&q=95&auto=format&dpr=2)

### Triage responsibility⁠

Triage responsibility is available on our Business and Enterprise plans.

Enable triage responsibility to define who handles incoming issues. You can select specific members of your workspace to receive notifications of new issues or be automatically assigned to them. Configure triage responsibility in your team's Triage settings.

![Triage view of a Linear workspace](https://webassets.linear.app/images/ornj730p/production/c40aa85cbcf9b1ae058bd94c2fb3dd7d2017270a-1784x515.png?w=1440&q=95&auto=format&dpr=2)

Once triage responsibility is set, optionally connect your PagerDuty, OpsGenie, Rootly, or Incident.io schedules to automate the rotation of first responders. If you use another provider, we have opened up that API so you can build a custom schedule.

Members of your team will be able to easily see who is currently assigned to monitor triage when creating issues.

## Integrations⁠

### Asks⁠

Use Triage to seamlessly intake issues reported from non-Linear users through Asks.

### Support integrations⁠

Get more out of Triage by connecting it to our support integrations—Intercom, Front, and Zendesk—or Slack. Using these integrations, your support team can create new Linear issues or link customer reports to existing issues directly from their customer support tool.

## FAQ⁠

[](https://linear.app/docs/triage#collapsible-6554f37d047c)Yes. Configure this behavior under Team Settings > Triage.

[](https://linear.app/docs/triage#collapsible-11bbc5452305)By default, we exclude triage issues from all views since triage is considered to be outside the normal workflow. To include them in a custom view, you need to explicitly include them by adding a status filter where "Triage" is included.

[PreviousCustom Views](https://linear.app/docs/custom-views)[NextUser views](https://linear.app/docs/user-views)