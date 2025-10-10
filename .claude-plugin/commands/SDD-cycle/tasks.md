---
description: Generate an actionable, dependency-ordered tasks.md for the feature based on available design artifacts.
---

The user input to you can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

1. Run `.specify/scripts/bash/check-prerequisites.sh --json` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute.
2. Load and analyze available design documents:
   - Always read plan.md for tech stack and libraries
   - IF EXISTS: Read data-model.md for entities
   - IF EXISTS: Read contracts/ for API endpoints
   - IF EXISTS: Read research.md for technical decisions
   - IF EXISTS: Read quickstart.md for test scenarios

   Note: Not all projects have all documents. For example:
   - CLI tools might not have contracts/
   - Simple libraries might not need data-model.md
   - Generate tasks based on what's available

3. Generate tasks following the template:
   - Use `.specify/templates/tasks-template.md` as the base
   - Replace example tasks with actual tasks based on:
     - **Setup tasks**: Project init, dependencies, linting
     - **Test tasks [P]**: One per contract, one per integration scenario
     - **Core tasks**: One per entity, service, CLI command, endpoint
     - **Integration tasks**: DB connections, middleware, logging
     - **Polish tasks [P]**: Unit tests, performance, docs

4. Task generation rules:
   - Each contract file → contract test task marked [P]
   - Each entity in data-model → model creation task marked [P]
   - Each endpoint → implementation task (not parallel if shared files)
   - Each user story → integration test marked [P]
   - Different files = can be parallel [P]
   - Same file = sequential (no [P])

5. Order tasks by dependencies:
   - Setup before everything
   - Tests before implementation (TDD)
   - Models before services
   - Services before endpoints
   - Core before integration
   - Everything before polish

6. Include parallel execution examples:
   - Group [P] tasks that can run together
   - Show actual Task agent commands

7. Create FEATURE_DIR/tasks.md with:
   - Correct feature name from implementation plan
   - Numbered tasks (T001, T002, etc.)
   - Clear file paths for each task
   - Dependency notes
   - Parallel execution guidance

8. Create GitHub sub-issues (if parent issue detected):
   - Read spec.md to check for parent issue in **Input** field (format: "GitHub Issue #456:")
   - If parent issue found, create GitHub sub-issues using gh-sub-issue extension
   - Update tasks.md to replace T001 format with actual GitHub issue numbers
   - Each task becomes a sub-issue under the parent issue for full traceability

Context for task generation: $ARGUMENTS

The tasks.md should be immediately executable - each task must be specific enough that an LLM can complete it without additional context.

## GitHub Sub-Issues Integration

**ONLY execute this if step 8 detected a parent issue in spec.md**

### 1. Extract Parent Issue and Milestone Information

```bash
# Read spec.md to extract parent issue number
spec_file="$FEATURE_DIR/spec.md"
if [ -f "$spec_file" ] && grep -q "GitHub Issue #" "$spec_file"; then
  parent_issue=\`grep "GitHub Issue #" "$spec_file" | sed -E 's/.*GitHub Issue #([0-9]+).*/\1/'\`
  echo "📝 Parent Issue detected: #$parent_issue"
else
  echo "ℹ️ No parent issue detected, skipping GitHub sub-issues creation"
  exit 0
fi

# Use milestone if available (optional enhancement)
epic_file="$FEATURE_DIR/epic.md"
milestone_number=""
if [ -f "$epic_file" ]; then
  milestone_number=\`grep "^milestone:" "$epic_file" 2>/dev/null | awk '{print $2}'\`
  [ -n "$milestone_number" ] && [ "$milestone_number" != "null" ] && echo "📝 Using milestone: #$milestone_number"
fi
```

### 2. Check gh-sub-issue Extension

```bash
if gh extension list | grep -q "yahsan2/gh-sub-issue"; then
  use_subissues=true
  echo "✅ gh-sub-issue extension available"
else
  use_subissues=false
  echo "⚠️ gh-sub-issue not installed. Using fallback mode with regular issues."
fi
```

### 3. Parse Tasks from tasks.md

