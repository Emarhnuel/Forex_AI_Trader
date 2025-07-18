# Multimodal Trading Assistant Backend

## Chart Analyst Agent Configuration

This directory contains the CrewAI configuration for the Chart Analyst Agent, which analyzes trading chart videos using multimodal LLMs.

### Setup

1. **Install Dependencies**:
   ```bash
   pip install -e .
   ```

2. **Environment Variables**:
   Copy `.env.example` to `.env` and set your API keys:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Test Configuration**:
   ```bash
   python test_chart_analyst.py
   ```

### Chart Analyst Agent

**Role**: Multimodal Chart Analysis Specialist

**Capabilities**:
- Analyzes trading chart videos frame-by-frame
- Identifies trading pairs (BTC/USD, EUR/USD, etc.)
- Detects technical indicators (RSI, MACD, Moving Averages)
- Recognizes chart patterns (triangles, head and shoulders, flags)
- Identifies support and resistance levels
- Determines trend direction and strength

**Tools**:
- `video_analysis_tool`: Processes videos using OpenAI's GPT-4 Vision model

### Configuration Files

- `src/config/agents.yaml`: Agent definitions and properties
- `src/config/tasks.yaml`: Task configurations and expected outputs
- `src/tools/video_analysis.py`: Multimodal video analysis tool

### Task: Chart Analysis

**Input**: Video file path containing trading chart footage
**Output**: Structured JSON with technical analysis including:
- Trading pair identification
- Technical indicators present
- Chart patterns detected
- Support/resistance levels
- Trend analysis
- Confidence scores

### Next Steps

This completes Task 1.1. The Chart Analyst Agent is configured and ready for integration with the full CrewAI workflow.

**Upcoming Tasks**:
- 1.2: Financial Data Agent configuration
- 1.3: Strategy Agent configuration
- 2.1: Implement remaining tools
- 3.1: Create TradingAssistantCrew class