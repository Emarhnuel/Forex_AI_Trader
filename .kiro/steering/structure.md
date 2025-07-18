# Project Structure

## Root Level Organization
```
├── .kiro/                          # Kiro IDE configuration and specs
├── gemini-fullstack-langgraph-quickstart-main/  # Frontend reference project
├── src/forex_ai_agent/             # CrewAI forex trading system (base)
├── knowledge/                      # User preferences and context
├── tests/                          # Test files
├── pyproject.toml                  # Root Python project config
└── README.md                       # Main project documentation
```

## CrewAI Base Structure
```
src/forex_ai_agent/
├── config/                         # YAML configuration files
│   ├── agents.yaml                 # Agent definitions (roles, goals)
│   └── tasks.yaml                  # Task definitions
├── tools/                          # Custom tools for agents
├── crew.py                         # Main crew orchestration logic
├── main.py                         # Entry point with CLI handlers
└── __init__.py
```

## Multimodal Trading Assistant Structure
```
multimodal-trading-assistant/
├── backend/                        # FastAPI + CrewAI backend
│   ├── src/
│   │   ├── agents/                 # CrewAI agent definitions
│   │   │   ├── chart_analyst.py    # Video analysis agent
│   │   │   ├── data_agent.py       # Market data agent
│   │   │   └── strategy_agent.py   # Strategy formulation agent
│   │   ├── tools/                  # Custom tools for agents
│   │   │   ├── video_analysis.py   # Multimodal video processing
│   │   │   ├── market_data.py      # Financial API connectors
│   │   │   └── strategy_tools.py   # Risk calculation tools
│   │   ├── api/                    # FastAPI endpoints
│   │   │   ├── video_upload.py     # Video processing endpoints
│   │   │   ├── chat.py             # WebSocket chat endpoints
│   │   │   └── strategy.py         # Strategy retrieval endpoints
│   │   ├── config/                 # YAML configuration files
│   │   │   ├── agents.yaml         # Agent definitions (roles, goals)
│   │   │   └── tasks.yaml          # Task definitions
│   │   ├── crew.py                 # Main crew orchestration logic
│   │   └── main.py                 # FastAPI application entry point
│   ├── .env                        # Environment variables (API keys)
│   └── pyproject.toml              # Backend dependencies
├── frontend/                       # React application (adapted from reference)
│   ├── src/
│   │   ├── components/             # React components
│   │   │   ├── ui/                 # Shadcn UI components
│   │   │   ├── VideoUpload.tsx     # Video upload component
│   │   │   ├── TradingTimeline.tsx # Activity timeline (adapted)
│   │   │   ├── ChatInterface.tsx   # Chat interface (adapted)
│   │   │   ├── StrategyDisplay.tsx # Trading strategy results
│   │   │   └── WelcomeScreen.tsx   # Welcome screen (adapted)
│   │   ├── lib/                    # Utility functions
│   │   │   └── utils.ts            # Helper functions
│   │   ├── hooks/                  # Custom React hooks
│   │   │   └── useCrewAI.ts        # CrewAI API integration hook
│   │   ├── App.tsx                 # Main app component
│   │   ├── main.tsx                # App entry point
│   │   └── global.css              # Tailwind + custom styles
│   ├── package.json                # Frontend dependencies
│   ├── vite.config.ts              # Vite configuration
│   └── components.json             # Shadcn UI configuration
├── docker-compose.yml              # Development environment
├── Dockerfile                      # Container build instructions
└── Makefile                        # Development commands
```

## Configuration Patterns
- **Environment Variables**: Store API keys in `.env` files
- **YAML Configs**: Use for agent/task definitions in CrewAI
- **Separate Concerns**: Frontend/backend clearly separated
- **Docker Ready**: Support containerized deployment for hackathon demo

## Key Files to Modify
- `config/*.yaml` - Agent and task configurations for CrewAI
- `crew.py` - Multi-agent logic and tools orchestration
- `api/*.py` - FastAPI endpoints for frontend integration
- `components/*.tsx` - React components for trading interface
- `.env` files - API keys and environment configuration