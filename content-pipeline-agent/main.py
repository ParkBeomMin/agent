"""
and_: 여러 개의 function을 listen(수신, 감지)할 수 있음. 모든 function이 끝나면 코드가 실행되게 할 수 있음.
or_: 여러 개의 function을 listen(수신, 감지)할 수 있음. 그 중 하나가 끝나면 코드가 실행되게 할 수 있음.
"""
from crewai.flow.flow import Flow, listen, start, router, and_, or_
from pydantic import BaseModel

class ContentPipelineState(BaseModel):
    # Inputs
    content_type: str = "";
    topic: str = "";

    # Internal
    max_length: int = 0;

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


