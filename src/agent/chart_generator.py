from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.agent.llm_client import get_chat_model
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class ChartData(BaseModel):
    label: str
    value: float

class ChartConfig(BaseModel):
    has_data: bool = Field(description="True if the text contains financial or numerical data suitable for charting")
    chart_type: Literal["bar", "line", "pie", "none"] = Field(description="Type of chart to generate. Choose none if no data exists.")
    title: str = Field(description="Title of the chart")
    x_axis_label: Optional[str] = Field(description="Label for the X axis")
    y_axis_label: Optional[str] = Field(description="Label for the Y axis")
    data: List[ChartData] = Field(description="List of data points to plot")

class ChartGenerator:
    def __init__(self, provider: str = "Azure OpenAI", model_name: str = "", api_key: str = None):
        self.llm = get_chat_model(provider, model_name, api_key)
        self.chart_parser = JsonOutputParser(pydantic_object=ChartConfig)
        
        chart_template = """Analyze the following text and extract any statistical, financial, or numerical data into a structured chart configuration.
        Determine the most appropriate chart type ('line' for trends/time series, 'bar' for comparisons, 'pie' for composition).
        If the text does NOT contain chartable data, set 'has_data' to false and 'chart_type' to 'none'.
        
        {format_instructions}
        
        Text to analyze:
        {text}
        """
        self.chart_prompt = ChatPromptTemplate.from_template(chart_template)
        self.chart_chain = self.chart_prompt | self.llm | self.chart_parser

    async def agenerate(self, answer_text: str) -> dict:
        """
        Analyze an answer and return a structured JSON dict dictating how to chart it.
        """
        try:
            return await self.chart_chain.ainvoke({
                "text": answer_text,
                "format_instructions": self.chart_parser.get_format_instructions()
            })
        except Exception:
            return {"has_data": False, "chart_type": "none", "title": "", "data": []}
