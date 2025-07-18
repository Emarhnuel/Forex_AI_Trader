from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from forex_ai_agent.tools.video_analysis import video_analysis_tool
from forex_ai_agent.tools.market_data import crypto_api_connector, forex_data_fetcher
from forex_ai_agent.tools.strategy_tools import risk_calculator, strategy_validator

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class ForexAiAgent():
    """Multimodal Trading Assistant Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    
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

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    
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
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,  # Sequential processing: Chart → Data → Strategy
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
