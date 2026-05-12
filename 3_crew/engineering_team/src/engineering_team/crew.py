from crewai import LLM, Agent, Crew, Process, Task, Memory
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

@CrewBase
class EngineeringTeam():
    """EngineeringTeam crew"""

    agents: list[BaseAgent]
    tasks: list[Task]
    memory = Memory()

    llm = LLM(
        model="anthropic/claude-haiku-4-5-20251001",
        temperature=0.7,
    )

    
    @agent
    def engineering_lead(self) -> Agent:
        return Agent(
            config=self.agents_config['engineering_lead'], 
            verbose=True,
            llm=self.llm,
        )
    
    @agent
    def backend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['backend_engineer'], 
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",
            max_execution_time=300,
            max_retry_limit=5,
            llm=self.llm,
        )
    
    @agent
    def frontend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['frontend_engineer'], 
            verbose=True,
            # allow_code_execution=True,
            # code_execution_mode="safe",
            # max_execution_time=300,
            # max_retry_limit=5,
            llm=self.llm,
        )
    
    @agent
    def test_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['test_engineer'], 
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",
            max_execution_time=300,
            max_retry_limit=5,
            llm=self.llm,
        )

    @task
    def design_task(self) -> Task:
        return Task(
            config=self.tasks_config['design_task'],
        )
    
    @task
    def code_task(self) -> Task:
        return Task(
            config=self.tasks_config['code_task'],
        )
    
    @task
    def frontend_task(self) -> Task:
        return Task(
            config=self.tasks_config['frontend_task'],
        )
    
    @task
    def testing_task(self) -> Task:
        return Task(
            config=self.tasks_config['test_task'],
        )


    @crew
    def crew(self) -> Crew:
        """Creates the EngineeringTeam crew"""

        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
            #memory=self.memory,
        )
