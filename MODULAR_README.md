# Kyros Dashboard - Modular Tools Architecture

## Overview

This document outlines the modular tools architecture implementation for the Kyros Dashboard. The goal is to transform the current monolithic structure into a pluggable, modular system where each tool (like the Content Repurposer) is self-contained and can be easily added, removed, or modified.

## Architecture Goals

- **Modularity**: Each tool lives in its own directory with backend and frontend components
- **Pluggability**: Tools can be enabled/disabled via configuration
- **Scalability**: Easy addition of new tools without modifying core code
- **Maintainability**: Clear separation of concerns between tools and shared services
- **Backwards Compatibility**: Existing API endpoints continue to work during transition

## Directory Structure

```
backend/
├── core/                    # Shared services (auth, storage, OpenAI wrapper, logging)
├── tools/                   # Individual tool modules
│   ├── repurposer/         # Content repurposing tool
│   │   ├── router.py       # FastAPI routes
│   │   ├── generator.py    # LLM wrapper + prompt logic
│   │   ├── schemas.py      # Pydantic models
│   │   ├── tasks.py        # Background tasks
│   │   └── tests/          # Unit tests
│   └── hello/              # Demo tool
└── tools_registry.py       # Tool discovery and registration

ui/src/
├── core/                   # Shared frontend services
├── tools/                  # Individual tool UI components
│   ├── repurposer/        # Repurposer UI components
│   └── hello/             # Demo tool UI
├── toolRegistry.js        # Frontend tool registry
└── components/
    └── ToolLoader.jsx     # Dynamic tool loading component
```

## Implementation Phases

### Phase 0: Prep & Branch Management ✅
- [x] Create `feature/modular-tools` branch
- [x] Add this documentation

### Phase 1: Backend Repurposer Extraction
- [ ] Create `backend/tools/repurposer/` structure
- [ ] Move generator logic from `api/generator.py`
- [ ] Create tool-specific router and schemas
- [ ] Maintain backwards compatibility
- [ ] Add unit tests

### Phase 2: Tools Registry & Dynamic Registration
- [ ] Create `backend/tools/registry.py`
- [ ] Implement dynamic router loading
- [ ] Add `/api/tools` meta endpoint
- [ ] Update main app to use registry

### Phase 3: Frontend ToolLoader & Repurposer UI
- [ ] Create `src/tools/repurposer/` structure
- [ ] Move Studio UI to RepurposerPanel
- [ ] Implement ToolLoader component
- [ ] Create tool registry system
- [ ] Update routing to use dynamic loading

### Phase 4: Core Services Extraction
- [ ] Move shared utilities to `backend/core/`
- [ ] Create OpenAI client wrapper
- [ ] Standardize logging and error handling
- [ ] Update tools to use core services

### Phase 5: Multi-tool Demo
- [ ] Add Hello World tool as proof of concept
- [ ] Demonstrate dynamic tool loading
- [ ] Test tool isolation

### Phase 6: Tests & CI Updates
- [ ] Add comprehensive test coverage
- [ ] Update CI/CD pipelines
- [ ] Add integration tests

### Phase 7: Feature Flags & Per-client Toggles (Optional)
- [ ] Implement client-specific tool enablement
- [ ] Add admin controls for tool management
- [ ] Database schema for tool permissions

## Key Benefits

1. **Faster Development**: New tools can be added without touching existing code
2. **Better Testing**: Each tool can be tested in isolation
3. **Easier Maintenance**: Clear boundaries between different functionalities
4. **Client Customization**: Tools can be enabled/disabled per client
5. **Team Scalability**: Different teams can work on different tools independently

## Migration Strategy

- Maintain backwards compatibility during transition
- Use feature flags to gradually roll out new architecture
- Keep existing API endpoints working
- Deploy incrementally with small PRs per phase

## Development Guidelines

### Adding a New Tool

1. Create `backend/tools/{tool_name}/` directory
2. Implement required files: `router.py`, `generator.py`, `schemas.py`
3. Add tool to `backend/tools/registry.py`
4. Create `ui/src/tools/{tool_name}/` directory
5. Implement UI components and add to `toolRegistry.js`
6. Add tests and documentation

### Tool Interface Requirements

Each tool must implement:
- **Backend**: Router with standard endpoints, generator logic, schemas
- **Frontend**: Panel component with consistent interface
- **Metadata**: Tool name, description, and configuration options

## References

- Original Cursor Task: Modular Tools Architecture Implementation
- Branch: `feature/modular-tools`
- Related PRs: See individual phase branches

---

*This document will be updated as the implementation progresses through each phase.*
