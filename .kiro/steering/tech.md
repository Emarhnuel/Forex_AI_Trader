# Technology Stack

## CrewAI Multi-Agent System
- **Framework**: CrewAI for multi-agent orchestration
- **Python**: 3.10-3.12 (strict version requirement)
- **Package Manager**: UV for dependency management
- **Configuration**: YAML files for agents and tasks
- **API Keys**: OpenAI API key required in `.env`

### Common Commands
```bash
# Install dependencies
crewai install

# Run the crew
crewai run

# Available scripts
forex_ai_agent  # Main entry point
run_crew       # Alternative run command
train          # Training mode
replay         # Replay functionality
test           # Testing
```

## Frontend Technology Stack
- **Framework**: React 19 + TypeScript
- **Build Tool**: Vite for development and build
- **Styling**: Tailwind CSS v4 + Shadcn UI (New York style)
- **Icons**: Lucide React
- **Routing**: React Router DOM
- **Markdown**: React Markdown for content rendering

### Frontend Development Commands
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Backend Integration
- **API Framework**: FastAPI for high-performance endpoints
- **Multi-Agent System**: CrewAI orchestrating specialized agents
- **LLM Integration**: OpenAI API for agent intelligence
- **File Handling**: Multimodal LLM processing for video analysis
- **Real-time Communication**: WebSocket for live updates

## Environment Variables
- `OPENAI_API_KEY`: Required for CrewAI agents
- `FASTAPI_ENV`: Environment setting (development/production)
- `CORS_ORIGINS`: Allowed origins for CORS (frontend URLs)
- `AUTH0_DOMAIN`: Auth0 domain for authentication
- `AUTH0_CLIENT_ID`: Auth0 client ID for frontend
- `AUTH0_CLIENT_SECRET`: Auth0 client secret for backend
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Supabase anonymous key
- `SUPABASE_SERVICE_KEY`: Supabase service role key