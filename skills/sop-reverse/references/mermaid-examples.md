# Mermaid Diagram Examples

Use mermaid for visual documentation throughout the investigation.

## Flowcharts

For process flows and decision trees:

```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```

## Architecture Diagrams

For system components and layers:

```mermaid
graph LR
    subgraph Frontend
        Client[Web Client]
        Mobile[Mobile App]
    end
    subgraph Backend
        API[API Server]
        Worker[Background Jobs]
    end
    subgraph Data
        Database[(PostgreSQL)]
        Cache[(Redis)]
    end
    Client --> API
    Mobile --> API
    API --> Database
    API --> Cache
    Worker --> Database
```

## Sequence Diagrams

For API interactions and process steps:

```mermaid
sequenceDiagram
    participant U as User
    participant A as API
    participant D as Database
    participant C as Cache

    U->>A: Request
    A->>C: Check cache
    alt Cache hit
        C-->>A: Cached data
    else Cache miss
        A->>D: Query
        D-->>A: Results
        A->>C: Store in cache
    end
    A-->>U: Response
```

## Entity Relationship Diagrams

For data models and relationships:

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    USER {
        int id PK
        string email
        string name
    }
    ORDER ||--|{ ITEM : contains
    ORDER {
        int id PK
        int user_id FK
        datetime created
    }
    ITEM {
        int id PK
        int order_id FK
        string product
        decimal price
    }
```

## State Diagrams

For process states and transitions:

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Review: Submit
    Review --> Approved: Accept
    Review --> Draft: Reject
    Approved --> Published: Publish
    Published --> [*]
```

## Class Diagrams

For component relationships:

```mermaid
classDiagram
    class Service {
        +start()
        +stop()
        +healthCheck()
    }
    class APIService {
        +handleRequest()
        +validateInput()
    }
    class DatabaseService {
        +connect()
        +query()
    }
    Service <|-- APIService
    Service <|-- DatabaseService
    APIService --> DatabaseService: uses
```

## When to Use Each Type

| Diagram | Use Case |
|---------|----------|
| Flowchart | Process flows, decision trees, workflows |
| Architecture | System components, service topology, layers |
| Sequence | API calls, interaction flows, step-by-step processes |
| ER | Data models, database schemas, entity relationships |
| State | Lifecycle states, status transitions |
| Class | Component structure, inheritance, dependencies |
