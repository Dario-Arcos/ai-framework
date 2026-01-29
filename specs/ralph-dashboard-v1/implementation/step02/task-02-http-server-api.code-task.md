## Status: COMPLETED
## Completed: 2026-01-29

# Task: HTTP Server + API Endpoint

## Description
Create a minimal HTTP server using Node.js native http module. Implement `/api/status` endpoint that aggregates data from all file readers into a single JSON response.

## Background
The dashboard uses a simple polling architecture. The browser fetches `/api/status` every 2 seconds. The server reads the ralph loop files and returns a consolidated response.

Port 3456 was chosen arbitrarily to avoid conflicts with common dev ports (3000, 8000, 8080).

## Reference Documentation
**Required:**
- Design: specs/ralph-dashboard-v1/design/detailed-design.md (API Design section)

**Additional References:**
- Task 01: specs/ralph-dashboard-v1/implementation/step01/ (reader functions)

**Note:** You MUST read the detailed design before implementing.

## Technical Requirements

1. Server listens on port 3456
2. GET `/api/status` returns JSON with structure:
   ```json
   {
     "status": { ... },
     "metrics": { ... },
     "recentLogs": [ ... ],
     "active": true/false,
     "lastUpdate": "ISO timestamp"
   }
   ```
3. When files missing: `{ "active": false, "error": "No loop running" }`
4. GET `/` returns 200 (HTML placeholder for now)
5. CORS headers for local development
6. Graceful error handling for malformed files

## Dependencies

- **Task 01 Complete**: Reader functions must be available
- **No external dependencies**: Use Node.js http module

## Implementation Approach

1. Create `server.js` in dashboard/
2. Import reader functions from lib/readers.js
3. Create HTTP server with request routing
4. Implement `/api/status` handler that calls all readers
5. Add error handling for file read failures
6. Write integration tests

**Note:** This is suggested approach. Alternative solutions are acceptable if they meet requirements.

## Acceptance Criteria

1. **Server Starts**
   - Given dashboard/ directory exists
   - When `npm start` is run
   - Then server logs "Dashboard running on http://localhost:3456"

2. **API Returns Status**
   - Given status.json and metrics.json exist
   - When GET /api/status is called
   - Then response is JSON with status, metrics, recentLogs, active:true

3. **API Handles Missing Files**
   - Given no ralph loop files exist
   - When GET /api/status is called
   - Then response is `{ "active": false, "error": "No loop running" }`

4. **Root Returns 200**
   - Given server is running
   - When GET / is called
   - Then response status is 200

5. **CORS Headers Present**
   - Given any API request
   - When response is received
   - Then Access-Control-Allow-Origin header is present

6. **Integration Test Passes**
   - Given test server starts
   - When test suite runs
   - Then API endpoint tests pass

## Metadata
- **Complexity**: Low
- **Estimated Effort**: S
- **Labels**: server, api, http
- **Required Skills**: Node.js http, JSON
- **Related Tasks**: Depends on Task 01, Task 03 depends on this
- **Step**: 02 of 04
