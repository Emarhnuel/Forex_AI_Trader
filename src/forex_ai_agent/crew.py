from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai import LLM 
from forex_ai_agent.tools.video_analysis import video_analysis_tool
from forex_ai_agent.tools.market_data import crypto_api_connector, forex_data_fetcher
from forex_ai_agent.tools.strategy_tools import risk_calculator, strategy_validator

@CrewBase
class ForexAiAgent():
    """Multimodal Trading Assistant Crew"""

    # Configuration file paths
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'


    llm_1 = LLM(
    model="openrouter/google/gemini-2.5-flash-preview-05-20",
    base_url="https://openrouter.ai/api/v1",
    max_tokens=2000,
    temperature=0.1,
    stream=True,
    seed=42,
    api_key=os.getenv("OPENROUTER_API_KEY")
)
    
    @agent
    def chart_analyst(self) -> Agent:
        """Chart Analyst Agent - Analyzes trading chart videos using multimodal LLMs"""
        return Agent(
            config=self.agents_config['chart_analyst'], # type: ignore[index]
            tools=[video_analysis_tool],
            verbose=True
        )

    @agent
    def financial_data_agent(self) -> Agent:
        """Financial Data Agent - Gathers real-time market data"""
        return Agent(
            config=self.agents_config['financial_data_agent'], # type: ignore[index]
            tools=[crypto_api_connector, forex_data_fetcher],
            verbose=True
        )

    @agent
    def strategy_agent(self) -> Agent:
        """Strategy Agent - Formulates comprehensive trading strategies"""
        return Agent(
            config=self.agents_config['strategy_agent'], # type: ignore[index]
            tools=[risk_calculator, strategy_validator],
            verbose=True
        )

    
    @task
    def chart_analysis_task(self) -> Task:
        """Task for analyzing trading chart videos"""
        return Task(
            config=self.tasks_config['chart_analysis_task'], # type: ignore[index]
            agent=self.chart_analyst
        )

    @task
    def market_data_task(self) -> Task:
        """Task for gathering real-time market data"""
        return Task(
            config=self.tasks_config['market_data_task'], # type: ignore[index]
            agent=self.financial_data_agent,
            context=[self.chart_analysis_task]  # Depends on chart analysis results
        )

    @task
    def strategy_formulation_task(self) -> Task:
        """Task for formulating comprehensive trading strategies"""
        return Task(
            config=self.tasks_config['strategy_formulation_task'], # type: ignore[index]
            agent=self.strategy_agent,
            context=[self.chart_analysis_task, self.market_data_task],  # Depends on both previous tasks
            output_file='trading_strategy.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Multimodal Trading Assistant crew"""
       
        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential, 
            verbose=True,
        )
