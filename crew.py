from typing import List
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

from crewai_tools import SerperDevTool, ScrapeWebsiteTool, DirectoryReadTool, FileWriterTool, FileReadTool
from pydantic import BaseModel, Field
from dotenv import load_dotenv

_ = load_dotenv()
llm = LLM(
    model="openrouter/mistralai/mistral-7b-instruct",  
    api_base="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0.7,
)



class Content(BaseModel):
    content_type: str = Field(...,
                              description="The type of content to be created (e.g., blog post, social media post, video)")
    topic: str = Field(..., description="The topic of the content")
    target_audience: str = Field(..., description="The target audience for the content")
    tags: List[str] = Field(..., description="Tags to be used for the content")
    content: str = Field(..., description="The content itself")


@CrewBase
class TheMarketingCrew():
    "The marketing crew is responsible for creating and executing marketing strategies, content creation, and managing marketing campaigns."
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def head_of_marketing(self) -> Agent:
        return Agent(
            config=self.agents_config['head_of_marketing'],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                DirectoryReadTool('resources/drafts'),
                FileWriterTool(),
                FileReadTool()
            ],
            reasoning=True,
            inject_date=True,
            llm=llm,
            allow_delegation=True,
            max_rpm=3
        )

    @agent
    def content_creator_social_media(self) -> Agent:
        return Agent(
            config=self.agents_config['content_creator_social_media'],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                DirectoryReadTool('resources/drafts'),
                FileWriterTool(),
                FileReadTool()
            ],
            inject_date=True,
            llm=llm,
            allow_delegation=True,
            max_iter=30,
            max_rpm=3
        )

    @agent
    def content_writer_blogs(self) -> Agent:
        return Agent(
            config=self.agents_config['content_writer_blogs'],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                DirectoryReadTool('resources/drafts/blogs'),
                FileWriterTool(),
                FileReadTool()
            ],
            inject_date=True,
            llm=llm,
            allow_delegation=True,
            max_iter=5,
            max_rpm=3
        )

    @agent
    def seo_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['seo_specialist'],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                DirectoryReadTool('resources/drafts'),
                FileWriterTool(),
                FileReadTool()
            ],
            inject_date=True,
            llm=llm,
            allow_delegation=True,
            max_iter=3,
            max_rpm=3
        )

    @task
    def market_research(self) -> Task:
        return Task(
            config=self.tasks_config['market_research'],
            agent=self.head_of_marketing()
        )

    @task
    def prepare_marketing_strategy(self) -> Task:
        return Task(
            config=self.tasks_config['prepare_marketing_strategy'],
            agent=self.head_of_marketing()
        )

    @task
    def create_content_calendar(self) -> Task:
        return Task(
            config=self.tasks_config['create_content_calendar'],
agent=self.content_creator_social_media()
        )

    @task
    def prepare_post_drafts(self) -> Task:
        return Task(
            config=self.tasks_config['prepare_post_drafts'],
            agent=self.content_creator_social_media()
            output_json=Content
        )

    @task
    def prepare_scripts_for_reels(self) -> Task:
        return Task(
            config=self.tasks_config['prepare_scripts_for_reels'],
agent=self.content_creator_social_media()
            output_json=Content
        )

    @task
    def content_research_for_blogs(self) -> Task:
        return Task(
            config=self.tasks_config['content_research_for_blogs'],
agent=self.content_creator_social_media()
        )

    @task
    def draft_blogs(self) -> Task:
        return Task(
            config=self.tasks_config['draft_blogs'],
            agent=self.content_writer_blogs(),
            output_json=Content
        )

    @task
    def seo_optimization(self) -> Task:
        return Task(
            config=self.tasks_config['seo_optimization'],
            agent=self.seo_specialist(),
            output_json=Content
        )

    @crew
    def marketingcrew(self) -> Crew:
        """Creates the Marketing crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            planning=True,
            planning_llm=llm,
            max_rpm=3
        )


if __name__ == "__main__":
    from datetime import datetime

    inputs = {
        "product_name": "AI Powered Excel Automation Tool",
        "target_audience": "Small and Medium Enterprises (SMEs)",
        "product_description": "A tool that automates repetitive tasks in Excel using AI, saving time and reducing errors.",
        "budget": "Rs. 50,000",
        "current_date": datetime.now().strftime("%Y-%m-%d"),
    }
    crew = TheMarketingCrew()
    crew.marketingcrew().kickoff(inputs=inputs)
    print("Marketing crew has been successfully created and run.")
