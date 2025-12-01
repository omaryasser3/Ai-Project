# AI-Powered Adaptive Program Repair System - Methodology & Architecture

## Overview

This document describes the main methodology and architectural design patterns used in developing the Adaptive Program Repair System. The system leverages Large Language Models (LLMs) orchestrated through a multi-agent architecture to automatically analyze and repair buggy code across multiple programming languages.

---

## Core Methodology

### 1. Multi-Agent Architecture

The system employs a **Multi-Agent System (MAS)** design pattern where specialized AI agents handle specific repair tasks. This approach enables:

- **Separation of Concerns**: Each agent focuses on a specific type of bug
- **Scalability**: New agent types can be added without modifying existing logic
- **Modularity**: Agents can be tested and improved independently

```mermaid
classDiagram
    class BaseAgent {
        +model_name: str
        +temperature: float
        +repair(code, issue, language) RepairResult
    }
    
    class MainAgent {
        +analyze_and_plan(code, src_language) tuple~List~Issue~, RepairPlan~
        +analyze_code(code, src_language) List~Issue~
        +create_specialized_agents(issues) List~BaseAgent~
    }
    
    class SyntaxAgent {
        +repair(code, issue, language) RepairResult
    }
    
    class LogicAgent {
        +repair(code, issue, language) RepairResult
    }
    
    class OptimizationAgent {
        +repair(code, issue, language) RepairResult
    }
    
    BaseAgent <|-- MainAgent
    BaseAgent <|-- SyntaxAgent
    BaseAgent <|-- LogicAgent
    BaseAgent <|-- OptimizationAgent
    
    MainAgent --> SyntaxAgent : creates
    MainAgent --> LogicAgent : creates
    MainAgent --> OptimizationAgent : creates
```

#### Key Data Structures

The system uses the following core data structures for communication between agents:

| Data Structure | Description |
|----------------|-------------|
| `Issue` | Represents a detected problem with id, type, description, and location hint |
| `RepairPlan` | High-level plan with translation decision (`translate`, `target_language`, `detected_language`, `language_match`) |
| `RepairResult` | Result from agent repair containing `fixed_code` and `explanation` |

### 2. Graph-Based Workflow Orchestration (LangGraph)

The system uses **LangGraph** to implement a state machine pattern for workflow orchestration. This provides:

- **Declarative Workflow Definition**: Clear visualization of the repair pipeline
- **Dynamic Routing**: Conditional edges enable adaptive processing paths
- **State Management**: Centralized state tracks code, issues, and repairs through the pipeline

```mermaid
stateDiagram-v2
    [*] --> main_node: Entry Point
    
    main_node --> dispatcher: Analyze & Plan
    
    dispatcher --> translator_forward: If translation needed (start)
    dispatcher --> syntax_fixer: If syntax errors
    dispatcher --> logic_fixer: If logic bugs
    dispatcher --> optimization_fixer: If performance issues
    dispatcher --> translator_backward: After repairs (if translated)
    dispatcher --> [*]: Queue empty (END)
    
    translator_forward --> dispatcher: Loop back
    syntax_fixer --> dispatcher: Loop back
    logic_fixer --> dispatcher: Loop back
    optimization_fixer --> dispatcher: Loop back
    translator_backward --> dispatcher: Loop back
    
    note right of dispatcher: Dynamic routing based on agent_queue
```

### 3. Adaptive Translation Strategy

A unique feature is the **cross-language repair** capability. The MainAgent can decide to translate code to a different programming language if:

- The target language has better LLM repair support
- The bug pattern is easier to analyze in another language

```mermaid
flowchart TD
    A[Input Code] --> B{MainAgent Analysis}
    B --> C{Should Translate?}
    C -->|Yes| D[Forward Translation]
    C -->|No| E[Repair in Original Language]
    D --> F[Repair in Target Language]
    F --> G[Backward Translation]
    G --> H[Output Fixed Code]
    E --> H
```

---

## System Architecture

### High-Level Architecture

```mermaid
flowchart TB
    subgraph UI["Web Interface Layer"]
        UI_WEB[Flask Web App]
        UI_STATIC[Static Assets]
        UI_TEMPLATES[HTML Templates]
    end
    
    subgraph API["API Layer"]
        API_ANALYZE["/api/analyze"]
        API_REPAIR["/api/repair"]
    end
    
    subgraph CORE["Core Processing Layer"]
        MAIN[MainAgent]
        GRAPH[LangGraph Workflow]
        AGENTS[Specialized Agents]
    end
    
    subgraph LLM["LLM Integration Layer"]
        GEMINI[Google Gemini API]
        CONFIG[config.yaml]
    end
    
    subgraph DATA["Data Layer"]
        BUGS[bugs.json]
        LOGS[Experiment Logs]
        TESTCASES[Test Cases]
    end
    
    UI_WEB --> API_ANALYZE
    UI_WEB --> API_REPAIR
    API_ANALYZE --> MAIN
    API_REPAIR --> GRAPH
    GRAPH --> MAIN
    GRAPH --> AGENTS
    MAIN --> GEMINI
    AGENTS --> GEMINI
    GEMINI --> CONFIG
    GRAPH --> LOGS
    MAIN --> BUGS
```

### Detailed Component Architecture