```bash
# Extract tasks from the generated tasks.md
tasks_file="$FEATURE_DIR/tasks.md"
temp_dir="/tmp/sdd-github-sync-$$"
mkdir -p "$temp_dir"

# Parse each task (format: - [ ] T001 [P] Task Description)
grep "^- \[ \] T[0-9]" "$tasks_file" | while IFS= read -r line; do
  # Extract task ID and description
  task_id=\`echo "$line" | grep -oE "T[0-9]+"\`
  task_desc=\`echo "$line" | sed -E 's/^- \[ \] T[0-9]+ *(\[P\] *)?//'\`

  # Create task body file
  task_body="$temp_dir/${task_id}-body.md"
  echo "# Task: $task_desc" > "$task_body"
  echo "" >> "$task_body"

  # Extract full task details from tasks.md
  awk "/^- \[ \] $task_id/,/^- \[ \] T[0-9]/" "$tasks_file" | head -n -1 >> "$task_body"

  # Record task for processing
  echo "$task_id:$task_desc:$task_body" >> "$temp_dir/tasks-list.txt"
done
```

### 4. Create Sub-Issues

```bash
# Count tasks to determine strategy
task_count=\`wc -l < "$temp_dir/tasks-list.txt"\`

if [ "$task_count" -lt 5 ]; then
  echo "📝 Creating $task_count sub-issues sequentially..."

  # Sequential creation for small batches
  while IFS=: read -r task_id task_desc task_body; do
    if [ "$use_subissues" = true ]; then
      issue_number=\`gh sub-issue create \
        --parent "$parent_issue" \
        --title "$task_desc" \
        --body-file "$task_body" \
        --label "task,sdd" \
        --json number -q .number\`
    else
      issue_number=\`gh issue create \
        --title "$task_desc" \
        --body-file "$task_body" \
        --label "task,sdd,parent:$parent_issue" \
        --json number -q .number\`
    fi

    echo "$task_id:$issue_number" >> "$temp_dir/mapping.txt"
    echo "✅ Created sub-issue #$issue_number for $task_id"
  done < "$temp_dir/tasks-list.txt"

else
  echo "📝 Creating $task_count sub-issues in parallel..."

  # For larger batches, process in parallel using Task agents
  # Split tasks into batches of 3-4
  split -l 4 "$temp_dir/tasks-list.txt" "$temp_dir/batch-"

  for batch_file in "$temp_dir"/batch-*; do
    # Use Task agent for parallel creation
    # Each agent processes 3-4 tasks and creates sub-issues
    # Implementation would use Task tool here
    echo "Processing batch: $batch_file"
  done
fi
```

### 5. Update tasks.md with GitHub Issue Numbers

```bash
# Update tasks.md to replace T001 format with actual GitHub issue numbers
while IFS=: read -r task_id issue_number; do
  # Replace T001 with actual issue number in tasks.md
  sed -i.bak "s/[[:<:]]T$task_id[[:>:]]/#$issue_number/g" "$tasks_file"
  echo "📝 Updated $task_id → #$issue_number in tasks.md"
done < "$temp_dir/mapping.txt"

# Clean up backup file
rm "${tasks_file}.bak"

# Clean up temp directory
rm -rf "$temp_dir"

echo "✅ GitHub sub-issues created and tasks.md updated with issue numbers"
echo "🔗 Parent Issue: https://github.com/\`gh repo view --json nameWithOwner -q .nameWithOwner\`/issues/$parent_issue"
if [ -n "$milestone_number" ]; then
  milestone_url=\`grep "^milestone_url:" "$epic_file" | cut -d' ' -f2\`
  echo "🎯 Milestone: #$milestone_number - $milestone_url"
fi
echo ""
echo "🚀 Next Step: Execute implementation tasks"
echo "Run: /SDD-cycle:implement"
echo ""
echo "This unified SDD command will:"
echo "  - Execute tasks with intelligent parallelization"
echo "  - Launch specialized Task agents based on coordination plan"
echo "  - Follow TDD methodology with enhanced coordination"
echo "  - Provide distributed progress tracking"
```
