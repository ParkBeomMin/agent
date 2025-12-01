"""
and_: 여러 개의 function을 listen(수신, 감지)할 수 있음. 모든 function이 끝나면 코드가 실행되게 할 수 있음.
or_: 여러 개의 function을 listen(수신, 감지)할 수 있음. 그 중 하나가 끝나면 코드가 실행되게 할 수 있음.
"""
from typing import List
from crewai.flow.flow import Flow, listen, start, router, and_, or_
from crewai.agent import Agent
from crewai import LLM
from pydantic import BaseModel
from tools import web_search_tool
from seo_crew import SeoCrew
from virality_crew import ViralityCrew
class BlogPost(BaseModel):
    title: str = "";
    subtitle: str = "";
    sections: List[str] = [];

class Tweet(BaseModel):
    content: str = "";
    hashtags: str

class LinkedinPost(BaseModel):
    hook: str
    content: str
    call_to_action: str

class Score(BaseModel):
    score: int = 0;
    reason: str = "";

class ContentPipelineState(BaseModel):
    # Inputs
    content_type: str = "";
    topic: str = "";

    # Internal
    max_length: int = 0;
    score: Score | None = None;
    research: str = "";

    # Content
    blog_post: BlogPost | None = None;
    tweet: Tweet | None = None;
    linkedin_post: LinkedinPost | None = None;

class ContentPipelineFlow(Flow[ContentPipelineState]):

    @start()
    def init_content_pipeline(self):
        if self.state.content_type not in ["tweet", "blog", "linkedin"]:
            raise ValueError(f"Invalid content type: {self.state.content_type}")

        if self.state.topic == "":
            raise ValueError(f"Topic is required")

        if self.state.content_type == "tweet":
            self.state.max_length = 120;
        elif self.state.content_type == "blog":
            self.state.max_length = 800;
        elif self.state.content_type == "linkedin":
            self.state.max_length = 500;

    @listen(init_content_pipeline)
    def conduct_research(self):
        researcher = Agent(
            role="Head Researcher",
            goal=f"Find the most, interesting and useful info about {self.state.topic}",
            backstory="You're like a digital detective who loves digging up fascinating facts and insights. You have a knack for finding the good stuff that others miss.",
            tools=[web_search_tool],
        )

        self.state.research = researcher.kickoff(f"Find the most, interesting and useful info about {self.state.topic}")

    @router(conduct_research)
    def conduct_research_router(self):
        content_type = self.state.content_type;
        if content_type == "tweet":
            return 'make_tweet';
        elif content_type == "blog":
            return "make_blog";
        elif content_type == "linkedin":
            return 'make_linkedin';
        else:
            raise ValueError(f"Invalid content type: {content_type}")

    @listen(or_("make_blog", "remake_blog"))
    def handle_make_blog(self):
        blog_post = self.state.blog_post;

        llm = LLM(model="openai/o4-mini", response_format=BlogPost)

        if blog_post is None:
            self.state.blog_post = llm.call(f"""
            Make a blog post with good SEO practices on the topic {self.state.topic} using the following research:

            <research>
            ==============
            {self.state.research}
            ==============
            </research>
            """)
        else:
            self.state.blog_post = llm.call(f"""
            You wrote this blog post on {self.state.topic}, but it does not have a good SEO score because of {self.state.score.reason}. 
            Improve it.

            <blog_post>
            ==============
            {blog_post.model_dump_json()}
            ==============
            </blog_post>

            Use the following research.

            <research>
            ==============
            {self.state.research}
            ==============
            </research>
            """)

    @listen(or_("make_linkedin", "remake_linkedin"))
    def handle_make_linkedin(self):
        linkedin_post = self.state.linkedin_post;

        llm = LLM(model="openai/o4-mini", response_format=LinkedinPost)

        if linkedin_post is None:
            self.state.linkedin_post = llm.call(f"""
            Make a linkedin post that can go viralon the topic {self.state.topic} using the following research:

            <research>
            ==============
            {self.state.research}
            ==============
            </research>
            """)
        else:
            self.state.linkedin_post = llm.call(f"""
            You wrote this linkedin post on {self.state.topic}, but it does not have a good virality score because of {self.state.score.reason}. 
            Improve it.

            <linkedin_post>
            ==============
            {linkedin_post.model_dump_json()}
            ==============
            </linkedin_post>

            Use the following research.

            <research>
            ==============
            {self.state.research}
            ==============
            </research>
            """)

    @listen(or_("make_tweet", "remake_tweet"))
    def handle_make_tweet(self):
        tweet = self.state.tweet;

        llm = LLM(model="openai/o4-mini", response_format=Tweet)

        if tweet is None:
            self.state.tweet = llm.call(f"""
            Make a tweet that can go viralon the topic {self.state.topic} using the following research:

            <research>
            ==============
            {self.state.research}
            ==============
            </research>
            """)
        else:
            self.state.tweet = llm.call(f"""
            You wrote this tweet on {self.state.topic}, but it does not have a good virality score because of {self.state.score.reason}. 
            Improve it.

            <tweet>
            ==============
            {tweet.model_dump_json()}
            ==============
            </tweet>

            Use the following research.

            <research>
            ==============
            {self.state.research}
            ==============
            </research>
            """)

    @listen(handle_make_blog)
    def check_seo(self):
        print("Checking SEO....")
        result = SeoCrew().crew().kickoff(inputs={'topic': self.state.topic, 'blog_post': self.state.blog_post.model_dump_json()})
        self.state.score = result.pydantic

    @listen(or_(handle_make_tweet, handle_make_linkedin))
    def check_virality(self):
        print("Checking virality....")
        result = ViralityCrew().crew().kickoff(inputs={
            'topic': self.state.topic, 
            'content_type': self.state.content_type,
            'content': self.state.tweet.model_dump_json() if self.state.content_type == "tweet" else self.state.linkedin_post.model_dump_json(),
        })
        self.state.score = result.pydantic

    @router(or_(check_seo, check_virality))
    def score_router(self):
        content_type = self.state.content_type;
        score = self.state.score;

        if score.score >= 8:
            return 'check_passed'
        else:
            if content_type == "tweet":
                return 'remake_tweet';
            elif content_type == "blog":
                return 'remake_blog';
            elif content_type == "linkedin":
                return 'remake_linkedin';
            else:
                raise ValueError(f"Invalid content type: {content_type}")

    @listen('check_passed')
    def finalize_content(self):
        """Finalize the content"""
        print("🎉 Finalizing content...")

        if self.state.content_type == "blog":
            print(f"📝 Blog Post: {self.state.blog_post.title}")
            print(f"🔍 SEO Score: {self.state.score.score}/100")
        elif self.state.content_type == "tweet":
            print(f"🐦 Tweet: {self.state.tweet}")
            print(f"🚀 Virality Score: {self.state.score.score}/100")
        elif self.state.content_type == "linkedin":
            print(f"💼 LinkedIn: {self.state.linkedin_post.title}")
            print(f"🚀 Virality Score: {self.state.score.score}/100")

        print("✅ Content ready for publication!")
        return (
            self.state.linkedin_post
            if self.state.content_type == "linkedin"
            else (
                self.state.tweet
                if self.state.content_type == "tweet"
                else self.state.blog_post
            )
        )
    


flow = ContentPipelineFlow()

flow.kickoff(inputs={'content_type': 'blog', 'topic': 'AI'})
# flow.plot()