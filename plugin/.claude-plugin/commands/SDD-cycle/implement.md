---
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md
---

The user input can be provided directly by the agent or as a command argument - you **MUST** consider it before proceeding with the prompt (if not empty).

User input:

$ARGUMENTS

1. Run `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute.

2. Load and analyze the implementation context:
   - **REQUIRED**: Read tasks.md for the complete task list and execution plan
   - **REQUIRED**: Read plan.md for tech stack, architecture, and file structure
   - **IF EXISTS**: Read data-model.md for entities and relationships
   - **IF EXISTS**: Read contracts/ for API specifications and test requirements
   - **IF EXISTS**: Read research.md for technical decisions and constraints
   - **IF EXISTS**: Read quickstart.md for integration scenarios

3. Parse tasks.md structure and extract:
   - **Task phases**: Setup, Tests, Core, Integration, Polish
   - **Task dependencies**: Sequential vs parallel execution rules
   - **Task details**: ID, description, file paths, parallel markers [P]
   - **Execution flow**: Order and dependency requirements

4. Load coordination plan from prior analysis (if available):
   - **Check for analysis output**: Look for previous `/SDD-cycle:analyze` execution results or parallel execution plan
   - **Agent assignments**: Map tasks to optimal specialized agents (test-automator, backend-architect, frontend-developer, etc.)
   - **Stream coordination**: Identify which tasks can run in parallel vs sequential
   - **File conflict detection**: Note shared files that require coordination between agents
   - **Fallback**: If no coordination plan available, proceed with single-agent sequential execution

5. Execute implementation with intelligent parallelization:
   - **Phase-by-phase execution**: Complete each phase before moving to the next (PRESERVED)
   - **TDD approach**: Execute test tasks before their corresponding implementation tasks (PRESERVED)
   - **Intelligent agent dispatch**:
     - For parallel tasks [P] with different files: Launch specialized Task agents simultaneously
     - For sequential dependencies: Execute one agent at a time in dependency order
     - Use agent assignments from coordination plan (test-automator, backend-architect, etc.)
   - **Coordination management**:
     - Monitor shared file access across parallel streams
     - Implement coordination checkpoints for file conflicts
     - Synchronize agents at phase boundaries
   - **Validation checkpoints**: Verify each phase completion before proceeding (PRESERVED)

6. Implementation execution rules:
   - **Setup first**: Initialize project structure, dependencies, configuration
   - **Tests before code**: If you need to write tests for contracts, entities, and integration scenarios
   - **Core development**: Implement models, services, CLI commands, endpoints
   - **Integration work**: Database connections, middleware, logging, external services
   - **Polish and validation**: Unit tests, performance optimization, documentation

7. Progress tracking and error handling:
   - **Sequential tasks**: Report progress after each completed task (PRESERVED)
   - **Parallel agent coordination**:
     - Monitor progress across multiple Task agents simultaneously
     - Aggregate status reports from parallel streams
     - Track completion of coordination checkpoints
   - **Error handling strategy**:
     - Halt execution if any non-parallel task fails (PRESERVED)
     - For parallel tasks [P], continue with successful tasks, report failed ones (PRESERVED)
     - Handle agent coordination failures gracefully
     - Provide clear error messages with context for debugging (PRESERVED)
   - **Task completion tracking**:
     - Mark completed tasks as [X] in tasks.md (PRESERVED)
     - Update task status for both sequential and parallel execution
     - Synchronize task file updates across agents
   - Suggest next steps if implementation cannot proceed (PRESERVED)

8. Completion validation:
   - Verify all required tasks are completed
   - Check that implemented features match the original specification
   - Validate that tests pass and coverage meets requirements
   - Confirm the implementation follows the technical plan
   - Report final status with summary of completed work

Note: This command assumes a complete task breakdown exists in tasks.md. If tasks are incomplete or missing, suggest running `/SDD-cycle:tasks` first to regenerate the task list.