```mermaid
flowchart LR
    subgraph Input
        CODE[Buggy Code]
        LANG[Source Language]
    end
    
    subgraph MainNode["Main Analysis Node"]
        ANALYZE[Analyze Code]
        PLAN[Create Repair Plan]
        QUEUE[Build Agent Queue]
    end
    
    subgraph Dispatcher
        ROUTE[Route to Next Agent]
        CHECK{Queue Empty?}
    end
    
    subgraph Agents["Specialized Agents"]
        TRANS_FWD[Translator Forward]
        SYNTAX[Syntax Fixer]
        LOGIC[Logic Fixer]
        OPTIM[Optimization Fixer]
        TRANS_BWD[Translator Backward]
    end
    
    subgraph Output
        FIXED[Fixed Code]
        EXPLAIN[Explanations]
    end
    
    CODE --> ANALYZE
    LANG --> ANALYZE
    ANALYZE --> PLAN
    PLAN --> QUEUE
    QUEUE --> ROUTE
    
    ROUTE --> TRANS_FWD
    ROUTE --> SYNTAX
    ROUTE --> LOGIC
    ROUTE --> OPTIM
    ROUTE --> TRANS_BWD
    
    TRANS_FWD --> CHECK
    SYNTAX --> CHECK
    LOGIC --> CHECK
    OPTIM --> CHECK
    TRANS_BWD --> CHECK
    
    CHECK -->|No| ROUTE
    CHECK -->|Yes| FIXED
    CHECK -->|Yes| EXPLAIN
```

---

## Data Flow Sequence

```mermaid
sequenceDiagram
    participant User
    participant Flask as Flask App
    participant Main as MainAgent
    participant Graph as LangGraph
    participant Dispatch as Dispatcher
    participant Agent as Specialized Agent
    participant LLM as Gemini LLM
    
    User->>Flask: POST /api/repair (code, language)
    Flask->>Graph: invoke(initial_state)
    Graph->>Main: main_node(state)
    Main->>LLM: analyze_and_plan()
    LLM-->>Main: issues, plan
    Main-->>Graph: updated state (issues, queue)
    
    loop For each agent in queue
        Graph->>Dispatch: dispatcher_node_logic(state)
        Dispatch-->>Graph: next agent to run
        Graph->>Agent: agent_node(state)
        Agent->>LLM: repair(code, issue)
        LLM-->>Agent: fixed_code, explanation
        Agent-->>Graph: updated state
    end
    
    Graph-->>Flask: final state
    Flask-->>User: JSON response (fixed_code, repairs)
```

---

## Key Design Patterns

### 1. State Machine Pattern

The LangGraph implementation uses a state machine where:
- **States**: Represented by `GraphState` TypedDict
- **Transitions**: Defined by edges between nodes
- **Conditions**: Handled by `route_dispatcher` function

### 2. Factory Pattern

The `MainAgent.create_specialized_agents()` method acts as a factory, creating appropriate agent instances based on detected issue types.

### 3. Chain of Responsibility

Issues flow through a chain of specialized agents, each handling its specific concern and passing the updated code to the next.

### 4. Observer Pattern (Logging)

The `log_experiment()` utility captures all API interactions for analysis and debugging.

---

## Issue Classification

The following diagram shows an example distribution of issue types that the system is designed to handle:

```mermaid
pie showData
    title Issue Types Handled (Example Distribution)
    "Syntax Errors" : 25
    "Logic Bugs" : 40
    "Performance Issues" : 20
    "Style Issues" : 15
```

The system categorizes bugs into four main types:

| Issue Type | Handler | Description |
|------------|---------|-------------|
| `syntax_error` | SyntaxAgent | Parsing errors, missing tokens, indentation |
| `logic_bug` | LogicAgent | Wrong conditions, off-by-one, incorrect algorithms |
| `performance_issue` | OptimizationAgent | Slow code, suboptimal complexity |
| `style_issue` | LogicAgent | Generic issues handled by LogicAgent |

---

## Technology Stack

```mermaid
mindmap
    root((Adaptive Repair System))
        AI/ML
            Google Gemini API
            LangGraph
            LangChain
        Backend
            Python 3.x
            Flask
        Frontend
            HTML5
            Bootstrap 5
            JavaScript ES6+
        Data
            JSON
            YAML Configuration
```

---

## Deployment Architecture

```mermaid
flowchart TB
    subgraph Client
        BROWSER[Web Browser]
    end
    
    subgraph Server["Flask Server"]
        APP[app.py]
        STATIC[Static Files]
        TEMPLATES[Templates]
    end
    
    subgraph External["External Services"]
        GEMINI[Google Gemini API]
    end
    
    subgraph Storage["Local Storage"]
        CONFIG[config.yaml]
        DATA[bugs.json]
        LOGS[logs/]
    end
    
    BROWSER <-->|HTTP| APP
    APP --> STATIC
    APP --> TEMPLATES
    APP <-->|HTTPS| GEMINI
    APP --> CONFIG
    APP --> DATA
    APP --> LOGS
```

---

## Summary

The Adaptive Program Repair System represents a modern approach to automated bug fixing by combining:

1. **Multi-Agent Architecture**: Specialized agents for different bug types
2. **Graph-Based Orchestration**: LangGraph for flexible, maintainable workflows
3. **Adaptive Translation**: Cross-language repair capabilities
4. **LLM Integration**: Leveraging Google Gemini for intelligent analysis and repair

This architecture enables the system to handle diverse programming languages and bug types while maintaining clean separation of concerns and extensibility for future enhancements.
