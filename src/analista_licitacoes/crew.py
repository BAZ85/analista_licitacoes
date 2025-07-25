from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from src.analista_licitacoes.tools.leitor_documentos_tool import carregar_arquivos
import agentops

agentops.init()


@CrewBase
class AnalistaLicitacoes():
    """AnalistaLicitacoes crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # === Agentes ===
    @agent
    def analista_documentos(self) -> Agent:
        return Agent(config=self.agents_config['analista_documentos'], verbose=True)

    @agent
    def extrator_metadata(self) -> Agent:
        return Agent(config=self.agents_config['extrator_metadata'], verbose=True)

    @agent
    def executor_prompt_01(self) -> Agent:
        return Agent(config=self.agents_config['executor_prompt_01'], verbose=True)

    @agent
    def executor_prompt_02(self) -> Agent:
        return Agent(config=self.agents_config['executor_prompt_02'], verbose=True)

    @agent
    def executor_prompt_03(self) -> Agent:
        return Agent(config=self.agents_config['executor_prompt_03'], verbose=True)

    @agent
    def executor_prompt_04(self) -> Agent:
        return Agent(config=self.agents_config['executor_prompt_04'], verbose=True)

    @agent
    def executor_prompt_05(self) -> Agent:
        return Agent(config=self.agents_config['executor_prompt_05'], verbose=True)

    @agent
    def executor_prompt_06(self) -> Agent:
        return Agent(config=self.agents_config['executor_prompt_06'], verbose=True)

    @agent
    def executor_prompt_07(self) -> Agent:
        return Agent(config=self.agents_config['executor_prompt_07'], verbose=True)

    @agent
    def validador(self) -> Agent:
        return Agent(config=self.agents_config['validador'], verbose=True)

    @agent
    def consolidador_respostas(self) -> Agent:
        return Agent(config=self.agents_config['consolidador_respostas'], verbose=True)

    # === Tasks ===
    @task
    def carregar_documentos(self) -> Task:
        return Task(
            config=self.tasks_config['carregar_documentos'],
            tools=[lambda pasta: carregar_arquivos(pasta=pasta)],
            input_schema={'pasta': {'type': 'string'}}
        )

    @task
    def classificar_documentos(self) -> Task:
        return Task(
            config=self.tasks_config['classificar_documentos']
            # Nenhuma ferramenta aqui: depende do output da task anterior
        )

    @task
    def extrair_metadados(self) -> Task:
        return Task(config=self.tasks_config['extrair_metadados'])

    @task
    def analisar_prompt_01(self) -> Task:
        return Task(config=self.tasks_config['analisar_prompt_01'])

    @task
    def analisar_prompt_02(self) -> Task:
        return Task(config=self.tasks_config['analisar_prompt_02'])

    @task
    def analisar_prompt_03(self) -> Task:
        return Task(config=self.tasks_config['analisar_prompt_03'])

    @task
    def analisar_prompt_04(self) -> Task:
        return Task(config=self.tasks_config['analisar_prompt_04'])

    @task
    def analisar_prompt_05(self) -> Task:
        return Task(config=self.tasks_config['analisar_prompt_05'])

    @task
    def analisar_prompt_06(self) -> Task:
        return Task(config=self.tasks_config['analisar_prompt_06'])

    @task
    def analisar_prompt_07(self) -> Task:
        return Task(config=self.tasks_config['analisar_prompt_07'])

    @task
    def validar_estrutura_analise(self) -> Task:
        return Task(config=self.tasks_config['validar_estrutura_analise'])

    @task
    def consolidar_respostas(self) -> Task:
        return Task(config=self.tasks_config['consolidar_respostas'])

    # === Crew ===
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
