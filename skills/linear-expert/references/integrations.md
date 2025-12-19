# Table of Contents

- Airbyte
- Asks
- Discord
- Figma
- Front
- GitHub
- GitLab
- Gong
- Google Sheets
- Integration Directory
- Intercom
- Jira
- Notion
- Salesforce
- Sentry
- Slack
- Zapier
- Zendesk

---

# GitHub

Source: https://linear.app/docs/github

---

# GitHub

Linear supports linking your GitHub pull requests, automating workflow statuses, and syncing issues between GitHub and Linear.

![Linear logo and Github logo](https://webassets.linear.app/images/ornj730p/production/d41fdca27f9f36238e86e4c01d3cd9d91b078d6b-2880x1620.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

The GitHub integration offers two core functionalities:

### Permissions⁠

The integration needs the following permissions for Pull Requests and GitHub Sync:

- Read access to checks and metadata
- Read and write access to issues and pull requests

Linking Linear issues to commits is handled through GitHub webhooks, which do not require access to your codebase.

To grant Linear organization-level access in GitHub, the integration must be installed by a GitHub organization owner. If you only need repository-level access, a repository administrator can install the integration instead.

## Configure⁠

### Enable the GitHub integration⁠

- Go to Setting > Features > Integrations > GitHub
- Click Enable
- Select the GitHub organization you want to connect
- Select All repositories or Only select repositories and choose the repositories you want to connect
- Click Install
- Authenticate into your personal Github account

#### GitHub Enterprise options⁠

If it's relevant to your organization, GitHub Enterprise Cloud and GitHub Enterprise Server require additional setup compared to GitHub.com. See the following section for details of each.

If you're using GitHub Enterprise Cloud and have IP Allow List security setting enabled, you'll also need to turn on Enable IP allow list configuration for installed GitHub Apps setting to enable Linear's GitHub integration. Read more here.

Alternatively you can grant access to Linear's IP addresses:

35.231.147.226

35.243.134.228

34.140.253.14

34.38.87.206

34.134.222.122

35.222.25.142

We've expanded Linear's pull request automation to self-hosted GitHub Enterprise Server. You can now install the new integration to link Linear issues with a GitHub instance that's hosted in a custom URL. This integration doesn't require new firewall rules.

GitHub Enterprise Server will support the majority of the functionality of our existing GitHub integration with the exception of GitHub issue syncing and commit linking. GitHub.com and Enterprise Cloud users should use our standard GitHub integration instead.

The table below provides a comparison of available features across GitHub.com, GitHub Enterprise Cloud, and GitHub Enterprise Server.

#### Add multiple GitHub organizations⁠

Click the + icon under Connected organizations to add another GitHub organization. This will take you through the same flow as when you connected the first organization. Currently, we support multiple organizations for the PR automation only. You will only be able to use commit linking with a single GitHub organization.

It is not possible to connect multiple Linear workspaces to a single GitHub organization. This is a limitation on GitHub's side. GitHub Apps can only be installed once for a GitHub organization so this means only one Linear workspace can be connected.

#### Branch format⁠

Select the branch format you want to use when copying the branch name using Cmd + Shift + . from a Linear issue and pasting it into your branch name.

![Branch format setting](https://webassets.linear.app/images/ornj730p/production/9a16304705f1e90c4056d4270221b3f09ac7c71b-1362x366.png?w=1440&q=95&auto=format&dpr=2)

### Personal account connection⁠

In addition to the organization-level setup, each member should connect their personal GitHub account. This ensures that the activity feed, synced comments, and assignees are mapped directly to the connected user in Linear, rather than appearing as generic GitHub activity.

To connect your account, navigate to Settings > Connected accounts. Once connected, any synced activity from GitHub will be correctly attributed to you in Linear.

![Section in your Github integration settings that indicates your personal account is not yet connected.](https://webassets.linear.app/images/ornj730p/production/48fb82ecd332e000afc047dc8a8fb5459079cdd2-1362x200.png?w=1440&q=95&auto=format&dpr=2)

![Connect your personal Github account to link issues with commits, PR, and branches.](https://webassets.linear.app/images/ornj730p/production/ec39f09171f32564bb2e8314bebaa85513b0b4ed-1422x466.png?w=1440&q=95&auto=format&dpr=2)

### Enable commit linking⁠

- Turn on the toggle for Link commits to issues with magic words at the bottom of the GitHub settings page.
- Go to Settings → Webhooks in your GitHub organization or repository.
- Click Add webhook button
- Input the Payload URL and Secret provided in Linear, and select application/json content type. Leave "Push events" selected.
- Click Add webhook.
- Go back to Linear and click Done.

![Setting to enable commit linking](https://webassets.linear.app/images/ornj730p/production/1aae774b895db809359e7fd2b080341a6b797de1-1372x250.png?w=1440&q=95&auto=format&dpr=2)

### Configure GitHub Issues Sync⁠

Watch this video to see how GitHub Issues sync works:

From the GitHub Issues section of the GitHub integration settings, click the + icon, then select the GitHub repo and Linear team to link.

You can choose to sync:

- One-way: issues created in GitHub will create a synced copy in Linear, or
- Two-way: issues created in either the GitHub repo or Linear team will create a synced copy in the other software

![Github Issue Sync configured for two repositories, mapped to their correlated Linear teams.](https://webassets.linear.app/images/ornj730p/production/88707d9d9208d520011ef1abc28e28d63093c236-1370x620.png?w=1440&q=95&auto=format&dpr=2)

![Setup for GitHub Issues Sync.](https://webassets.linear.app/images/ornj730p/production/f5210265017419b639ab32ccbe952133c74316ef-1042x980.png?w=1440&q=95&auto=format&dpr=2)

Multiple repositories can be connected to create issues to a single Linear team through one-way sync when issues are created in GitHub. However, only one repo can be configured for two-way sync at a time.

You can enable two-way sync when connecting a repo to Linear, or change this to another repo by pressing ... > Edit Link on an existing repo connection.

GitHub Issues Sync will only sync newly created issues. To sync existing GitHub Issues, you will have to import them. Refer to the Importer page.

Properties that are synced between Linear and GitHub issues include:

- Title
- Description
- StatusPlease note that any custom statuses set at the GitHub Project level do not sync to Linear.
- AssigneeLinear users can connect their GitHub account from https://linear.app/settings/account/connections to be synced as the issue assignee
- Labels
- Sub-issuesMulti-level & cross-repository/team hierarchies are supported. If parent issue is not a synced issue (e.g. it's in a different GH repo/Linear team), the sub-issue can still get synced, but will have no parent issue set on the other end.
- CommentsComments made not in the synced thread of the Linear issue will not get synced to the GitHub issue. This allows for private discussions.

Moving GitHub synced Linear issues between Linear teams will maintain the synced relationship. You can also transfer GitHub issues between two synced repos; this will appropriately update the team of the associated issue in Linear.

To manually stop syncing, remove the attachment from the Linear issue through its overflow menu.

Issue sync banners

Once an issue is synced between GitHub and Linear, a banner will appear at the top of the issue to make this clear. The banners will display information to show current sync status or will surface any errors with syncing.

![Synced issue banners showing connected and a sync error](https://webassets.linear.app/images/ornj730p/production/d0d25688334fad6ebef18e9411daad033b77432f-2990x400.png?w=1440&q=95&auto=format&dpr=2)



## Linking Linear issues to GitHub PRs⁠

You can link a Linear issue using pull requests or commits.

Watch this video for a quick demo on the available linking methods:

### Link through pull requests⁠

## Link multiple issues⁠

Link multiple issues to one PR

Include multiple issue IDs after the magic word in the description (e.g. Fixes ENG-123, DES-5 and ENG-256). Linking will happen after you save your changes. Magic words must be used in the PR description, they will not work if linked in a comment on the PR.

Link multiple PRs to one Linear issue

You can link multiple PRs to a single Linear issue using any linking technique. The Linear issue status will be updated when the final linked PR moves to the required state from your workflow.

For example if you have 2 PRs linked to 1 issue, you'll need merge both PRs before the Linear issue status will change.

### Link using commits⁠

Use a magic word before the issue ID in commit message to link issues. We'll move the issue to In Progress when the commit is pushed and Done when the commit reaches the default branch.

## Viewing a linked Linear issue⁠

### Remove a PR from an issue⁠

To remove a PR from a Linear issue, open the issue, click on the three dots on the PR attachment, and select Remove. You can also do this through the command menu in Linear by viewing or selecting an issue, then searching for git.

To link a PR that is already open, modify the PR title or description to link an issue.

### PR review state⁠

When individual reviewers comment, request changes, or approve your PR, we'll display their avatars and their actions on the GitHub attachment visible on the linked Linear issue. You can use this feature to quickly parse the review state of your PR without needing to return to GitHub.

![PR comments and approved state displayed in Linear attachment.](https://webassets.linear.app/images/ornj730p/production/71c7f822215a7dbd92212e4e4cf15fe06412bec0-1642x190.png?w=1440&q=95&auto=format&dpr=2)

If you request a team review instead of a review from specific individuals, we display "review requested" or "in review" on the GitHub attachment in place of user avatars.

### Pull request preview links⁠

If your PR contains one or multiple preview links, this will add a preview link shortcut to the Linear issue.

Preview links are automatically detected for popular platforms like Vercel, Netlify, Cloudflare and AWS Amplify if you have connected Linear with your GitHub repository. We also support custom preview links: pull request descriptions and comments are parsed for any markdown links ending with "preview," once these are added by the PR author or a GitHub bot.

Multiple previews for a single PR are available in a dropdown menu, with customizable names and icons for easy identification (e.g. mobile and desktop previews). Icons are automatically chosen to reflect best their name, such as a mobile icon for mobile release links. Preview links are automatically removed after 30 days of inactivity on the PR.

![Preview links on a Linear issue](https://webassets.linear.app/images/ornj730p/production/3a621c036a7905eba1232e10ab9d0198b462ad4d-2140x1105.png?w=1440&q=95&auto=format&dpr=2)

Pull request preview link accepted formats

Links that end with "preview" in your PR descriptions and comments will get added to the Linear issue as a preview link. For example:

![PR containing preview links](https://webassets.linear.app/images/ornj730p/production/2560ff47911cab9d2cd2b0a4df57810572801a98-901x649.png?w=1440&q=95&auto=format&dpr=2)

Vercel comments with the following format will be added as a preview link in your Linear issue.

![Vercel preview comment in GitHub](https://webassets.linear.app/images/ornj730p/production/56ded746ad9cab1212c73a7619cfcaf528d2cd8f-1278x531.png?w=1440&q=95&auto=format&dpr=2)

Netlify comments with the following format will be added as a preview link in your Linear issue.

![Netlify PR comment with preview](https://webassets.linear.app/images/ornj730p/production/99d538e6966157ac67473bb4a2e70db205f1aa3a-1277x575.png?w=1440&q=95&auto=format&dpr=2)

## Workflow automation⁠

### Issue status updates⁠

Updates to PRs can automatically update the status of their linked Linear issues.

Watch this video to explore more about how issue status automation works:

You can customize the automation in Settings > Team > Issue statuses & automations > Pull request and commit automation. Since this is a team setting, it must be configured for each team in your workspace.

You can configure status updates when PRs are drafted, opened, have a review requested, are ready for merge, and merged. By default, we will move linked issues to "In Progress" when PRs are open and "Done" when PRs merge.

![Pull request and commit automation](https://webassets.linear.app/images/ornj730p/production/84e19df283f1da9252108a9fed0a4761697bb999-1430x896.png?w=1440&q=95&auto=format&dpr=2)

The "Ready for merge" automation relies on GitHub reporting a stable/mergeable PR status. If any check (including non-required checks) fails, GitHub reports the PR as unstable and the automation to move issues to the ready-for-merge destination will not trigger.

### Custom merge queues⁠

If you use a custom merge queue that merges changes and then closes the pull request, be sure to add the externally-merged label before closing it. This tells Linear to treat the pull request as successfully merged even though it was closed.

### Branch protection rules⁠

Once a review is requested, if you do not have branch protection rules set up in GitHub, the issue will skip the "review request or activity" state and move to "ready to merge”. Without branch protection rules, a PR is considered always mergeable. Please note that "ready to merge" automations will not fire if a "review request or activity" automation is not also configured.

### Branch-specific rules⁠

You can also set custom workflow automations based on particular target branches.

For example, you can now configure that when a PR is merged to:

- staging, the issue status should change to “In QA”
- main, the issue status should change to “Deployed”

Branch rules apply only to target branches—the branch a PR is being merged into. Automations are not supported for source branches, the branch the PR is created from.

Watch this video to visualize how branch-specific rules work:

You can also override a default rule in a particular branch with “no action” if desired, so that issues linked to a change in that branch will not change status. Branch rules can be specified using regex, e.g: ^fea/.* can set automations for all feature branches.

![Image shows a set of default rules, rules specific to a "staging" branch.](https://webassets.linear.app/images/ornj730p/production/61ff343a87898b3f64535a1af1fc09b1da76d711-1414x862.png?w=1440&q=95&auto=format&dpr=2)

### Auto-assign and move issue to start⁠

Save yourself a few steps by toggling on our automations that auto-assign the issue to you and move it to a started status when you copy the git branch name. To set up this automation, refer to Preferences.

## Other settings⁠

### Linkbacks⁠

When an issue is linked with a pull request, commit or GitHub Issue, Linear posts a linkback message as a comment with the issue title and description—including any images or attachments that exist within the description. All the pull requests are also listed in the issue details in Linear. This cross-referencing makes it faster to retain context without jumping between apps.

If enabled for private teams, the issue titles will not be included in the comment. The link will go to your Linear issue and be accessible only by users who are part of that private team.

![Setting for enabling or disabling linkbacks.](https://webassets.linear.app/images/ornj730p/production/524d938918c0a733d722d9a39f8c3589265dba8a-1376x490.png?w=1440&q=95&auto=format&dpr=2)

### Enable Autolink⁠

If you want to automatically resolve your Linear issue IDs (e.g. ENG-123) in PR descriptions or comment to links, you can enable this using GitHub's Autolink references feature. See instructions on GitHub.

Use the following URL format: https://linear.app/<workspace>/issue/ID-<num> where workspace corresponds to your workspace's URL and ID is the issue identifier key for your team. You need to add each team separately as they all have a different ID pattern.If you change your Linear team name/ID, you may need to reconfigure the Autolink settings.

## FAQ⁠

[](https://linear.app/docs/github#collapsible-038e5e50ce78)If you get an error when setting up your GitHub integration, or it doesn't work:

- Disconnect the integration from GitHub's side.
- Open Linear in the browser and reset your local database by going to https://linear.app/reset.
- Reconnect the integration in Linear settings.

These are the most common causes of errors:

- The integration got out of sync. In this case, reconnecting and resetting should fix it.
- You can only connect your GitHub account to a single Linear workspace. The workaround is to ask someone else from your org to set up the integration.

[](https://linear.app/docs/github#collapsible-7b93baacd8a5)Go to integration settings and remove linkbacks. This should reduce the notifications.

[](https://linear.app/docs/github#collapsible-57f683ac890d)Make sure you completed the following steps during integration installation:

- Copied the provided webhook secret and saved it when creating the Linear GitHub App for your GHES instance. Without the secret, Linear is unable to verify requests
- Installed the newly created app to organizations and their repos you wish to link

If you missed the step 1 during installation, you'll need to Disconnect the integration inside Linear, and remove the installation inside your GitHub's developer settings, and re-install.

If you haven't completed the step 2, but successfully created the app, you can link new organizations and repositories under "Install App" in the application's developer settings.

If you have added new organizations, or repositories, they will also need to be linked to the application under developer settings under the "Install App" menu.

[](https://linear.app/docs/github#collapsible-0f9fcfdc21d5)For the "Ready for merge" workflow to trigger, either review or checks are required within GitHub for this PR. Without either of these, the "Ready for merge" workflow will not trigger.

![GitHub workflow settings](https://webassets.linear.app/images/ornj730p/production/6f22958c2c097f287fc3304dddc183a08d803a0f-1332x608.png?w=1440&q=95&auto=format&dpr=2)

[](https://linear.app/docs/github#collapsible-cfbf30fc7aba)If you have already merged multiple PRs into a single branch and you want to merge that branch into a new branch, we will not auto-detect any Linear issues that were linked in the previous PRs. You will need to link each issue anew. You can do this by mentioning the Linear issue IDs in the new PR title or by mentioning them alongside magic words in the PR description.

[](https://linear.app/docs/github#collapsible-707f3cb58aa6)If your branch name includes a Linear issue ID, Linear will automatically link the pull request to that issue. Even if you manually unlink it, the connection can return when you push new commits or when the PR is merged.

To prevent this from happening, include the magic word skip or ignore followed by the relevant Linear issue ID in the PR description:

- skip ENG-123
- ignore ENG-123

This will fully unlink the PR and prevent status automation, even if the branch name still includes the issue ID.



# GitHub

Source: https://linear.app/docs/github-integration

---

## Getting started

[OverviewUnderstand how to configure your Github integration and what the integration powers.](https://linear.app/docs/github#overview)[Organization connectionSet up the GitHub integration at the organization level.](https://linear.app/docs/github#enable-the-github-integration)[Account connectionConnect your GitHub account to enable features like assignee syncing.](https://linear.app/docs/github#personal-account-connection)## Linking your work

[Pull request linkingConnect Linear issues to PRs with branches, titles, or magic words in the description.](https://linear.app/docs/github#linking-linear-issues-to-github-prs)[Commit linkingUse commit messages with magic words to automatically link work to Linear issues.](https://linear.app/docs/github#enable-commit-linking)[Magic wordsUse a magic word to link your work, either in the PR description or commit message.](https://linear.app/docs/github#link-through-pull-requests)## Workflow automation

[Issue status automationAutomatically update Linear issue statuses based on PR and commit activity.](https://linear.app/docs/github#issue-status-updates)[Branch-specific rulesCustomize your automation by target branch.](https://linear.app/docs/github#branch-specific-rules)[Assign and move forwardAssign yourself and move issues forward when creating branches from Linear issues.](https://linear.app/docs/github#auto-assign-and-move-issue-to-start)## Reviews

[Configure ReviewsEnable pull request reviews to sync review state into Linear.](https://linear.app/docs/pull-request-reviews#enable-reviews)[Viewing PRsSee reviewers and the status of your code reviews directly on linked issues.](https://linear.app/docs/pull-request-reviews#view-prs)[PR NotificationsStay updated with review requests and review activity in Linear.](https://linear.app/docs/pull-request-reviews#notifications)## Github Issues Syncing

[Configure Issues SyncLink GitHub repos and Linear teams for one-way or two-way issue syncing.](https://linear.app/docs/github#configure-github-issues-sync)[Github Issues ImporterImport historical GitHub issues into Linear for complete tracking.](https://linear.app/docs/github-to-linear)# GitLab

Source: https://linear.app/docs/gitlab

---

# GitLab

Linear supports linking your Linear issues to GitLab and automates your merge request workflows.

![Linear and GitLab logos](https://webassets.linear.app/images/ornj730p/production/d025b73f1b272515da65e8823306b88dff8aa699-2880x1620.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Link Linear issues to GitLab merge requests. Automate your MR workflow so that issues update when MRs are drafted, opened, merged and when reviews are requested. You can link single or multiple issues to a specific MR.

## Configure the GitLab integration⁠

We support linking GitLab merge requests for both hosted and self-hosted installations, as long as your installation is publicly available.

- Navigate to Linear Settings > Features > Integrations > GitLab
- Click Enable to launch the set-up pop-up.

![Pop-up for setting up the GitLab integration](https://webassets.linear.app/images/ornj730p/production/535b00faf5fdbfad01399eb8bdaffb7ca1efa780-1002x948.png?w=1440&q=95&auto=format&dpr=2)

- Navigate to GitLab > User Settings > Personal Access Token or GitLab > Project Settings > Access Token to create an API access token.An access token is used to query the GitLab API for further information and also used to post issue linkbacks. Because GitLab doesn't support bot accounts, linkbacks are created under the name of the token owner. It's recommended that you create a new user for Linear to act as the bot account.
- When creating the token, set the api or read_api scope.If the read_api scope is selected, Linear will not post linkbacks to the issue on GitLab merge requests. If using a project access token, the token needs Reporter role or higher.
- (Optional) Enable and set a custom URL for your self-hosted GitLab installation without any path (e.g. https://gitlab.yourcompany.com). This URL needs to be accessible to public Internet and is only required for self-hosted installations. The earliest supported version of GitLab is 15.6.If you need to grant access to Linear's IPs, they are 35.231.147.226, 35.243.134.228, 34.140.253.14, 34.38.87.206, 34.134.222.122, and 35.222.25.142.
- Click Connect.
- Linear will generate the Webhook URL after it validates the access token. Copy and paste this URL to GitLab in either:A Group's Webhook Settings (For a company on GitLab's Premium or Ultimate tiers) to integrate all projects under it.A Project's Webhook Settings, to individually connect a specific project.
- Enable the following Triggers:Push eventsCommentsMerge request eventsPipeline events
- Under SSL verification, ensure Enable SSL verification is checked
- Click Save changes.

## Link Merge Requests⁠

### Create a new branch⁠

Set the branch format in Linear Settings > Workspace > Integrations GitLab > Branch format. When viewing or selecting a Linear issue, use the Copy git branch name action or shortcut Cmd/Ctrl + Shift  . It will give you a branch name with the issue ID which you can use to create a new branch in GitLab.

We recommend using common branch naming patterns throughout all of your teams.

### Add the issue ID in the MR title⁠

Include the Linear issue ID (e.g. ID-123) in the MR title when creating merge requests.

### Use a magic word⁠

Add a magic word + issue ID in the MR description (e.g. Fixes ENG-123). The integration cannot link MRs via comments or commit messages. The available magic words to link issues are: close, closes, closed, closing fix, fixes, fixed, fixing resolve, resolves, resolved, resolving complete, completes, completed, completing.

To link MRs to issues without them automating your issue status on MR merge, use the one of the contributing magic words: ref, references, part of, related to, contributes to, towards. When using a non-closing magic word like this, the linked MR or commit will still move the issue through other statuses per Workflow settings, but will not automate the issue's status when the MR or commit merges. Instead, it will only transition the issue through to what’s configured prior to the On MR or commit merge event.

#### Link multiple Linear issues to an MR⁠

To link multiple Linear issues to a single Merge Request, or to link a Merge Request after creating it, use the magic word linking method by including multiple closing statements in the MR description (e.g. Fixes ENG-123, DES-5 and ENG-256). Linking will happen after you save your changes. The Linear issue will not close until all Merge Requests have been closed/merged.

## Merge Request automation⁠

The merge request automation allows you to select specific statuses for your Linear issues based on MR changes—saving you the hassle of updating Linear issues manually.

Customize the MR automation in Settings > Team > Workflow. Since this is a team setting, it must be configured for each team in your workspace.

![MR status automation set for the following categories: on draft mr open, on mr open, on mr review request, on mr ready for merge, on mr merge](https://webassets.linear.app/images/ornj730p/production/b26feeac53ba12d391fef53daa87a38366e4a6f2-1346x676.png?w=1440&q=95&auto=format&dpr=2)

### Ready for merge automation⁠

If you'd like to use the Merge Request automation to capture passing CI checks, please verify in GitLab that:

- You have enabled Pipeline events under the Webhook settings for any repo part of the GitLab integration.
- All pipelines that Linear should consider when determining if an MR is mergeable need to be merge request pipelines. GitLab documentation is available here.
- Under ‘Merge requests’ in project settings, ‘Pipelines must succeed’ is checked.

If you want to capture MR approvals, please verify in Project Settings > Merge requests that Merge request approvals are required.

### Custom merge queues⁠

If you use a custom merge queue that merges changes and then closes the merge request, be sure to add the externally-merged label before closing it. This tells Linear to treat the merge request as successfully merged even though it was closed.

### Branch-specific rules⁠

You can set custom workflow automations based on particular target branches. For example, you can now configure that when a MR is merged to:

- staging, the issue status should change to “In QA”
- main, the issue status should change to “Deployed”

You can also override a default rule in a particular branch with “no action” if desired, so that issues linked to a change in that branch will not change status. Branch rules can be specified using regex, e.g: ^fea/.* can set automations for all feature branches.

## Issue linkbacks⁠

When an issue is linked with a merge request, Linear posts a linkback message as a comment with the issue title and description. All the merge requests are also listed in the issue details in Linear. When your MR is being reviewed in GitLab, see the avatars of up to three most recent reviewers and their review states without leaving Linear. This cross-referencing makes it faster to retain context without jumping between apps. Linkbacks are managed by the scope selected.

## Auto-assign and update status⁠

Save yourself a few steps by toggling on our automations in Settings > My Account > Preferences > Behavior.

- Auto-assigns the issue to you, and/or
- Move the issue to the first Started status (which you can customize in Settings > Team > Workflow) when you copy the git branch name.

## Auto-linking⁠

GitLab supports rendering URLs pointing to Linear when you mention issue IDs in GitLab. To configure this functionality, please reference GitLab's documentation.

## FAQ⁠

[](https://linear.app/docs/gitlab#collapsible-4f14ba0e1398)Our issue migration assistant does not support GitLab issues. We suggest customizing the CLI importer to import issues. One option is to customize the importer to support GitLab imports. Another option is to export GitLab issues to a CSV and then modify the headers and format so that it matches one of the issue trackers supported by the CLI.

[](https://linear.app/docs/gitlab#collapsible-880ef80ea411)Modify the MR title or description to link an issue. See the section on this page titled Linking MRs to issues.

[](https://linear.app/docs/gitlab#collapsible-0c4b49967f64)Open the issue in Linear and right click on the merge request attachment to bring up an option to remove it. You can also do this through the command menu in Linear by viewing or selecting an issue, then searching for git.

[](https://linear.app/docs/gitlab#collapsible-7b93baacd8a5)Go to integration settings and remove linkbacks. This should reduce the notifications.

[](https://linear.app/docs/gitlab#collapsible-a6254a741b3f)If your team is private, we won't disclose the issue title. The link will go to your Linear issue and be accessible only by users who are part of that private team.

[](https://linear.app/docs/gitlab#collapsible-2d97381cd50f)On GitLab, we have both read and write access with their API (they don't have separate permissions for comments).

[](https://linear.app/docs/gitlab#collapsible-3aa580112ace)During integration setup, Linear requires an access token. The below is an exhaustive list of how that token is used:

- To get supplemental information about merge requests that isn't included in the webhooks we receive
- For posting linkbacks on linked merge requests
- To retrieve merge request information when linking an MR to an issue (for rich attachment)
- To retrieve merge request mergeability status when a pipeline completes

[](https://linear.app/docs/gitlab#collapsible-93d6a16da88d)We currently only allow issues to transition to the status you've chosen for "On MR ready for merge" if you also have a status selected for "On MR review request or activity". Make sure that you have a status selected for this event.

![GitLab MR workflow status events](https://webassets.linear.app/images/ornj730p/production/69971e7151c829466d84567e82fbf516db5c6390-1586x742.png?w=1440&q=95&auto=format&dpr=2)

[](https://linear.app/docs/gitlab#collapsible-287d5f894dd4)In GitLab's webhook settings, check that the webhook used for Linear is active. If it isn't, please send take a screenshot of its recent events and send it into support@linear.app for further support.

In the meantime, please click the "Test" button for the relevant webhook and confirm if you continue to see issues with the integration.

[](https://linear.app/docs/gitlab#collapsible-528f0e91f376)It is not currently possible to connect multiple GitLab instances to your Linear workspace, you will need to select one GitLab instance to connect within your GitLab settings.



[PreviousGitHub](https://linear.app/docs/github-integration)[NextGoogle Sheets](https://linear.app/docs/google-sheets)# Slack

Source: https://linear.app/docs/slack

---

# Slack

Combine Linear with Slack to keep everyone in sync.

![Linear logo and Slack logo](https://webassets.linear.app/images/ornj730p/production/42ec7d05b6dd1e64e3803ac7752b7e2c325058a5-2880x1620.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Create Linear issues from Slack messages, sync threads between Slack and Linear, set up personal and channel-specific notifications, display rich unfurls in Slack and more.

## Configure⁠

### Integration setup⁠

Go to Settings > Features > Integrations > Slack to connect your Slack account to Linear. You must be a Linear admin to do this.

Once this has been completed, others in your Linear workspace can:

- Use Linear agent if your plan is Business or Enterprise
- Create Linear issues from the More actions menu on Slack messages or by using the /linear command on all plans
- Take quick actions from Linear links shared in your Slack workspace
- View rich unfurls in Slack that show key issue, comment, document, initiative or project details
- Enable personal Slack notifications
- Send team and project updates to dedicated Slack channels

### Notifications setup⁠

Slack notifications are available for teams, projects, and individuals. Once the initial integration has been configured, any user can set up these notifications.

Set up team notifications from team general settings or from the integration settings page. Authenticate to Slack and then choose a channel for the notifications to post to.

Set up project notifications from individual project pages. Click on the bell in the titlebar on the top right of the app, authenticate to Slack, and choose a channel for the notifications to post to.

Set up personal Slack notifications from notification settings. Authenticate to Slack and then choose which notifications to receive.

Click the bell icon at the top of a view, then the Configure button next to Slack notifications. Turn on the toggle and authorize Linear to post to a particular channel. Choose whether to be notified for when an issue is added to the view, completed/canceled, or both.

Moving forwards, notifications for these selected changes will be sent as messages to the chosen Slack channel.

### Connect multiple Slack workspaces⁠

Linear's Enterprise plan supports connecting multiple Slack workspaces to Linear to use the Slack integration. If you're using Slack's Enterprise Grid plan for example, this would allow you to use the Slack integration across your workspaces. To add a new workspace, go to Linear's Slack integration settings and click the  button under connected workspaces. You must hold Admin permissions on an Enterprise Linear plan in order to enable this feature.

## Linear agent for Slack⁠

This agent is available on Business and Enterprise plans.

Mention @linear in discussions on Slack, and the Linear agent will create issues informed by your conversation's context. Use natural language to specify issue details or simply let the agent infer what's needed.

For example, try:

- @linear file a bug, assign me
- @linear make feature requests from this thread
- @linear file to the Rideshare Loyalty project

To use this functionality, send /invite @linear to the desired Slack channel before sending. This feature is available to users in your Slack workspace with Linear accounts.

### Set Linear agent guidance⁠

Linear agent considers instructions you write in Slack integration settings on how to create issues. Use this field to refine the agent's behavior and give it more context about how you use Slack.

You might give it context about your channel naming structure and how it relates to your Linear projects, what statuses you prefer it create in, the team it should use when unsure, and more.

Outside of this field, the agent also uses contextual clues to help infer where to create issues (for example, if you're sending project updates from a project to a channel that sounds related, issues created in that channel will favor creation in that project.)

## Create issues with message actions⁠

You can also create issues using the More actions menu on a Slack message if you prefer to specify all the details of your created issue.

If you select a team in the resulting window that uses default templates, that template's text will appear in the description field. Only Linear users in your Slack workspace can create issues with this integration.

If you're interested in allowing non-Linear users in your Slack workspace to create issues, consider using Asks instead.

### Use templates⁠

Your issue templates in Linear can also be used in Slack. Add templates to your Slack integration from workspace template settings or the Slack settings page. Admins can make up to 10 issue templates available in your Slack integration, which any Linear members in your Slack workspace can view and apply during issue creation. If you have a default template set for your team, it’ll show up as an additional template option after the team has been selected.

Templates in private teams are not available to the Slack integration (nor in other integrations that support templates like Intercom and Zendesk.) If you need to allow users to create issues using templates in private teams, consider using Asks where this use-case is supported.

### Sync threads⁠

![Image showing a synced thread in Linear that also posts to Slack](https://webassets.linear.app/images/ornj730p/production/fa1449871ae3ec87e600bd34708505162578c054-5760x3538.png?w=1440&q=95&auto=format&dpr=2)

To use synced threads in private channels, invite the integration using /invite @Linear. Synced threads is not available when using /linear or in DMs that don't include Linear.

To create a synced thread, create an issue from Slack through the More actions menu on a Slack message.

When you click Submit, you'll also create a synced comment thread in the Linear issue by default. Both threads will update as replies are sent in either location, and we'll also update the synced thread in Slack when the issue is completed or canceled, or reopened after being completed or canceled.

When people in your company report issues in Slack, syncing threads is a great way to keep them in the loop regardless of whether they're in your Linear workspace. Comments made in the synced Linear thread will also appear in Slack, and the Slack thread will be updated when the issue is completed or canceled.

If an issue synced to a Slack thread is marked as a duplicate of another issue, we'll also update the Slack thread where the duplicate was created once the canonical issue is resolved.

### Add Slack messages to existing issues⁠

There are a few options to link Slack messages to existing Linear issues.

If there is not already a synced thread on the issue, you can choose to sync with an existing Slack thread. To do so, paste the issue's URL into the thread and send the message. Select the overflow menu from inside the unfurl and choose "Sync thread".

![syncing a Linear thread manually](https://webassets.linear.app/images/ornj730p/production/cbeb13764b09360f5e94824645ed7bad148ab041-1556x829.png?w=1440&q=95&auto=format&dpr=2)

To associate a Slack message to a Linear issue without syncing, copy the Slack message's URL through the overflow menu on that message. In the Linear issue, use Control L to add that URL as an attachment. No updates or messages will be sent to the Slack message when linking this way.

On an issue in Slack, use the overflow menu to select "Link existing issue". Search for and select the issue to associate the Slack message with the Linear issue. With this type of linking, no terminal updates will be sent to the Slack thread, and no synced thread will be created.

### Notifications functionality⁠

Team notifications will post updates to a specific Slack channel when issues in that team are created, receive comments, and/or update status.

We recommend creating a separate #linear or #linear-team channel in Slack for these updates, especially if you choose the option to post status updates (we post every time an issue status changes).

Projects have two types of notifications: Slack channel notifications and personal notifications.

Project Slack channel notifications will post updates to a specific Slack channel when issues in that team are created, receive comments, and/or update status.

Personal notifications for projects are not directly tied to Slack. They'll subscribe you to receive a notification whenever an issue is created in a project, which you will get in the Inbox (and personal Slack notifications if you have set those up to receive those in notification settings).

Receive the same notifications in Slack that you normally get in Inbox, email, or desktop push notifications. Once enabled, the notification settings page will let you choose which issue, project, and team updates you want to receive via Slack. A Linear app will appear under Apps in your Slack workspace which is where these notifications will be sent.

### Rich unfurls and issue actions ⁠

Once you've connected the integration for Slack, we'll show expanded links anytime you post issue, project, document, or initiative links from public teams in Slack.

URLs associated with private Linear teams never unfurl. Unfurling can be disabled in Settings > Integrations > Slack if desired.

Issue links show the issue title, description, status, assignee, and creation date.



They also give other Linear users in Slack the option to update the assignee, comment on the issue, and subscribe or unsubscribe to the issue directly from Slack. You can also engage Slack sync in an existing thread from this menu.

Project links in Slack will show a preview with the project name, description, status and target date.

Whenever you mention an issue ID in Slack , a reply with the issue link is automatically added in thread. To prevent clutter, repeated mentions of the same issue ID in this thread within 60 minutes won't generate additional replies. After 60 minutes, posting the issue ID in this thread will prompt a new link reply. Mentioning this issue ID in additional messages or threads elsewhere during this 60 minutes will generate a reply. You can disable this feature in 'Linear settings > Integrations > Slack' if desired.



This feature does not work in shared channels to protect the privacy of your issues

## FAQ⁠

[](https://linear.app/docs/slack#collapsible-5ed2cbed24ec)You can use the /linear command in Slack as a lightweight way to create an issue.

This action will be confirmed by an ephemeral message in Slack which is only displayed to you. /linear is not supported in Slack threads, for Slack sync or for uploading files to issues.

[](https://linear.app/docs/slack#collapsible-a10e7556f08a)This is intentional behaviour. There's rarely a scenario where you will create an issue without having to change the title or the description in some way. We choose to populate both the issue title and the issue description with the message text so that there's a higher chance you won't need to change both prior to creating the issue.

[](https://linear.app/docs/slack#collapsible-202510ecde5c)Only users with Linear accounts can create issues in Slack using the Linear integration. Slack Guests cannot install or approve apps in Slack, so they'll be unable to use the Linear integration even if they have a Linear account.

Everyone in your Slack workspace will be able to see team and project notifications pushed to Slack channels and issues created in channels as long as they are part of the Slack channel.

We do have an integration which enables non-Linear users to create issues for workspaces on on our Business and Enterprise plans: Linear Asks.





[](https://linear.app/docs/slack#collapsible-402cd716dd74)Go to workspace settings to import your team's favorite emoji to Linear. This is great for building team morale and creating a consistent experience in your team's workflow.

[](https://linear.app/docs/slack#collapsible-b6b6219cb4bf)Yes! Separate from the integration, you can also join our community on Slack! We have a community of Linear users who share tips, feedback, and discuss how they're using Linear with their team. There's also an #api channel for people building apps on our GraphQL API.

[](https://linear.app/docs/slack#collapsible-be34d3ed6e94)Please contact us at support@linear.app for any feedback or issues around using the Linear integration for Slack.

[](https://linear.app/docs/slack#collapsible-d2550ba4edee)Our privacy policy is here and you can refer to our security FAQs here for further information.

[](https://linear.app/docs/slack#collapsible-9af4fcb4f3d5)Yes, you can link an existing Slack thread to a Linear issue over our API. To do so, pass syncToCommentThread: true in the input to the attachmentLinkSlack mutation (documentation is available here.)

[](https://linear.app/docs/slack#collapsible-37ea9d7f65f5)If your org installed Linear Asks first and the Slack integration discussed on this page second, unfurls will not work for the regular Slack integration. To fix this:

- Disconnect both the Asks and Slack integrations from Linear.
- Disconnect Asks from the Slack Marketplace

![Disconnect connected workspace](https://webassets.linear.app/images/ornj730p/production/98546c65ca6fb71b615df4631d3cb11d4bd64750-703x406.png?w=1440&q=95&auto=format&dpr=2)

![Disconnect connected workspace](https://webassets.linear.app/images/ornj730p/production/adec2590b6f0181b3028a9c19534c49625dcdd44-723x539.png?w=1440&q=95&auto=format&dpr=2)

- On the Slack side, go to Tools & settings -> Manage apps. Linear Asks should not appear in the list of installed apps (Linear may still appear if other users in the workspace have personal Slack integrations installed, but this is fine)

![Manage apps in Slack](https://webassets.linear.app/images/ornj730p/production/d845d745081aed4e5faa33baa0c0bcbf3a808ac9-651x761.png?w=1440&q=95&auto=format&dpr=2)

- Reconnect the Slack integration in LinearUnfurls for public team issues should now work in SlackTemplates available to Slack will need to be reconfigured
- Reconnect the Asks integration in Linear. You will have to manually re-add the Asks bot to any channels you have configured for Asks in Slack.Asks team to Linear channel configuration is retained after reconnecting, but you will need to toggle the available templates on for each team.

[](https://linear.app/docs/slack#collapsible-e5a0dbcbca2b)Linear uses LLMs from OpenAI that have the potential to generate inaccurate results.





[PreviousSentry](https://linear.app/docs/sentry)[NextZapier](https://linear.app/docs/zapier)# Figma

Source: https://linear.app/docs/figma

---

# Figma

We use Figma at Linear and our integrated tools make it easy for you to collaborate on design.

![Linear and Figma logos](https://webassets.linear.app/images/ornj730p/production/715e73405ea73596781be7d43896081207e38598-2880x1620.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

There are two ways to connect Figma to Linear to streamline your design and development workflows. The Linear plugin for Figma allows you to create and link issues directly from Figma. A separate integration enables you to embed designs into Linear descriptions, comments and documents.

G then S to go to Settings

Paste the link to embed file

Click on files to open in Figma (no shortcuts)

To update the preview, use E to go into issue edit mode or select the more menu (three dots) to edit a comment, then hover to bring up the refresh button

- Paste the link to embed file
- Click on the link to open in Figma
- To update the preview, go into issue or comment edit mode, then hover to bring up the refresh button

No command menu options available

## Configure⁠

#### Embed Figma previews in Linear⁠

Connect to Figma under Settings > Features > Integrations > Figma. We recommend that you do this in a browser and not the desktop client. Once connected, the integration will work across your full workspace.

#### Linear plugin for Figma⁠

To create or link issues from Figma, select a frame, section or link and run the Linear plugin from Resources > Plugins > Linear or run directly from the Figma community here.

## Embed Figma Previews⁠

#### Preview designs⁠

Simply copy a link to specific frames or files and paste it into a Linear issue description or comment. We automatically convert the link into a design preview. Even if the file changes, the snapshot in Linear remains as it appeared when the comment or description was created.

#### Open files⁠

Click to preview the embedded file without having to leave Linear. We currently support interactive in-app preview of publicly shared Figma files only. We're considering building support for private files in the future. We built this as a custom integration using Figma's API with their OAuth2 authentication instead of using their standard embed to create a faster experience.

#### Refresh files⁠

By default, we do not refresh the Figma preview so that you maintain the context of related comments and issue descriptions. To update the preview, go into Edit mode in the issue or comment, then hover over the Figma file. You'll see a Refresh button appear, which you can click to pull the latest version. This action cannot be undone.

## Linear Plugin for Figma⁠

Run the plugin to see all Linear issues linked to your designs. From the plugin, select issues or the linked elements below the issue description to be taken to the inked frame, section, or page.

## Create issues⁠

When using the Linear plugin from within Figma, select the  button to create issues that link pages, frames, and sections of your Figma design. You'll be able to create issues in any teams that you've joined.

#### Link issues⁠

Link designs to existing issues by searching for the ID, title, or description. From the Linear side, you can link designs to issues by attaching Figma links for the page, section, or frame using Ctrl L. You can link multiple issues to the same design and multiple frames, sections, or pages to a single Linear issue.

#### Update issues⁠

Update properties such as team, status, assignee, and project directly from Figma. You'll be able to update these at any point during your design process. Any changes made in Linear are immediately synced to the Figma plugin.

#### Filter and sort⁠

Filter your issues that appear in the plugin window to hide completed or cancelled issues, show only assigned or created by you, and to sort by status, priority, nam, or created date. By default, the plugin will hide canceled issues.

## Figma Plugin ⁠

### Privacy Policy⁠

- Terms of Service By authenticating the plugin, you agree to Linear's Terms of Service. Plugin authentication grants you access to Linear's features and functionality.
- Figma File Key Transmission When the plugin is opened within Figma, Linear will receive the file key for the current Figma file. When connecting a frame in Figma to a Linear issue, Linear will receive and securely store the file key associated with the respective Figma file. This storage of file keys allows Linear to establish the necessary connection and enable bi-directional linking between Figma and Linear.
- Figma File Key Access Any user with access to a Linear issue will also have access to the associated file key for any linked Figma frames.
- Data Removal Users have the authority to remove Figma data stored by Linear at any time. This can be achieved by either disconnecting the frame from the Linear issue or deleting the associated team or workspace. To permanently delete your data from Linear’s storage contact security@linear.app
- Data Processing All data, including Figma file keys, is processed by Linear in accordance with Linear’s Data Processing Agreement (DPA). The DPA outlines the measures taken by Linear to ensure the privacy and security of customer data. For more details on our data processing practices, please refer to our DPA.

## FAQ⁠

[](https://linear.app/docs/figma#collapsible-1fbaafe83348)First, check that the Figma integration is connected in settings. We'll disable integrations if we notice they're not working anymore (admins should receive an email if we do) and it's also possible that someone on your team removed the integration, intentionally or not.

If the Figma integration is enabled and it's still not working, try removing and then reconnecting the integration.

- Open Linear in the browser and remove the integration.
- Go to linear.app/reset
- Reconnect to Figma via the browser.

Reach out to us in support if you still have trouble after taking those steps.

[](https://linear.app/docs/figma#collapsible-c7b9bb8fcc56)By default, any Figma links added to Linear will embed and there is no way to hide it. The workaround is to hyperlink text in a comment or description instead of pasting the full link.

[](https://linear.app/docs/figma#collapsible-139056291aa6)We've noticed this issue specifically for If your Brave shield is up you must manually allow "cross-site cookies" to be able to view authenticated Figma embeds.

![Brave browser settings](https://webassets.linear.app/images/ornj730p/production/aad6a15aa033a4d4ccd01d6c4e866d75fd218f3d-834x1164.png?w=1440&q=95&auto=format&dpr=2)

[](https://linear.app/docs/figma#collapsible-84078abe3578)This error message typically also references "Insufficient permissions to access the file". While you yourself may have access to the file, it's important that the installer of the Figma integration in Linear also has access to the file. If they don't this error message will appear. The solution here is to share the file with the team member who installed the Figma integration.

[](https://linear.app/docs/figma#collapsible-907ac1acd5ea)Connect the integration using Linear in a web browser. If the integration doesn’t work on the macOS app, open Linear in a browser and disconnect the integration. Then open the macOS app and clear application data (found under Linear in the application menu bar). Open Linear in the browser again and reconnect to Figma. If that doesn’t work, reach out to us at support@linear.app.





[PreviousDiscord](https://linear.app/docs/discord)[NextFront](https://linear.app/docs/front)# Notion

Source: https://linear.app/docs/notion

---

# Notion

Preview Linear issues directly from Notion

![Linear logo next to Notion logo](https://webassets.linear.app/images/ornj730p/production/aa059b63024dcffde6775ea37c92ab424d6dc98e-2880x1620.png?w=1440&q=95&auto=format&dpr=2)

### Overview⁠

The Notion integration embeds Linear issues and projects into Notion pages. They can be previewed in Notion or clicked to open the file in Linear.



### Configure⁠

Paste a link from Linear into Notion and follow the setup steps. Alternatively, Connect to Notion from within Linear under Settings > Features > Integrations > Notion. Each user in a workspace wishing to use this integration must set it up individually.

If desired, multiple Notion workspaces can be connected to the same Linear workspace.



### Basics⁠

Embed files

Simply copy a link to a specific Linear issue or project and paste it into a Notion document. Choose whether to paste the link as a rich preview, a less detailed mention, or the raw URL.



Open files

Click the preview, mention or URL to open the associated data in Linear.

Refreshing mentions and previews

Once issue, project, or view properties change in Linear, the preview in Notion changes accordingly (on page reload or manual preview refresh).

[PreviousJira](https://linear.app/docs/jira)[NextSalesforce](https://linear.app/docs/salesforce)# Jira

Source: https://linear.app/docs/jira

---

# Jira

Enable Jira Sync while trialing or transitioning to Linear to keep Jira spaces up to date.

![image](https://webassets.linear.app/images/ornj730p/production/507bb59e625a3d4ab4cc0e7502ae7199a4d68ea7-16x16.svg?q=95&auto=format&dpr=2)

To complete a one-time import from Jira to Linear, use the CSV or API credential options in importer. Imported issues import as synced only if the Jira integration is configured prior to completing your import. Switching from another tool? Follow our manual.

![Linear and Jira logos](https://webassets.linear.app/images/ornj730p/production/adbef6f35402b94c3522a0f38ac578573dcb6f57-2880x1620.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Some companies choose to import issues and switch to Linear immediately; others prefer to trial Linear on a small team first or need some time to make the full transition. For the latter cases, we built Jira Sync. This feature allows you to connect Jira spaces to Linear teams, so that new issues created in Jira or Linear are kept current in both places.

## Permissions⁠

The user creating the API token to enable Jira Sync must have the ADMINISTER permission in Jira. This is necessary for Linear to install the required webhooks. It is possible to remove the global ADMINISTER permission after the setup is complete without impacting this integration.

If the ADMINISTER holder does not have a Linear seat or does not want this permission stored in Linear, please see the FAQ.

Create an API key for this user by following instructions here. The default token expiry is one week, please choose to enable for a year instead.

API keys might not be available. Instead, you need to create a personal access token (or PAT). Instructions can be found here. The default token expiry is one week, please choose to enable for a year instead.

#### Posting in a synced thread⁠

In order to send a reply to a synced thread, you'll need to link your Atlassian account first.

[](https://linear.app/docs/jira#collapsible-0bb4c78125da)Jira Server users will be presented with a simple form to input their own personal access token.

![OAuth consent screen for Jira Sync](https://webassets.linear.app/images/ornj730p/production/f6d920cbe88216b212e34342426a83e1a16dbae7-1196x1270.png?w=1440&q=95&auto=format&dpr=2)

## Configure⁠

Enable the integration in Linear from workspace settings under Workspace > Integrations > Jira.

Enter your personal access token (see Permissions > Setup above), email address and installation or cloud hostname and then select which Jira space to link to which Linear team. For the installation or cloud hostname, remember to remove the http:// and anything after .net.

For best performance, users should link their individual Jira accounts in Settings > Integrations > Jira > Connect personal account. This allows better handling of fields in Jira like Assignee and Creator.

## Basics⁠

### Select Jira Spaces⁠

We've set up the integration so that Jira spaces map to teams in Linear. You can link each Jira space to only a single team in Linear, so the same space cannot create issues in multiple Linear teams. Multiple Jira spaces can be linked to the same Linear team though and issues will be created in Linear from any connected Jira space.

### Relationship to Jira Imports⁠

Running a Jira import will not automatically import issues as synced unless you've configured the Jira integration prior to the import. You do not need to create the space/team mappings prior to importing. For full instructions about importing issues as synced, please see our Importer documentation.

### Synced properties⁠

Once the integration is enabled, any new issue created in a linked Jira space or Linear team will create a synced version of that issue in the other service.

[](https://linear.app/docs/jira#collapsible-e066fe481ec7)* For these fields to sync successfully, the relevant user must connect their Jira account to Linear in Settings > Integrations > Jira > Connect personal account. If no connection exists, the Assignee field will be unassigned, and/or the creator field will be the user who configured Jira.

** Deleting a synced issue in either Jira or Linear will not delete the issue in the other direction, or otherwise affect status in the synced issue.

If a synced issue in Jira moves to a status not in Linear, The Linear issue's status will not update. The status will update in Linear if the synced issue is moved in Jira to a status that can be mapped properly, or if the status is changed in Linear directly.

*** For labels to sync from Jira to Linear, the label must have already been created in Linear (either through a previous import, or by creating the label manually or through our GraphQL API. When labels sync from Linear to Jira, we'll create a new label in Jira when appropriate.



### Sync directionality⁠

When configuring the mapping between a Jira space and a Linear team, you have the choice of syncing uni-directionally or bi-directionally.

When syncing uni-directionally, issues created in Jira are also created in Linear. Changes made to that issue from Jira are synced to Linear, but changes made in Linear do not sync back to Jira.

When syncing bi-directionally, creating an issue in either service will create a synced copy in the other. Updating the synced copy in either service will sync changes back to the other issue.

### Issue sync banners⁠

Once an issue is synced between Jira and Linear, a banner will appear at the top of the issue to make this clear. The banners will display information to show current sync status or will surface any errors with syncing.

![Jira synced issue banner](https://webassets.linear.app/images/ornj730p/production/08bd834bb5c1c5ae41ac68192a284a82363690f7-2874x150.png?w=1440&q=95&auto=format&dpr=2)

### Limitations⁠

There are a number of features in Jira that Linear has chosen not to pursue as a matter of product philosophy. These discrepancies are worth noting, as they will affect sync. Among these are Issue Type, Constraints, Components, and Required fields. Read more about how these differences are handled by sync below.

[](https://linear.app/docs/jira#collapsible-3140e701d25a)If a Jira project's workflow demands required fields, we will not create the synced issue in Linear. In the case where an issue has been created in Linear before required fields are enforced in Jira, we'll send an error to the Linear issue as a comment to surface the problem.

[](https://linear.app/docs/jira#collapsible-a7166ff1bcca)Issue type is a native required field in Jira. Bug, Story, Epic and Task are common issue types. When you create a new issue in Linear and we create a synced issue in Jira, it will be type Task if we find that type in Jira.

If this type has been deleted, we'll fallback to the first type on the list. If issues created in Linear are created in Jira as Story for instance, you may wish to create a type Task so that future issues created in Linear will display appropriately.

[](https://linear.app/docs/jira#collapsible-7797ee852337)You may have constraints in Jira that prevent certain updates to a Jira issue   until various conditions are met.

If you update a synced Linear issue in a way that violates Jira constraint, the Linear issue will update but the Jira issue will not.

[](https://linear.app/docs/jira#collapsible-76f03ae1d719)In a synced Linear issue, components appear as labels - "Component: Engineering" for instance. These labels cannot be grouped or deleted. Removing a component label from an issue in Linear will remove the component in the synced Jira issue.

### Issue filter⁠

By default, Jira Sync will create and sync every issue that’s created in the mapped Jira space. If you wish to filter out some issues, you have the ability to do so by editing the webhook in Jira.

Please note that any JQL filters you applied to limit the scope of import do not apply for Jira Sync purposes. In order to change what is provided to Linear for Jira Sync, follow the instructions below:

Go to Settings → System → Advanced → Webhooks. Select the Linear webhook and click Edit.

The Issue related events box allows you to provide a custom JQL query to filter out some issues that you do not want to sync with Linear. This works both when the conditions are met at the time of the Jira issue's creation, as well as if the Jira issue is updated to meet the parameters of your filter later.

Here is an example to only sync issues with the label Bug:

![image of editing a webhook in Jira to restrict returned results](https://webassets.linear.app/images/ornj730p/production/82c1152a9b627e4b7ebf326122e3dc08a9deea5c-2096x316.png?w=1440&q=95&auto=format&dpr=2)

### Pre-sync issues in Jira⁠

Once configured, Jira Sync will create issues in Linear when issues are created in a synced Jira space. Issues belonging to that synced space from before the sync was configured will not create issues in Linear.

However, when those issues receive updates in Jira, the updates will prompt those issues to be created and synced in Linear.

### FAQ⁠

[](https://linear.app/docs/jira#collapsible-933ae95cc8e4)Jira Sync is a forward looking integration -- it will create new issues in Linear or Jira when a new issue is created in a synced context in either service.

If you'd like to import your Jira issues as synced, please follow the steps here.

[](https://linear.app/docs/jira#collapsible-cf59c9c4f235)If you change metadata in synced Jira spaces (delete, add, make them unrequired) this may cause the Jira issue and Linear issue to become out of sync.

Clicking the refresh button on the list of synced Jira spaces in Linear settings will update the list of available spaces, but also update the metadata to Linear's context. This is a fix forward; issues already out of sync because of missing metadata will not update after pressing this.





![Showing the refresh button in the Jira integration to account for new Jira metadata](https://webassets.linear.app/images/ornj730p/production/028551dbcc69612f31c12505703eedd684a6c3d9-819x469.png?w=1440&q=95&auto=format&dpr=2)

[](https://linear.app/docs/jira#collapsible-8beba3452ac8)No, Issues imported to Linear in general will not create a synced copy in Jira. The specific exception to this is if you set up a synced Jira project in Linear and import from that Jira project to Linear.

Other imports outside of this will not create synced issues in Jira.

[](https://linear.app/docs/jira#collapsible-62f19343e964)You may wish to triage Linear issues created by Jira instead of syncing their status automatically (for example, you may want the opportunity to decline the issue before admitting it to your backlog).



While this integration is broadly intended to keep Jira and Linear issues in sync, you can workaround this by renaming your first status under type Started something besides To do, to-do or similar variants. When the integration can't determine the right status at issue creation, it falls back to Triage. In other words, if your first started status is called "Started" in Linear and "To do" in Jira, new issues created by Jira in Linear will go to Triage.

[](https://linear.app/docs/jira#collapsible-040215bfba20)Yes, a Linear issue will be created when a Jira issue is moved into a synced space.

[](https://linear.app/docs/jira#collapsible-f9e0ea3d891d91af23aff92d4857f603)No, a Jira issue will not be created when a Linear issue is moved from one team to another. This will only work when an issue is created directly in the Linear Team.

[](https://linear.app/docs/jira#collapsible-4e540549b1c6)This integration may also be setup with the webhook option. The actor who configures the webhook must still have ADMINISTER, but this can be done between two people synchronously -- A Jira ADMINISTER holder without a Linear seat, and a Linear admin with BROWSE PROJECTS permissions.



To do this, the Linear actor would choose the "Manual Webhook" option in Linear > Settings > Integrations > Jira

![shows the webhook option when enabling jira sync](https://webassets.linear.app/images/ornj730p/production/bbfe85dd0e58a3f01b7642dc0c3d653fccf8eb16-516x243.png?w=1440&q=95&auto=format&dpr=2)

Then, the same person can fill this section:

![Picture of the form asking for API token, Jira account email address and jira hostname](https://webassets.linear.app/images/ornj730p/production/b10ac5161fcb397d860c4e6fa15238ed3f0d6c75-487x414.png?w=1440&q=95&auto=format&dpr=2)

On submission, they'll be presented with this form. They can then share the webhook URL and these instructions with the Jira ADMINISTER holder, who can setup the webhook in Jira directly:

![jira webhook form in Linear](https://webassets.linear.app/images/ornj730p/production/b2c81982922bb2ccefd750b2fcf17adda6acc7c3-485x584.png?w=1440&q=95&auto=format&dpr=2)

After the webhook is setup, the Jira actor can securely share the webhook secret (through something like 1Password) to the Linear admin, who can input it where prompted and click Save. Any Linear admin can then manage the integration from within Linear.

[](https://linear.app/docs/jira#collapsible-a492a83b93a4)Viewing the sync error will tell you more specific information about the root cause of the sync error. This can typically occur in cases where an issue is missing on Jira or your permissions are not configured correctly.

For permissions errors, using Jira's permissions helper can shed light on where the error lies.

![Jira permission helper](https://webassets.linear.app/images/ornj730p/production/1b0faa06c89c3759263aa68f59d4e584de22eba8-633x344.png?w=1440&q=95&auto=format&dpr=2)

Fill the values to:

- ​User​: This should be set to the user who created the Jira Sync integration (you can check this in Linear in Settings > Integrations > Jira > Enabled by)
- ​Issue​: Even though we are looking to check permissions to create new issues, the form requires us to pick an issue to check against. Choose any issue.
- Permission:​ Choose Create issues. Then click submit and look for a status in the blue box, it should tell if that user has access to this permission on this project. If not, the details below should contain some clues about what's missing.

[](https://linear.app/docs/jira#collapsible-58470b53467a)Sub-teams are not considered when mapping Jira spaces and Linear teams.

If a parent team is linked to Jira bidirectionally, issues created in that parent team will be created in Jira. Issues created in its sub-teams will not be created in the linked Jira team.

The sub-teams themselves may be linked individually to Jira spaces however, and this will work independent of the parent team's sync settings.



[PreviousIntercom](https://linear.app/docs/intercom)[NextNotion](https://linear.app/docs/notion)# Discord

Source: https://linear.app/docs/discord

---

# Discord

Combine Linear with Discord keep everyone in sync.

![Linear logo and Slack logo](https://webassets.linear.app/images/ornj730p/production/3cb5427465846c01e025bfa502231d96530d4682-2880x1620.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Create issues and search for them from the Discord app. The wrap command will post a summary of your day's work in the channel.

/linear issue to create an issue in Linear

/linear search to search and then post an issue

/linear wrap to share a summary of your issue updates in the last 24 hours

## Configure⁠

Connect to your Discord server to create issues from Discord messages, search issues, and use the wrap command.

### Integration setup⁠

A Linear admin must first enable the integration for the workspace. One they have, you can go to Settings > Features > Integrations > Discord to connect your Discord account to Linear. Every Linear user must individually link their account in order to use the Linear integration in Discord.

Once connected, anyone with a Linear account will be able to do the following:

- Create Linear issues from Discord with the /linear issue command.
- Search and display Linear issues in Discord
- Post a wrap, a summary of your days work, in your Discord channel.

## Basics⁠

### Create issues⁠

Type the /linear issue command into any channel to create a Linear issue. You will need to fill in the issue title and team and you will also have the option to add a description, status, assignee and project.

### Search issues⁠

Type the /linear search command into any channel to search Linear issues on your workspace. The application uses the same search as the app, so you can search for issues by issue ID or words in the title, description, or comments. Once you select the relevant issue and click enter, this will be posted to the channel for all members to see.

### Post your daily wrap⁠

Type the /linear wrap command into any channel and click enter to post a summary of any issues you started or completed in the past day.

### Link Discord messages in Linear issues⁠

- Click on contextual menu icon … to the top right of the issue
- Click Add link
- Click Discord message

discord when in issue view, then select Link Discord message…



### Unlink issues⁠

You can remove a Discord link from the Linear issue by right-clicking on the issue attachment.

### Filter for Discord links⁠

From any Linear view, you can filter by issues linked to Discord messages. Click F then select Links and then select Discord.

## FAQ⁠

[](https://linear.app/docs/discord#collapsible-121e172918a6)We need it in order to fetch individual message data when linking a Discord message to an issue with the "Link Discord message" action.

[](https://linear.app/docs/discord#collapsible-f03154dc40f3)It's something we'd like to support in the future, but no timeline on if/when that might be yet. If you'd like to see it, let us know at support@linear.app as we track demand.

[PreviousAsks](https://linear.app/docs/linear-asks)[NextFigma](https://linear.app/docs/figma)# Zapier

Source: https://linear.app/docs/zapier

---

# Zapier

This integration lets you build custom automations to create or update Linear issues when actions are taken on other apps or using any of Zapier's triggers.

![Linear and Zapier logos](https://webassets.linear.app/images/ornj730p/production/2b0624304661a01aeb711c514ac6d55496dc30d3-2880x1620.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Zapier is a good solution for building no-code automations with Linear.

G then S to go to Settings > Workspace > Integrations > Zapier

- Click the Avatar to go to to go to Settings > Workspace > Integrations > Zapier

settings to go to Settings > Workspace > Integrations > Zapier

## Getting Started⁠

Create a Zapier account and then create workflows using our Zapier integration. This integration is open source and you're welcome to contribute to it. Zapier has a free trial after which you're charged based on usage.

You can create workflows with apps such as Typeform, Gmail, Intercom, Google Forms, Discord, Airtable, Todoist, Productboard and more.

## Basics⁠

### Build workflows⁠

Our Zapier trigger can be combined with other app triggers or with Zapier's default triggers to build workflows and automations. For instance, you can set up a Zapier workflow that creates a Linear issue whenever a specific Typeform is filled out.



### Actions⁠

You can take the following actions in Linear in response to a trigger you configure in Zapier:

- Create a new issue
- Update an issue
- Create an issue attachment
- Create a new comment
- Create a new project

### Triggers⁠

If Linear is the start of your Zap, the following actions can be used as triggers for downstream actions in Linear or other applications:

- New issue
- New issue comment
- New document comment
- New project
- New project update
- New project update comment
- Updated issue
- Updated project update

Issues created through Zapier appear as created by “Zapier” and not the user who authorized the application.

### Example workflows⁠

- Create an issue with a bug label when you receive an email message with specific keywords.
- Create a new issue when a tag has been added to an Intercom conversation.
- Let team members or clients outside of Linear create bug reports and feature requests via an online form.
- Create an issue whenever a custom database query returns a new row.
- Create a dealflow pipeline: use a form integration such as Typeform or Google Forms to create a new Linear issue with a custom description.

### Update to latest version⁠

If you're not seeing full functionality, you may be running an old version of the Zapier integration. Update the version you're using in a Zap from the status pane:

![status pane in zapier showing an available update for Linear](https://webassets.linear.app/images/ornj730p/production/875f39f2b76b594ea8e188cfe11e08ebce581df7-1508x942.png?w=1440&q=95&auto=format&dpr=2)

## FAQ⁠

[](https://linear.app/docs/zapier#collapsible-2d4de9b5f74e)We support the syntax @[displayName](userId) to mention Linear user accounts from Zapier. For example @[alantest](68bc9696-35d5-442d-ab56-214c8cfefbec)



[PreviousSlack](https://linear.app/docs/slack)[NextZendesk](https://linear.app/docs/zendesk)# Sentry

Source: https://linear.app/docs/sentry

---

# Sentry

Our integration with Sentry lets you create Linear issues from Sentry and create links between Linear and Sentry issues.

![Linear and Sentry logos](https://webassets.linear.app/images/ornj730p/production/00e683be1ab8349d22269ba76ff9fd667c9b05b5-2880x1620.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Create new Linear issues from Sentry exceptions and link Sentry exceptions to existing Linear issues. Once enabled, the option will show up in Sentry under Linked Issues. When a Linear issue is completed, any linked Sentry issues will be automatically resolved. Re-assigning an issue in Linear will update the assignee on linked Sentry issues, too. Read more about the integration on Sentry.

G then S to go to Settings > Workspace > Integrations > Sentry

Use mouse to interact with Sentry links in Linear

- Click the Avatar to go to to go to Settings > Workspace > Integrations > Sentry
- Click on link to go open in Sentry
- Right-click on link to remove it

settings to go to Settings > Workspace > Integrations > Sentry

## Configure⁠

Enable the integration in Linear from workspace settings.

## Basics⁠

### Create issues⁠

When viewing a Sentry issue, go to the right sidebar and select Create Linear issue, then fill out the quick form. We pre-fill the description with the Sentry issue details and you'll add the title, team, assignee and priority.

### Link issues⁠

When viewing a Sentry issue, go to the right sidebar and select Link Linear issue, then search for it existing issue by ID or title.

### Automations⁠

We’ll automatically close Sentry issues when the linked Linear issue is resolved. We'll also update the assignee in Sentry if it changes in Linear (this will work if you use the same email for Linear and Sentry).You can also configure automatic creation of Linear issues based on issue/event alerts and metric alerts in Sentry from Alerts > Create Alert and customize your rules to create a Linear issue.

![image](https://webassets.linear.app/images/ornj730p/production/c377a88c314fd6d0ceacf255f927c3220f1d9a07-16x16.svg?q=95&auto=format&dpr=2)

Protip: Most list or board views let you display a Sentry icon when issues are linked to Sentry issues. If the view supports this option, you'll see it as an optional field under Display properties. Clicking the icon will take you directly to Sentry, saving you a click.

### Remove links⁠

To remove the Sentry link, right-click on the link from the Linear issue and select Remove.

## FAQ⁠

[](https://linear.app/docs/sentry#collapsible-fc4350ef4ad1)Unfortunately, the integration is limited to cloud accounts. This is a limitation with their integrations, reach out to Sentry if you'd like them to support this in the future.

[](https://linear.app/docs/sentry#collapsible-9ffffbf93302)Not at this time.

[](https://linear.app/docs/sentry#collapsible-6aa61eddbeda)You can only use this integration for public Linear teams, private teams aren't supported. If you convert a team to private any existing connection will no longer work.



[PreviousSalesforce](https://linear.app/docs/salesforce)[NextSlack](https://linear.app/docs/slack)# Intercom

Source: https://linear.app/docs/intercom

---

# Intercom

Our Intercom integration makes easy to keep track of bugs and feature requests and interact with the customers who report them.

Available to workspaces on our Business and Enterprise plans.

![Linear and Intercom logos](https://webassets.linear.app/images/ornj730p/production/b37ff30ec6a94c31bf19c16a4151747ff924f9fb-2880x1620.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

The Intercom integration lets you create and link Linear issues from Intercom conversations. Linked issues, their status, and relevant assignee show up in the sidebar in Intercom. Linked Intercom conversations will show up in Linear issues as link attachments.

## Configure⁠

Enable the integration in Linear from Settings > Features > Integrations > Intercom. A Linear app will show up in the Conversation details sidebar in Intercom with options to create issues or link issues. You can show or hide the Linear app in Intercom's sidebar by pinning Linear under Edit apps.

When troubleshooting where you uninstall and re-install the Intercom integration directly on the same Linear workspace, comment sync and status updates for existing connections will resume without problems.

## User Access⁠

Anyone in Intercom can create or link Linear issues and see the issue details in the sidebar. Only Linear users will be able to view linked issues in Linear. If the person who created the issue is a Linear member, the issue will show that it was created by them and they'll see the issue under Created in My Issues. Otherwise, the issue will show it was created by Intercom.

## Create new issues⁠

Create a new issue using the button from the righthand sidebar. It will bring up a form which requires a title and that you assign a team. You can also optionally include a description with additional details from the Intercom conversation, assign a priority, add an assignee or add a label.

Issues created through the integration will be sent to the Linear team's Triage Inbox if you've enabled that feature. The Intercom conversation will show up as a link attachment in the Linear issue.

![image](https://webassets.linear.app/images/ornj730p/production/c377a88c314fd6d0ceacf255f927c3220f1d9a07-16x16.svg?q=95&auto=format&dpr=2)

Get more out of the Intercom integration by enabling the Triage feature for your teams. Any issues created from Intercom will go to Triage when enabled (otherwise, the issues will be added to the first backlog status in your team).

### Create with Linear Agent⁠

In addition to creating issues manually from an Intercom conversation, you can now use the Create with Linear Agent option to automatically create Linear issues using AI.

When selected, Linear analyzes the entire conversation, including customer messages, support replies, metadata, and any attachments, and identifies the underlying product request or bug. The Linear Agent generates an informed title and description while pulling in the relevant context from your conversation with the customer.

![Create Linear issues automatically with the Linear Agent](https://webassets.linear.app/images/ornj730p/production/6690f2e2a1414f007321531ab0a8f1213a6aae70-696x760.png?w=1440&q=95&auto=format&dpr=2)

A customer request is created when applicable, and the issue is routed to the desired team for review and prioritization.

To use the Linear Agent in Intercom, make sure the Intercom integration is installed and connected, then enable the feature in Settings > Integrations > Intercom.

Once enabled, you can optionally provide guidance that helps the agent choose the right team or template when creating issues. These instructions can include examples, routing hints, or references to internal documentation. The agent will follow this guidance when creating issues, ensuring they land in the appropriate place within your workflow.

![Linear Agent guidance to route new issues created through Intercom](https://webassets.linear.app/images/ornj730p/production/b11dd176e244aba10997374331bb0afa8c2c5c38-1524x1428.png?w=1440&q=95&auto=format&dpr=2)

### Use templates⁠

Linear admins can designate up to 5 templates to be available for quick use from within the Linear integration in Intercom. Selecting any of these templates will pre-fill issue property fields appropriately, helping to speed up issue creation and maintain a high level of data hygiene in your issues.

## Search and link issues⁠

Click the link issue option and then search for it by title or issue ID. Linked issues will be added as links to the issue. Optionally add all or parts of the newly linked conversation to the Linear issue as a comment.

### View issue details⁠

From the Intercom conversation, you will see all linked issues in the sidebar along with the issue ID, status, and assignee.  Click the issue title from the Intercom sidebar to view more details. From here, you will also have the the option to view the issue in Linear or remove the link with the associated Linear issue.

### Link multiple issues ⁠

You can link multiple Intercom conversations to a single Linear issue. You can also link multiple Linear issues to a single conversation in Intercom.

## Re-open conversations⁠

In the integration settings page, you can automate the reopening of linked conversations when the associated issue is marked as completed, cancelled or a comment is made. The integration will post an internal note and re-open the conversation in Intercom so it's easy to follow up with customers. Both closed and snoozed conversations will be reopened.

![Intercom integration re-open conversations setting](https://webassets.linear.app/images/ornj730p/production/e959a66c93d9b6003aba0a3079defedb0d84ea3d-1446x502.png?w=1440&q=95&auto=format&dpr=2)

## Internal notes⁠

By default, Intercom posts an internal note when issues are created, cancelled, or completed. Optionally set the integration to post an internal note whenever the issue status is updated. This feature allows Intercom users to gain additional signal on the issue without context switching away from Intercom. Please note that internal notes left in Intercom do not sync to the associated Linear issue.

![Intercom integration internal notes setting](https://webassets.linear.app/images/ornj730p/production/24290a9f755f88502131461fe54f3be5ac2b13b4-1372x440.png?w=1440&q=95&auto=format&dpr=2)

## Link Intercom conversations in Linear issues⁠

- Click on contextual menu icon … to the top right of the issue
- Click Add link
- Click Intercom conversation

### Remove links⁠

Click Unlink from the Linear sidebar in Intercom to remove the link between the conversation and a Linear issue. You can also remove this from the Linear issue by right-clicking on the Intercom link attachment or clicking the … icon on the link attachment.

### Filter for Intercom links⁠

From any Linear view, you can filter by issues linked to Intercom issues. Click F, then select Links and then select Intercom.

[PreviousGong](https://linear.app/docs/gong)[NextJira](https://linear.app/docs/jira)# Front

Source: https://linear.app/docs/front

---

# Front

Our Front integration makes it easier for you and your team to keep track of bugs and feature requests and interact with the customers who report them.

![Linear and Front logos](https://webassets.linear.app/images/ornj730p/production/25379055474c939cc9ab698c30c0e748ad4d4264-2880x1620.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

The Front integration lets you create and link Linear issues from Front conversations. Linked issues, their status, and assignee show up in the sidebar in Front. Linked conversations will show up in Linear issues as link attachments. When issues close, we'll automatically re-open the Front conversation so you can get back to users with an update.



This integration is available on Linear's Business and Enterprise plans.

G then S to go to Settings > Workspace > Integrations > Front

Ctrl L (Mac) or Alt Ctrl L (Windows) to link from Linear issue

- Click the Avatar to go to to go to Settings > Workspace > Integrations > Front
- Select the more menu (three dots) after saving the Linear issue to link conversations from Linear

settings to go to Settings > Workspace > Integrations > Intercom

link to link Front conversations from Linear

## Configure⁠

There are three steps to installing the Front integration (you must do them in order):

- Install and approve Linear for your Front workspace by installing it from the Front integrations page. This will add the Linear widget to your Front application sidebar.
- Then go into Linear's settings and enable Front automation from the Front settings page.
- From the Front sidebar, click on the Linear widget. Sign into the account and select the workspace.

Front users are required to have a Linear account to use the integration and create and view issues in Front. We also recommend using the Front desktop application for a better experience.

## Basics⁠

### Create new issues⁠

You can create new Linear issues from Front conversations. When linked, Linear issue information is shown inside Front while viewing the related message. A link attachment for the Front message is also shown in the Linear issue.

When creating a new linear issue, you can choose a team in which to create the issue, provide a title, and then optionally provide a description, set issue priority, assignee, and labels.

![image](https://webassets.linear.app/images/ornj730p/production/c377a88c314fd6d0ceacf255f927c3220f1d9a07-16x16.svg?q=95&auto=format&dpr=2)

Get more out of the Front integration by enabling the Triage feature for your teams. Any issues created from Front will go to Triage when enabled (otherwise, the issues will be added to the first backlog status in your team).

### Link existing issues⁠

Search for a specific issue ID or words in the related title to link a relevant Linear issue to a Front conversation. This will add a Front link attachment to the Linear issue and gives you the option to add any image content as a comment on the issue. Front's issue search works the same way as our in-app Search.

### Link Front conversations in Linear issues⁠

- Click on contextual menu icon … to the top right of the issue
- Click Add link
- Click Front conversation

Front when in issue view, then select Link Front conversation to issue…



### ⁠

### Re-open conversations⁠

In the Front settings page in Linear, you can automate the reopening of the linked issue when it's completed, cancelled or a comment is made. The integration will post an internal note and re-open the conversation in Front so it's easy to follow up with customers.

### Link multiple issues⁠

Sometimes customers will write in with multiple requests at one time. You can link as many Front messages to a Linear issue as you like.

### Unlink issues⁠

Click Unlink from the Linear sidebar in Front to remove the link between the message and a Linear issue. You can also remove this from the Linear issue by right-clicking on the issue attachment.

### Merge duplicate reports⁠

It's common for support requests to relate to bugs or issues already filed in Linear. When you merge duplicate issues that have Front attachments, we'll move any Front attachments and comments over to the canonical issue and update the linked Front message so that it's connected to the canonical issue and automations work.

Click Unlink from the Linear sidebar in Front to remove the link between the conversation and the associated Linear issue. You can also remove this link from the Linear issue by right-clicking on the Front link attachment.

### Filter for Front links⁠

From any Linear view, you can filter by issues linked to Front conversations. Click F then select Links and then select Front.



## FAQ⁠

[](https://linear.app/docs/front#collapsible-9d482fded492)No, the only option is to send comments from Linear back as internal notes in Front when a comment is made, or an issue changes status. This is configurable in Linear settings > Integrations > Front

[](https://linear.app/docs/front#collapsible-05472ae39a39)Templates are not supported at this time in the Front integration.

[](https://linear.app/docs/front#collapsible-3d31b0c9d026)Conversations in private inboxes do not support automated comments or reopening.

[PreviousFigma](https://linear.app/docs/figma)[NextGitHub](https://linear.app/docs/github-integration)# Zendesk

Source: https://linear.app/docs/zendesk

---

# Zendesk

Our Zendesk integration makes it easier for you and your team to keep track of bugs and feature requests and interact with the customers who report them.

![Linear and Zendesk logos](https://webassets.linear.app/images/ornj730p/production/cc44cb21b341c3be70dda6c9a8ef1cf698f7dd8f-2880x1620.png?w=1440&q=95&auto=format&dpr=2)

## Overview ⁠

Our Zendesk integration lets you create Linear issues from Zendesk or link existing issues to your Zendesk tickets. When linked, Linear issue information is shown inside Zendesk and a link to Zendesk is added to your Linear issue. Automate updating Zendesk tickets when its related Linear issue has been closed (Done or Cancelled). Our integration will also re-open the ticket so that your agents will be able to notify the customers.

## Configure⁠

### Install⁠

There are two steps to installing the Zendesk integration:

- Install and approve Linear for your Zendesk workspace by installing it from Zendesk Marketplace. This will add the Linear widget to your Zendesk ticket sidebar.
- Enable Zendesk automation from Linear's Zendesk settings page. This will enable ticket re-opening and updates to your tickets. You must be a Zendesk admin to complete this step.

After you install the Linear add-on, it will show up in the right sidebar when viewing a ticket. Each agent will have to login to their Linear account from the application to create and view issues.

### Requirements⁠

Our integration requires that each Zendesk agent who installs Linear  also has a Linear account, since the linked issues will be created in their name. This also allows agents to open the Linear issue to update it or add more information. This integration is available on our Business and Enterprise plans.

## Basics⁠

### Create new issues⁠

Create a new issue from the Zendesk widget. It will bring up a form which requires a title and that you assign the issue to a team. Optionally add priority, assignee, or labels from within Zendesk.

When linked, Linear issue information is shown inside Zendesk while viewing the related ticket. This also adds a link to the Zendesk ticket from the Linear issue.

Optionally, toggle "include message" in the widget to add message content from the customer ticket to the Linear issue description, including images if applicable.

![image](https://webassets.linear.app/images/ornj730p/production/c377a88c314fd6d0ceacf255f927c3220f1d9a07-16x16.svg?q=95&auto=format&dpr=2)

Get more out of the Zendesk integration by enabling the Triage feature for your teams. Any issues created from Zendesk will go to Triage when enabled (otherwise, the issues will be added to the first backlog status in your team).

### Create with Linear Agent⁠

In addition to creating issues manually from a Zendesk ticket, you can use the Create with Linear Agent option to automatically create Linear issues using AI.

When selected, Linear analyzes the entire conversation, including customer messages, support replies, metadata, and any attachments, and identifies the underlying product request or bug. The Linear Agent generates an informed title and description while pulling in the relevant context from your conversation with the customer.

![Create a new Linear issue automatically with the Linear Agent](https://webassets.linear.app/images/ornj730p/production/06255674e4a80db8c543e292bbfae51d52af9b1b-865x610.png?w=1440&q=95&auto=format&dpr=2)

A customer request is created when applicable, and the issue is routed to the desired team for review and prioritization.

To use the Linear Agent in Zendesk, enable the integration in Settings > Integrations > Zendesk and turn on the option to allow AI-generated issues.

![Zendesk integration settings to enable the Linear Agent for automatic issue creation](https://webassets.linear.app/images/ornj730p/production/00ef4032be96abf042dac6f746985985b98c4d23-1470x430.png?w=1440&q=95&auto=format&dpr=2)

Optionally, you can also provide additional guidance to help route issues to the correct teams or templates. This guidance can include examples, team mentions, or internal rules the Linear Agent should follow when interpreting feedback.

### Use templates⁠

Linear admins can designate up to 5 templates to be available for quick use from within the Linear integration in Zendesk. Selecting any of these templates will pre-fill issue property fields appropriately, helping to speed up issue creation and maintain a high level of data hygiene in your issues.

### Link existing issues⁠

Search for issues by their issue ID or words in the title to link them. This will add a Zendesk link to the Linear issue. Zendesk's issue search works the same way as our in-app Search.

### Re-open conversations⁠

In the integration settings page, you can automate the reopening of the linked issue when it's completed, cancelled or a comment is made. The integration will post an internal note and re-open the conversation in Zendesk so it's easy to follow up with customers.

### Link multiple issues⁠

Sometimes customers will write in with multiple requests at one time. You can link as many Zendesk tickets to a Linear issue as you like.

### Link Zendesk tickets in Linear issues⁠

- Click on contextual menu icon … to the top right of the issue
- Click Add link
- Click Zendesk ticket

Front when in issue view, then select Link Zendesk ticket to issue…



### Unlink issues⁠

Click Unlink from the Linear widget to remove the link between the ticket and a Linear issue. You can also remove this from the Linear issue by right-clicking on the issue link.

### Merge duplicate reports⁠

It's common for support requests to relate to bugs or issues already filed in Linear. When you merge duplicate issues that have Zendesk links, we'll move any Zendesk links and comments over to the canonical issue and update the linked Zendesk ticket so that it's connected to the canonical issue and automations work.

Click Unlink from the Linear widget to remove the link between the ticket and a Linear issue. You can also remove this from the Linear issue by right-clicking on the issue link.

### Filter for Zendesk links⁠

From any Linear view, you can filter by issues linked to Zendesk tickets. Click F then select Links and then select Zendesk.

## FAQ⁠

[](https://linear.app/docs/zendesk#collapsible-914243845565)Check to make sure that you've enabled the Zendesk integration in your Linear workspace settings as well as in Zendesk's settings. The most common reason for this issue is that both steps of the installation process have not been followed.

[](https://linear.app/docs/zendesk#collapsible-51b6e9ffee4a)Yes, you can choose to add internal notes to your Zendesk ticket when comments or status changes are made in the original issue.

[](https://linear.app/docs/zendesk#collapsible-29f60f6f5062)Our Zendesk integration is not designed to accommodate updating the associated Zendesk domain. If you update your Zendesk URL, here's what you can expect:

- For tickets linked to Linear issues prior to the Zendesk domain change: the linked tickets will not show up in the Linear app in Zendesk.
- Some of the automations to post internal notes may still work.

If you'd like Linear to support updating your Zendesk domain, please let us know more about your use-case at support@linear.app.



[PreviousZapier](https://linear.app/docs/zapier)[NextIntegration Directory](https://linear.app/docs/integration-directory)# Salesforce

Source: https://linear.app/docs/salesforce

---

# Salesforce

Create or link to issues from cases. Linear's Salesforce integration is available as an add-on to our Enterprise plan.

![Linear x Salesforce cover image](https://webassets.linear.app/images/ornj730p/production/e54e48e34eec77b4dea1a1d51eda7e1bec5bdfcb-2880x1620.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Salesforce users—whether or not they use Linear—can link cases to existing issues and projects or create new issues using a Linear template.

Real-time updates ensure Salesforce users stay informed of issue/project status and priority changes as they happen, streamlining collaboration between teams.

## Configure⁠

### Contact us⁠

Please reach out to sales@linear.app to purchase licenses for this integration. Once purchased, assign them to Salesforce users to enable them to access the integration.

### Configure from Salesforce App Exchange⁠

- Install the Linear integration from the Salesforce Marketplace
- Find the Linear Development app in the Salesforce App Launcher. In order to see this app in the menu launcher, you must have been granted a licence to use this integration.
- Click Login with Linear
- Select the Linear workspace you want to connect
- Confirm the integration between Salesforce and Linear

### Configure from Linear⁠

- Navigate to Settings > Integrations > Salesforce
- Click Enable
- Copy the URL from any page in your Salesforce installation
- Paste the URL in the modal in Linear settings

### Enable the Linear component⁠

- Navigate to a case detail page (commonly in Service Cloud or Support Cloud)
- Edit the case detail page
- Find Linear in the list of custom components
- Place the component in the location of your choice on the page

### Linear x Salesforce integration configuration video⁠

Watch a video overview of how to set up the Salesforce integration.

## Permissions⁠

Three permission sets will become available in Salesforce:

## Settings⁠

### Restrict issue visibility⁠

Once enabled, only Linear issues that were created from or previously linked to Salesforce can be found when searching from the Linear component. This allows teams with privacy concerns to reduce the scope of visible issues in the Salesforce workspace.

### Internal notes⁠

Automatically notify your team in Salesforce when an issue linked to a case changes to any status. Changes will be added to the All updates section of a case.

### Automatic case reopening⁠

When the linked Linear issue is completed or canceled, you can automate reopening the case to the case status of your choice. This signals your team to follow up with customers.

Case statuses are customizable. If a new case status is added, visiting the Salesforce integration's page in Linear settings will reflect the addition.

### Templates⁠

Once a template has been created in Linear, click the + icon to make a template available to Salesforce.

### Mapping attributes from Salesforce to Linear⁠

When Customer Requests is enabled, creating issues from a Salesforce case will create new Customers in Linear as needed. The customer request added to the created issue contains the case description.

Customers support attributes you can use to group, order, and filter for data in Linear. For example, filter issues by the tier of the Customer who requested them, order projects by the associated sum of attributed customer revenue, and more. To bring this data into Linear from Salesforce, set the desired mapping between Salesforce account properties and Customer attributes in Linear in Settings > Customer Requests.

You can set mappings with any property you use on Salesforce accounts, as long as the data type is allowable:

If you're using lookup fields in Salesforce and wish to map to these in Linear, consider using formula fields as described in the FAQ.

## Using the integration⁠

### Create a new issue⁠

- From a case's details, click Create issue
- Select a template. All issues created by this integration use templates to drive consistency.
- Include a title
- Write a new issue description, or turn on the Include case description toggle to automatically insert the case description into the Linear issue description. The case description will appear in Linear as the Customer Request attached to the issue.

### Link cases to existing issues or projects⁠

- Click Link issue or project (depending on permission levels)
- Search for the issue or project and confirm

### Link to cases from Linear⁠

You can also link a Linear issue to a case by pasting the case's URL into the Linear issue as a link attachment with Control + L.

## Synced details⁠

### Status and priority⁠

When an issue is linked to a case, a reference to that issue appears in the Salesforce integration. The linked issue's status and priority are always current.

### User account attribution⁠

If a Salesforce user is also a Linear user, their name will be displayed as the issue creator in relevant issue activity sections. If the user does not have a Linear account, the issue creator displays as “User User” (the name of the Salesforce developer account) and the email of the Salesforce user who created or linked the issue.

### Customer information⁠

Linear syncs customer information from the Salesforce workspace. Modify attribute mapping as discussed in Mapping attributes above.

## Triage rules⁠

Using the Salesforce integration concurrently with Triage rules offers tools to direct how issues are routed after they're created from Salesforce. You can create rule conditions using properties of the Salesforce Case specifically, along with the normal set of filterable issue data in Linear. Triage rules can set an issue's team, status, assignee, label, project, and priority.

![a triage rule triggered by case origin and priority support](https://webassets.linear.app/images/ornj730p/production/7fee4c6a541d375ee392532d1bb0df893fcd9b49-1788x644.png?w=1440&q=95&auto=format&dpr=2)



## FAQ⁠

[](https://linear.app/docs/salesforce#collapsible-f15672f2632e)The case will reopen in Salesforce as the linked issue has been canceled. We do not merge Salesforce cases. If desired you may link the reopened case to the canonical issue and re-close the case.

[](https://linear.app/docs/salesforce#collapsible-3b039b499b47)Suppose in Salesforce you have a field called "account owner"; an owner ID with a lookup to the user email. This would not work by default in our attribute mapping, as the owner field in Linear requires an email address.

You can work around this by using a formula field. To do so, create a new custom field of type formula. Clicking into "Advanced Formula" will help you build the formula you need.

![new custom field of type formula in Salesforce](https://webassets.linear.app/images/ornj730p/production/5fbd8928154f911eee5dc3c339f314a85b5c822b-1198x822.png?w=1440&q=95&auto=format&dpr=2)

In this scenario, a formula field for account.owner returning an email address can be used to map between Linear's Customer owner and the necessary value in Salesforce.

[](https://linear.app/docs/salesforce#collapsible-6e54755d4723)Linear data living inside of Salesforce (like which customers have the most issues created from within Salesforce) can be queried directly with SOQL. This can be used to run analyses like returning issues linked to cases, or building custom dashboards within Salesforce.

[](https://linear.app/docs/salesforce#collapsible-6a71fba9a6f6)Yes, you can filter issues in views in Linear under the filter sub-menu Salesforce case properties. Salesforce properties are not supported in Insights or Dashboards.



[PreviousNotion](https://linear.app/docs/notion)[NextSentry](https://linear.app/docs/sentry)# Gong

Source: https://linear.app/docs/gong

---

# Gong

Automatically create issues from Gong call recordings.

Available to workspaces on our Enterprise plan

![Linear X Gong](https://webassets.linear.app/images/ornj730p/production/940ff2d3f160aeeb393baafb09b22edd78250cb3-2880x1620.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

The Gong integration automatically creates Linear issues from customer call recordings. Each issue includes a drafted title and description, speaker-attributed excerpts pulled directly from the transcript, and a link to the exact moment in the recording where the request or problem was raised.

Once enabled, Linear reviews new customer-facing calls and identifies meaningful product feedback without requiring anyone to listen to the recording. The integration captures what customers are asking for, adds the relevant context from the conversation, and sends the issue into your team’s Triage view for review. This keeps your workflow organized in Linear while leaving calls and transcripts in Gong.

## How it works⁠⁠

Linear periodically checks for new Gong recordings and processes new calls that meet specific criteria for analysis. Only customer-facing conversations are included, so internal or private calls and shorter recordings under 10 minutes are automatically skipped.

The system filters out items that aren’t actionable, like sales-related questions, beta access requests, general inquiries, or internal commentary.

Actionable findings that pass these filters are created as issues in Linear. Each issue includes a concise summary, customer motivation for the request, transcript excerpts with speaker attribution and a link directly to the timestamp in the recording for posterity.

Issues are added to your team’s Triage view, where they can be quickly reviewed, categorized, and moved into your existing backlog.

## Configure⁠

To set up the integration, navigate into your workspace-level Settings > Integrations and search for Gong. After enabling the Gong integration, navigate to your Gong settings, enable the recording intake and select the team that should receive Gong-generated issues:

![Recording intake settings section on, with a destination team chosen](https://webassets.linear.app/images/ornj730p/production/bc401ef7f3a78e59da4ba456851349d01d9834c4-1444x532.heif?w=1440&q=95&auto=format&dpr=2)

Optionally, you can also provide additional guidance to help route issues to the correct teams or templates. This guidance can include examples, team mentions, or internal rules the Linear Agent should follow when interpreting feedback.

## Customer requests⁠

When customer requests are enabled in your workspace, Gong is capable of creating customers just-in-time as their first request is added. If a customer already exists in Linear that matches the customer on the call, that customer will be re-used for association with the new customer request.

## FAQ⁠

[](https://linear.app/docs/gong#collapsible-0edba2c7b827)No, once an admin configures this integration it will run on all external calls without a seat for itself or other call participants.



[PreviousGoogle Sheets](https://linear.app/docs/google-sheets)[NextIntercom](https://linear.app/docs/intercom)# Google Sheets

Source: https://linear.app/docs/google-sheets

---

# Google Sheets

Use the Google Sheets integration to create custom analytics and dashboards for your company.

![Linear and Google Sheets logos](https://webassets.linear.app/images/ornj730p/production/e72a17743d75cacf18542c1c95122ca4bf4bc5da-2880x1620.png?w=1440&q=95&auto=format&dpr=2)

## Overview ⁠

The Google Sheets integration creates a Google Sheet for your workspace's issue data, project data, or both, allowing you to build out custom analytics among other uses. The data in these sheets refreshes hourly when changes have been made in your workspace.

All issues in public teams in a workspace will be shared to the issues sheet, and all projects belonging to at least one public team will sync to the projects sheet. We do not export data contained only in private teams.

There isn't a way to select what data is shared to the Google Sheet beyond configuring whether you wish to sync issues, projects, and/or initiatives.

## Configure⁠

Go to the Google Sheets integration settings and connect Linear to a Google account. This will automatically create a Google Sheet called Linear Issues in your Google Drive. Optionally, also choose to enable new sheets for projects and initiatives.

As this is a workspace setting, you can only connect one account per team. To share the data with teammates, update permissions directly on the sheet. If you're looking for a one-time download, workspace Admins can export a CSV instead.

## Synced data⁠

### Issues⁠

- ID
- Team
- Title
- Description
- Status
- Estimate
- Priority
- Project ID
- Project
- Creator
- Assignee
- Labels
- Cycle Number
- Cycle Name
- Cycle Start
- Cycle End
- Due Date
- Parent issue
- Initiatives
- Project Milestone ID
- Project Milestone
- SLA Status
- Roadmaps
- Created
- Updated
- Started
- Triaged
- Completed
- Canceled
- Archived

### Projects⁠

- ID
- Name
- URL
- Summary
- Description
- Status
- Priority
- Milestones
- Creator
- Lead
- Members
- Start Date (Start)
- Start Date (End)
- Target Date (Start)
- Target Date (End)
- Created At
- Started At
- Updated At
- Completed At
- Canceled At
- Archived At
- Teams
- Initiatives
- Health
- Latest Update
- Latest Update Date
- Customer Count
- Customer Revenue

### Initiatives⁠

- ID
- Parent ID
- Name
- URL
- Description
- Details
- Status
- Creator
- Owner
- Target Date (Start)
- Target Date (End)
- Created At
- Started At
- Updated At
- Completed At
- Archived At
- Teams
- Health
- Latest Update
- Latest Update Date

## Updating data⁠

The Sheets data refreshes every hour if there is an update to be made, otherwise it won't refresh.

To run an immediate update, Admins can open the Cmd/Ctrl + K menu and select Sync to Google Sheets action. Alternatively, go to the integration's page and click Update now.

You can rename the sheet or move it to shared drives without affecting the data or uploads.

Avoid updating cells in the source sheet as any changes will be overridden. If you want to run analytics, do so in a separate sheet.

## Custom project analytics⁠

By using the projects sheet, you have more flexibility to build custom analyses in support of planning decisions. You can see an example of a project prioritization analysis here.

## Custom issue analytics⁠

To build analytics from issue data, import or reference data from the sheet Linear created using IMPORTRANGE, VLOOKUP or similar functions.

Linear users have used the Google integration to build analytics that:

- Track velocity per team member.
- Combine with Linear's cycle statistics to get a deeper view into individual and team velocity.
- Track the types of work completed and planned. To do this, create custom labels and issue statuses in Linear. A common way to do this is to name labels with a prefix or key:value pair for easier filtering (e.g. comp: feature_name or type: feature/bug/etc.)
- Build a Gantt chart for planning or other charts and graphs to show issue progress over time.
- Track bugs more granularly. What percent of open issues are bugs? How many bugs were worked on in a cycle compared to features?
- Track time: Use the timestamp data to measure how long issues remain open or how long it takes an issue to go from start to completion.

For more advanced queries, consider using the API or Zapier.

## Timestamp FAQs⁠

- Multiple issue statuses can exist in a single category (e.g. In Progress and In Review fall under Started. The timestamp exported reflects the latest timestamp at which an issue was moved to that status category from another category -- not between statuses of the same category.
- Null fields on timestamps mean the issue or project was never in that status, or the timestamp was cleared (an issue moving from Backlog -> Done -> In Progress will clear the completed timestamp.)
- All times in this integration are displayed in GMT.

[PreviousGitLab](https://linear.app/docs/gitlab)[NextGong](https://linear.app/docs/gong)# Airbyte

Source: https://linear.app/docs/airbyte

---

# Airbyte

Available to workspaces on our Enterprise plan

Connect with Airbyte to consolidate data in data warehouses, lakes, and databases.

![Linear and Airbyte logos](https://webassets.linear.app/images/ornj730p/production/01f331e6f28947dc5304640abb8cf844ea0ff280-2880x1620.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

With the Airbyte integration you can load your Linear data into any data warehouse, lakes or databases in minutes. Create custom analytics and dashboards for your company and update it on any schedule through Airbyte.

We support Airbyte Open Source environments, and do not support Airbyte Cloud.

## Configure⁠

Configuration requires workspace admin permissions to navigate to Settings > Features > Integrations > Airbyte and click the Enable button.

Copy the one time Airbyte API key as you will need this later. With this key the integration receives read access to all data in supported tables. There is no way to exclude access to private team access at this time.

### Set up Airbyte locally⁠

Install Docker Desktop and launch it.

Clone the Airbyte repo and run Docker using the following command in Terminal:

```
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker-compose up
```

Now you can open Airbyte in your browser at http://localhost:8000.

### Set up Linear Source⁠

- In the Airbyte dashboard, click "Settings" on the bottom left.
- Click "Sources" on the left sidebar.
- Click the "New connector" button > enter the following: - Connector display name: Linear- Docker repository name: gcr.io/linear-public-registry/linear-airbyte-source- Docker image tag: latest- Connector Documentation URL: https://github.com/linear/linear-airbyte-source/blob/main/readme.md

![Settings page in Airbyte for adding a new connector](https://webassets.linear.app/images/ornj730p/production/411c6aec9ef601e16ae5a157da4dbbf1b133e114-804x719.png?w=1440&q=95&auto=format&dpr=2)

### Connect your destination⁠

With the connection complete, you can now choose your destination.

- Click "Connections" in the sidebar and the "New connection" button.
- In the "Source type" box search for "Linear".
- You can give a custom name to your source or leave it as Linear.
- Paste the API key you generated in the Linear integration page for Airbyte and click "Set up source".
- On the next page, you can select an existing destination or set up your destination service, their instructions will be provided there if you have not yet created a destination with them before.
- Save the connection.

![Airbyte settings page where you paste your API key ](https://webassets.linear.app/images/ornj730p/production/e55fd4eaa74ab6d7ba2f40af3ad9eb490e12721b-901x512.png?w=1440&q=95&auto=format&dpr=2)

### Choose your sync frequency⁠

Next, you need to choose how often you want to sync your Linear data to this destination:

- Click on Connections and your chosen Connection in the list
- Click on the "Replication" tab and choose your Replication frequency
- Select the data you want to sync. You should see a list of table names. You can select all or choose which ones to sync individually.
- Choose what type of sync mode you'd like to use for each source table. Full Refresh and Append are the options you can choose from. Incremental is not supported at this time. Linear data can sync every 12 hours, it cannot sync sooner than this.
- Click "Save changes"

Everything is now configured to extract, transform, load (ETL) your Linear data into Airbyte and sync it to the selected destination on the schedule you chose.

The following models will be synced:

- Organization
- Teams
- Team Key
- Team Membership
- User
- Milestone
- Project
- Project Updates
- Project Link
- Issues
- Issue History
- Issue Label
- Issue Relation
- Integration Resource
- Attachment
- Audit Entry
- Comment
- Cycle
- Workflow State
- Document
- documentContent

## Remove connection⁠

You can disable any incremental or full syncs by going to the Connection settings page and clicking Delete this connection.

## FAQ⁠

[](https://linear.app/docs/airbyte#collapsible-67ebc8e63aca)Airbyte Open Source is free to use, only the cloud version is paid — which we don’t currently support.

[](https://linear.app/docs/airbyte#collapsible-73d8f6b9de99)Airbyte offers many services you can connect your Linear workspace data to, you can view the full list here: https://docs.airbyte.com/integrations/



[PreviousTriage Intelligence](https://linear.app/docs/triage-intelligence)[NextAsks](https://linear.app/docs/linear-asks)# Asks

Source: https://linear.app/docs/linear-asks

---

# Asks

Asks turns requests like bug reports, questions, and IT needs into actionable issues in Linear.

Available to workspaces on our Business and Enterprise plans. Additional features available to Enterprise workspaces through Advanced Linear Asks.

![Linear logo and Asks logo](https://webassets.linear.app/images/ornj730p/production/cafe02ae27a254a6eda1dc00b00d91d063cd7656-2880x1620.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Linear Asks gives organizations a powerful tool to manage common workplace requests. Once enabled, anyone can create an Ask to send their request to the relevant Linear team—even if they don’t have a Linear account—via Slack or email.

### Purpose and use cases⁠

Linear Asks is purpose-built to support internal requests that are typically scattered across tools or lost in chat threads. It’s ideal for:

- Engineering teams receiving bug reports from non-technical staff
- IT and support teams fielding hardware, access, or setup questions
- Operations and HR gathering requests from across the company
- Product and design teams collecting feedback or feature requests

By providing familiar and low-friction channels, Asks allows teams to quickly make requests without context switching.

### Multi-channel request intake⁠

Linear Asks supports multiple intake channels to meet teams where they already work:

It’s important to note that Asks via email intake is not designed for high-volume, front-line customer support, therefore feature development does not reflect those found in other customer support tools—first response times, NPS scores, etc. As part of Linear's development, we will continue to evolve the feature for internal requests.

### Linear Asks vs Advanced Linear Asks⁠

Asks features are available in both Business and Enterprise plans, with additional features available to Enterprise workspaces as follows:

## Using Linear Asks with Slack⁠

### Configure Asks⁠

#### Install Asks⁠

- Navigate to Settings > Features > Asks
- Click the "+" icon under Slack intake to Connect Asks integration
- Authenticate into a Slack workspace

#### Connect teams and invite @Linear Asks⁠

- Click the three dots next to Private Asks or All public Slack channels.
- Hover over Add teams to channel
- Select the team to add to a private Ask or a public Slack channel. Repeat this process for each channel that will be used to create Asks. DMs do not need to be added as channels.
- Add Asks to each channel using /invite @Linear Asks in Slack

There are some Asks that you’ll want to keep private between the requester and the team managing the issue. Add these sensitive requests under the Private Asks section in Asks settings. Private Asks includes Asks in DMs or created in the Asks app home (Apps > Linear Asks in Slack's sidebar). Asks templates added to Private Asks are available when creating Asks in DMs.

Ensure that the Linear teams you connect to Private Asks are also private. This guarantees that only members of the desired Linear team will see content shared on that issue.

#### Per-channel configuration⁠

- Click Add channel button
- Select the correct Slack workspace
- Select the specific channel
- Click Allow
- Add Asks to each channel using /invite @Linear Asks in Slack

To set up Asks with a private channel, use a channel-specific configuration.

#### Add templates to channels⁠

If you wish to allow users to submit Asks without selecting a template, keep "Create Asks without a template" enabled.

Select available templates under each team. Workspace level templates are not available for use with Asks.

Asks templates added to Private Asks are available when creating Asks in DMs.

#### Enable auto-creation⁠

Configure automations in settings to allow Asks to be created automatically. Asks auto-creation is not supported in DMs.

Select a default template by hovering over the template you wish to use, and clicking "Set as default". This template will apply to auto-created Asks in the set context. The description of the template will not be used and will be replaced by the user's message. If you'd just like to select a default team, consider selecting a default of "Create Asks without a template."

By default, users can turn a message in Slack into an Ask by reacting to it with the 🎫  (:ticket:) emoji. This can be turned off for individual channels. Starting a Slack message with 🎫 will also trigger this behavior.

Bot-posted messages can create an ask on 🎫 if the bot's message's first character is 🎫.

If multiple Linear teams are associated with the channel or channel type in your Asks settings, the 🎫 emoji will create an issue in the team template marked "default."

For Slack channels meant solely for the creation of Asks, you can enable auto-creation whenever a new message is posted to the channel. This is common for channels such as #it-asks or #bugs, in which you want all messages to be triaged. This feature is available on Enterprise plans only as it requires a single-channel configuration.

To exempt a message from creating an Ask with this setting on, begin the message with 📢 or 📣 emojis.

Please note that this auto-creation on new messages is not available in private channels

If desired, Slack users can also create an ask by mentioning @Linear Asks in the body of their Slack message.

[](https://linear.app/docs/linear-asks#collapsible-b5ead03c69f6)![On bot mention selected in Asks settings](https://webassets.linear.app/images/ornj730p/production/71a682a280b322873fb4e08dc097d532a033917f-1634x576.png?w=1440&q=95&auto=format&dpr=2)



Bot-posted messages can create an Ask automatically if the bot's message begins with 🎫. Use this behavior when auto-create Asks "on 🎫  reaction" or "On new message" is enabled. On Business plans, you can still use this functionality to allow bot messages to create Asks, provided the bot message is sent in a public channel.

[](https://linear.app/docs/linear-asks#collapsible-098a354ddca3)![Settings showing Asks auto-create on new message turned on](https://webassets.linear.app/images/ornj730p/production/cf8decfafc05650050dccd5b26dae8af3b475a43-1666x426.png?w=1440&q=95&auto=format&dpr=2)



### Set permissions for managing Asks⁠

Linear admins can determine whether Asks channels, teams and templates can be managed by all users, or admins only.

![Allow members to manage Asks](https://webassets.linear.app/images/ornj730p/production/a39ecbd9a59ce94927a590c95f9950fb64430bdb-721x154.png?w=1440&q=95&auto=format&dpr=2)

### Customize templates⁠

When creating Asks from a template, the newly created issue will use the properties assigned to the template by default. Create or edit templates under Template settings for the relevant team. Workspace-level templates cannot be associated with Linear Asks.

There are a variety of formatting tools you can use to customize the behavior of a particular template. Form templates are particularly useful in combination with Asks. Learn more about template fields here.

If you set required form template fields on a default template for a channel, auto-creation options will not be available.

### Submit Asks in Slack⁠

From any connected Slack channel, use the following actions to create an Ask:

Once created, Asks will create a threaded reply with a link to the Ask and connected Linear issue. The Slack thread and Linear issue share a synced comment thread, so comments and files can be shared across both applications.

Whoever submits the Asks can see the issue status, assignee, and reply in the synced comment thread. They will be notified on the thread automatically when the Ask is completed, canceled, or re-opened.

Users with a Linear account will be able to make updates to Asks from Slack using the Quick Actions menu, including changing the status and assigning it to themselves.

### Manage your Asks from Slack⁠

View Asks

Navigate to the Linear Asks bot in Slack. See a list of all active and closed Asks in Linear Asks > Home tab. Click Open thread to go to the Ask in the channel it was created. You can also view Asks and their threads (including private Asks) in the Messages tab.

Mark as urgent

If your Ask is urgent, you can choose to override its default priority by selecting the Mark as urgent option in your Ask's unfurl menu. This will also apply a siren emoji to your Ask for better visibility in Slack.

See status and assignee

Asks app home will show the real-time status and assignee of your Ask. You'll also be notified in the original thread when your issue leaves Triage (all Asks start in Triage), and when it's completed, canceled, or reopened. In a shared channel using Asks, users from the other organization will not see Asks app home.

Reply and share files

Reply to the Slack thread to ask questions, follow up on the Ask, or even send files, screenshots, and video to the assignee working on your Ask. All replies are sent to the Linear issue on a synced comment thread.

Close Asks

You’ll get a notification on the thread whenever a comment is posted to the Ask and when the Ask is completed, canceled, or re-opened. When completed, the Ask message will also have a ✅ on the original Ask.

Requestors can close their own Asks in Slack from Linear Asks > Home by changing its status.

## Using Linear Asks with email⁠

### Permissions⁠

Admins can add new email, edit, or delete a custom intake email. Members can change settings related to the configured email (team/template/sync-reply/customer requests).

### Configure⁠

- Navigate to Settings > Asks
- Click the “+” icon for Add Asks intake email
- Select the Linear team and [optional] issue template that should be applied to incoming emails to this address.
- A unique forwarding email will be created.
- Configure email forwarding so emails sent to your custom email address are forwarded to the unique Linear email address.
- (Optional) If you want your replies to appear from your custom email address, upload the provided DNS records to your DNS hosting provider, or provide these records to an engineer on your team. If this step is skipped, the replies will still be delivered, but they will come from a Linear address (issues@linear.app) instead of your own.

### Configure email forwarding⁠

[](https://linear.app/docs/linear-asks#collapsible-b4ea4ff782b5)You will need administrator permissions to set up email forwarding in your Google Workspace.

We do not recommend using Google Groups to set up forwarding as it modifies email headers which can result in several downstream issues.

This approach is recommended because it does not require a separate Google account for the custom address and does not modify any email headers.

- Sign in to Google Admin console
- Open the side menu and click on Apps > Gmail
- Scroll to the bottom and select Routing
- Scroll to the bottom under Email forwarding using recipient address map.
- Click Add another rule
- Click Add
- Add your custom email address (e.g., helpdesk@acme.com) in the “Address” field
- Copy and paste your unique Linear intake email address in the “Map to address” field
- Under “Messages to affect”, ensure All incoming messages is selected
- Under “Routing”, check the box for Also route to original destination.
- Click Save

Refer to Google’s help documents in Forward email to a third-party CRM for more details.

[](https://linear.app/docs/linear-asks#collapsible-69aa249165b4)- Log into your Microsoft 365 Admin Center
- Select the mailbox that you wish to configure forwarding for:Shared mailbox: On the admin center homepage, go to the Teams & groups > Shared mailboxes page. Select the mailbox, then select Edit in the "Email forwarding" section.User: On the admin center homepage, go to the Users > Active users page. Select the user, then the mail tab and select Manage email forwarding in the "Email forwarding" section.
- On the "Shared mailbox" email forwarding side panel, select the "Forward all email sent to this mailbox" checkbox.
- Enter your Linear intake email address copied from Linear Email Asks Settings
- Select Save

Automatic forwarding needs to be enabled in your anti-spam outbound policy before trying to verify your forwarding setup. This is found in the Microsoft Defender portal.

Refer to Microsoft's help documents in Configure email forwarding in Microsoft 365.

[](https://linear.app/docs/linear-asks#collapsible-8cf8bd205a41)Refer to your providers routing/forwarding instructions.

### Configure the reply sender email address⁠

To have replies appear from your custom email address instead of the default Linear address (issues@linear.app), you'll need to update your DNS settings. Add the provided DNS records to your DNS hosting provider. Alternatively, share them with your engineering team for implementation.

Important: If you skip this step, replies will still be delivered, but they'll be sent from Linear’s default email (issues@linear.app) address rather than your own.

### Synced email thread⁠

![Synced email thread](https://webassets.linear.app/images/ornj730p/production/8483ed7271453dc3f42888a71803c886cb052dfa-1604x776.png?w=1440&q=95&auto=format&dpr=2)

When an issue is created from an email, a synced thread will appear in the Linear issue, allowing members in Linear to communicate with requesters directly.

- Any new email reply to the original email thread will appear as a comment in the synced thread within Linear
- Any new comment on the synced Linear thread will be sent out as a new email to the email thread

This keeps all context centralized in Linear while enabling seamless communication with non-Linear users.

### Customize auto-replies⁠

By default, new emails are sent by Asks when an issue is first created, and again when it's completed or canceled. Customize which messages are sent, and their copy in Settings > Asks > Email Intake > [Email address].

![Shows how to customize auto-replies](https://webassets.linear.app/images/ornj730p/production/6e08009215e8519086fc1c87cb7a9dc51b21a1f3-756x459.png?w=1440&q=95&auto=format&dpr=2)

### Enable customer requests⁠

Toggle this feature on to automatically link inbound emails with customers based on the sender’s email domain. Refer to customer requests feature for more details.

## FAQ⁠

[](https://linear.app/docs/linear-asks#collapsible-0d10347f2a4f)Yes! In a shared channel initiated by your organization, use Asks as you would in a public channel.

Users in the channel from external Slack workspaces can create issues in your Linear workspace by applying the 🎫 :ticket: emoji reaction or mentioning @Linear Asks if enabled in Asks settings. If you've enabled auto-creation on every new message in the channel, this will create issues from the messages of both internal and external users.

Entrypoints to Asks not mentioned above are unavailable to external users in a shared channel.

External users can also mark their Ask as urgent through the overflow menu in its unfurl.

[](https://linear.app/docs/linear-asks#collapsible-5889e05c149b)There is a limitation to the Slack integration where it will show up as a new person for every unique User via Linear response. There is not a way to fully get around some duplication in avatars.

[](https://linear.app/docs/linear-asks#collapsible-0129b5b68930)Yes, you can link an existing Slack thread to a Linear issue over our API. To do so, pass syncToCommentThread: true in the input to the attachmentLinkSlack mutation (documentation is available here.)

[](https://linear.app/docs/linear-asks#collapsible-f6e8db2d223c)If you start a DM with multiple users that includes Linear Asks as a recipient from the beginning, you'll be able to use Asks there. However, as Slack will not allow you to add a bot user to an ongoing multi-person DM, you cannot create an Ask from an ongoing conversation that did not have Linear Asks in it from the start.

On Enterprise Linear plans, you can workaround this if desired by converting the multi-person DM to a private channel. Then, adding a configuration for that channel in Linear's Asks settings will allow you to create Asks from that private channel.

[](https://linear.app/docs/linear-asks#collapsible-512c12b5f097)Yes, though some setup is required.

- Check which workspaces in your Grid the channel belongs to in Slack.
- Ensure that each of those workspaces is connected to Asks in Linear > Settings > Asks
- From that same Asks settings page, open each workspace and add the channel. Ensure that your auto-create settings are the same to ensure consistent behavior.

[](https://linear.app/docs/linear-asks#collapsible-8953739bc544)- If an Ask is associated with a private team, it will never unfurl in Slack
- Please ensure that "Enable unfurls and actions in Slack" is toggled on in Settings > Integrations > Asks if you wish to see Asks unfurls in Slack.

[](https://linear.app/docs/linear-asks#collapsible-ba8fdd5bde2f)You can use per-account Gmail forwarding, which requires no Google Workspace admin permissions. This requires you to have a dedicated Gmail user—costing money—and requires confirming access to the intake address where Gmail will send an email with an activation code to the intake address that you will need to input back into Gmail settings.

![Email forwarding from inbox settings](https://webassets.linear.app/images/ornj730p/production/599c4660688b67df4a584b70552bbaa3bb49d455-1147x452.png?w=1440&q=95&auto=format&dpr=2)



[](https://linear.app/docs/linear-asks#collapsible-9ea458add54e)When hitting the error

550 5.7.520 Access denied, Your organization does not allow external forwarding. Please contact your administrator for further assistance. AS(7555)

Microsoft 365 (Outlook) by default blocks automatic forwarding to external email addresses to prevent data exfiltration/phishing abuse, even if you set up an inbox rule to forward. You will need an admin to explicitly allow it in the Exchange or Defender policies.

Allow external forwarding as Exchange admin:

- Navigate to Microsoft 365 Admin Center
- Open the Exchange Admin Center (EAC)
- Navigate to Mail Flow → Remote Domains
- Edit the default (or relevant) remote domain (usually *)
- Set "Allow automatic forwarding" to "On"

Fix via Microsoft 365 Defender UI

- Go to https://security.microsoft.com/antispam
- Go to Email & Collaboration → Policies & Rules → Threat policies → Anti-spam policies
- Click into your Outbound spam filter policy (likely called “Default”).
- Scroll down to the "Automatic forwarding rules" section.
- Set it to "On – allow automatic forwarding"
- Save the policy.

[](https://linear.app/docs/linear-asks#collapsible-83eb2d7492cc)Double check your forwarding settings to ensure it is set up for the custom email address to be forwarded to the Linear intake email address.



[PreviousAirbyte](https://linear.app/docs/airbyte)[NextDiscord](https://linear.app/docs/discord)# Integration Directory

Source: https://linear.app/docs/integration-directory

---

# Integration Directory

Discover Linear add-ons or build your own

![Linear icon next to integration icon](https://webassets.linear.app/images/ornj730p/production/b29db83e0238c6adea3c3a6d86834734fe332f29-2880x1620.png?w=1440&q=95&auto=format&dpr=2)

## Overview⁠

Linear's Integration Directory features apps and add-ons created by the Linear team as well as external applications. Install these to improve your workflow and sync with your favorite tools. You can also build your own integrations and submit them to the directory.

## Basics⁠

### Linear crafted⁠

If you see an integration with a star badge on the icon, that means it was crafted by the Linear team. You can install them via the link in the directory or by going to Settings > Workspace > Integrations and then select the integration name.

For most integrations, you'll have to be a workspace admin to install them for your workspace. If you don't know who is an admin, go to Settings > Workspace > Members and filter for Admins.

### Third-party integrations⁠

The directory also features integrations built by other apps and third parties. We recommend doing your own research into the integration owner and permissions required before installing these integrations. You can find the creator's website and contact in the sidebar.

### Build your own⁠

Use Linear's API to build your own integration and submit it to the directory following the instructions below. We recommend building applications using OAuth and having a separate workspace for the application, which gives all admins access to the application (instead of only the application creator).

We'll accept integrations that we think are useful to the community and are built by formal companies. We generally do not accept scripts or apps built by hobbyists, but feel free to reach out to integrations@linear.app if you think it should be included. You can also ask questions and see what others are building in our Slack community's #api channel.

![Figma file screenshot of Linear integration template](https://webassets.linear.app/images/ornj730p/production/597944e28167f567525f4b602ad72c3db65a973d-1504x933.png?w=1440&q=95&auto=format&dpr=2)

### Submit your integration⁠

- Fill out this form. It includes a sample page to give you a sense of copy style and length.
- Submit assets to integrations@linear.app or include a link in the form. We've built a template in Figma to make this easy.
- Send any questions to integrations@linear.app

[PreviousZendesk](https://linear.app/docs/zendesk)[NextMCP server](https://linear.app/docs/mcp)