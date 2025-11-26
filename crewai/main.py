import dotenv

dotenv.load_dotenv()

"""
* Crew 
- 여러 Agent들의 그룹
- 여러 Agent들이 특정 task를 협력하여 작업을 수행

* Agent
- 독립적으로 움직이는 존재
- 자기 role과 goal에 따라 task를 수행하고 의사결정을 함
- 목적을 달성하기 위해 tool을 사용함
- 기본적으로 Agent는 역할극
"""
from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task
from tools import count_letters
@CrewBase
class TranslatorCrew:

    @agent
    def translator_agent(self):
        return Agent(
            config=self.agents_config["translator_agent"],
        )
    @agent
    def counter_agent(self):
        return Agent(
            config=self.agents_config["counter_agent"],
            tools=[count_letters],
        )
    
    @task
    def translate_task(self):
        return Task(
            config=self.tasks_config["translate_task"],
        )
    @task
    def count_task(self):
        return Task(
            config=self.tasks_config["count_task"],
        )

    @crew
    def assemble_crew(self):
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True, # 로그를 남기는 옵션
        )


TranslatorCrew().assemble_crew().kickoff(inputs={"sentence": "Hello, how are you?"})