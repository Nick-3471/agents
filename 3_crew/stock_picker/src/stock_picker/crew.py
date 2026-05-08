from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool
from pydantic import BaseModel, Field
from typing import List


class TrendingCompany(BaseModel):
    """ A company that is in the news and attracting attention """
    name: str = Field(description="Company name")
    ticker: str = Field(description="Stock ticker symbol")
    current_price: float = Field(description="Current stock price in USD")
    price_change_pct: float = Field(description="Recent price change as a percentage")
    reason: str = Field(description="Primary reason the company is trending")
    sector: str = Field(description="Sector the company belongs to")
    market_cap_category: str = Field(description="Market cap category: small, mid, or large")
    confidence_score: int = Field(description="Confidence score from 1-10 on the strength of the trend", ge=1, le=10)

class TrendingCompanyList(BaseModel):
    """ List of exactly 10 trending companies that are in the news """
    companies: List[TrendingCompany] = Field(description="List of exactly 10 companies trending in the news")

class TrendingCompanyResearch(BaseModel):
    """ Detailed financial research on a trending company """
    name: str = Field(description="Company name")
    ticker: str = Field(description="Stock ticker symbol")
    financial_health: str = Field(description="Financial health summary covering revenue, EPS, margins, and debt")
    valuation: str = Field(description="Valuation assessment including P/E and EV/EBITDA versus sector average")
    analyst_consensus: str = Field(description="Analyst consensus rating and average price target")
    catalysts_and_risks: str = Field(description="Key upcoming catalysts and material risks")
    fundamentals_rating: str = Field(description="Fundamentals rating: Strong, Moderate, or Weak")
    investment_grade: str = Field(description="Overall investment grade: A, B, C, or D")
    investment_thesis: str = Field(description="A 2-3 sentence investment thesis summary")

class TrendingCompanyResearchList(BaseModel):
    """ A list of detailed research on all 10 trending companies """
    research_list: List[TrendingCompanyResearch] = Field(description="Comprehensive research on all 10 trending companies")


@CrewBase
class StockPicker():
    """StockPicker crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    llm = LLM(
        model="anthropic/claude-haiku-4-5-20251001",
        temperature=0.7,
    )
    llm_for_manager = LLM(
        model="anthropic/claude-sonnet-4-6",
    )


    @agent
    def stock_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['stock_researcher'],
            tools=[SerperDevTool()],
            llm=self.llm,
        )
        
    @agent
    def financial_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_analyst'],
            tools=[SerperDevTool()],
            llm=self.llm,
        )
    
    @agent
    def stock_picker(self) -> Agent:
        return Agent(
            config=self.agents_config['stock_picker'],
            llm=self.llm,
        )

    @task
    def stock_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['stock_research_task'],
            output_pydantic=TrendingCompanyList,
        )
    
    @task
    def financial_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['financial_analysis_task'],
            # output_pydantic=TrendingCompanyResearchList,
        )
    
    @task
    def stock_picking_task(self) -> Task:
        return Task(
            config=self.tasks_config['stock_picking_task'],
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the StockPicker crew"""

        manager = Agent(
            config=self.agents_config['crew_manager'],
            allow_delegation=True,
            llm=self.llm,
        )
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager,
        )