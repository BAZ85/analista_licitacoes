from crewai import Agent, Crew, Process, Task
from crewai.tools import tool
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from src.analista_licitacoes.tools.leitor_documentos_tool import carregar_documentos
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
#import agentops

#agentops.init()


@CrewBase
class AnalistaLicitacoes():
    """AnalistaLicitacoes crew"""

    agents: List[BaseAgent]
    tasks: List[Task]


    @agent
    def analista_documentos(self) -> Agent:
        return Agent(
            config=self.agents_config['analista_documentos'], # type: ignore[index]
            verbose=True
        )

    @agent
    def extrator_metadata(self) -> Agent:
        return Agent(
            config=self.agents_config['extrator_metadata'], # type: ignore[index]
            verbose=True
        )
    
    @agent
    def executor_prompt_01(self) -> Agent:
        return Agent(
            config=self.agents_config['executor_prompt_01'], # type: ignore[index]
            verbose=True,
        )

    @agent
    def executor_prompt_02(self) -> Agent:
        return Agent(
            config=self.agents_config['executor_prompt_02'], # type: ignore[index]
            verbose=True,
        )

    @agent
    def executor_prompt_03(self) -> Agent:
        return Agent(
            config=self.agents_config['executor_prompt_03'], # type: ignore[index]
            verbose=True,
        )
    
    @agent
    def executor_prompt_04(self) -> Agent:
        return Agent(
            config=self.agents_config['executor_prompt_04'], # type: ignore[index]
            verbose=True,
        )
    
    @agent
    def executor_prompt_05(self) -> Agent:
        return Agent(
            config=self.agents_config['executor_prompt_05'], # type: ignore[index]
            verbose=True,
        )

    @agent
    def executor_prompt_06(self) -> Agent:
        return Agent(
            config=self.agents_config['executor_prompt_06'], # type: ignore[index]
            verbose=True,
        )
    
    @agent
    def executor_prompt_07(self) -> Agent:
        return Agent(
            config=self.agents_config['executor_prompt_07'], # type: ignore[index]
            verbose=True,
        )

    @agent
    def validador(self) -> Agent:
        return Agent(
            config=self.agents_config['validador'], # type: ignore[index]
            verbose=True,
        )

    @agent
    def consolidador_respostas(self) -> Agent:
        return Agent(
            config=self.agents_config['consolidador_respostas'], # type: ignore[index]
            verbose=True,
        )

    @task
    def carregar_documentos(self) -> Task:
        return Task(
            config=self.tasks_config['carregar_documentos'], # type: ignore[index]
            tools=[carregar_documentos]
        )

    @task
    def classificar_documentos(self) -> Task:
        return Task(
            config=self.tasks_config['classificar_documentos'], # type: ignore[index]     
            tools=[carregar_documentos]       
        )
    
    @task
    def extrair_metadados(self) -> Task:
        return Task(
            config=self.tasks_config['extrair_metadados'], # type: ignore[index]            
    )

    @task
    def analisar_prompt_01(self) -> Task:
        return Task(
            config=self.tasks_config['analisar_prompt_01'], # type: ignore[index]                       
    )

    @task
    def analisar_prompt_02(self) -> Task:
        return Task(
            config=self.tasks_config['analisar_prompt_02'], # type: ignore[index]                       
    )

    @task
    def analisar_prompt_03(self) -> Task:
        return Task(
            config=self.tasks_config['analisar_prompt_03'], # type: ignore[index]                      
    )

    @task
    def analisar_prompt_04(self) -> Task:
        return Task(
            config=self.tasks_config['analisar_prompt_04'], # type: ignore[index]                      
    )

    @task
    def analisar_prompt_05(self) -> Task:
        return Task(
            config=self.tasks_config['analisar_prompt_05'], # type: ignore[index]                      
    )

    @task
    def analisar_prompt_06(self) -> Task:
        return Task(
            config=self.tasks_config['analisar_prompt_06'], # type: ignore[index]                      
    )

    @task
    def analisar_prompt_07(self) -> Task:
        return Task(
            config=self.tasks_config['analisar_prompt_07'], # type: ignore[index]                      
    )
    
    @task
    def validar_estrutura_analise(self) -> Task:
        return Task(
            config=self.tasks_config['validar_estrutura_analise'], # type: ignore[index]                       
    )

    @task
    def consolidar_respostas(self) -> Task:
        return Task(
            config=self.tasks_config['consolidar_respostas'], # type: ignore[index]            
    )

    @tool
    def leitor_documentos_tool(self):
        """
        Ferramenta para leitura de documentos em diversos formatos
        """
        return carregar_documentos

    @crew
    def crew(self) -> Crew:
        """Creates the AnalistaLicitacoes crew"""

        return Crew(
            agents=self.agents, 
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,  
        )
