## Status: COMPLETED
## Completed: 2026-01-29

# Task: Project Setup + File Readers

## Description
Create the dashboard project structure and implement file reading functions for status.json, metrics.json, and iteration.log. These readers are the foundation for the API layer.

## Background
The ralph loop generates three files that the dashboard needs to read:
- `status.json` - Current loop state (iteration, status, failures)
- `logs/metrics.json` - Accumulated metrics (total iterations, success rate)
- `logs/iteration.log` - Text log of recent activity

All readers must handle missing files gracefully since the loop may not be running.

## Reference Documentation
**Required:**
- Design: specs/ralph-dashboard-v1/design/detailed-design.md

**Additional References:**
- Research: specs/ralph-dashboard-v1/research/file-formats.md
- Loop source: loop.sh (lines 146-160 for status.json structure)

**Note:** You MUST read the detailed design before implementing.

## Technical Requirements

1. Create `dashboard/` directory in project root
2. Create `package.json` with `start` script (`node server.js`)
3. Implement `readStatusFile()` that returns parsed JSON or null
4. Implement `readMetricsFile()` that returns parsed JSON or null
5. Implement `readRecentLogs(n)` that returns last n lines as array
6. All readers must use try/catch for file operations
7. All readers must be exported for testing

## Dependencies

- **Node.js 18+**: Required for native fs.promises
- **No external dependencies**: Use only Node.js stdlib

## Implementation Approach

1. Create directory structure: `dashboard/`, `dashboard/__tests__/`
2. Create minimal package.json with scripts
3. Create `lib/readers.js` with the three reader functions
4. Write unit tests first (TDD approach)
5. Implement readers to make tests pass

**Note:** This is suggested approach. Alternative solutions are acceptable if they meet requirements.

## Acceptance Criteria

1. **Directory Structure**
   - Given a fresh project
   - When I run `ls dashboard/`
   - Then I see `package.json`, `lib/`, `__tests__/`

2. **readStatusFile - File Missing**
   - Given status.json does not exist
   - When readStatusFile() is called
   - Then it returns null without throwing

3. **readStatusFile - File Exists**
   - Given status.json contains valid JSON
   - When readStatusFile() is called
   - Then it returns parsed object with current_iteration, status, etc.

4. **readMetricsFile - File Missing**
   - Given logs/metrics.json does not exist
   - When readMetricsFile() is called
   - Then it returns null without throwing

5. **readRecentLogs - Returns Last N**
   - Given logs/iteration.log has 20 lines
   - When readRecentLogs(5) is called
   - Then it returns array of 5 most recent lines

6. **Unit Tests Pass**
   - Given test files in __tests__/
   - When `npm test` is run
   - Then all reader tests pass

## Metadata
- **Complexity**: Low
- **Estimated Effort**: S
- **Labels**: setup, foundation, tdd
- **Required Skills**: Node.js, filesystem, testing
- **Related Tasks**: Task 02 depends on this
- **Step**: 01 of 04
