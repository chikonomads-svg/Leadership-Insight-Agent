import json
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.agent.llm_client import get_chat_model

class EvaluationReport(BaseModel):
    faithfulness_score: float = Field(description="A score from 0.0 to 1.0 indicating if the answer is completely supported by the context without hallucinations.")
    faithfulness_reasoning: str = Field(description="Brief explanation of why the answer is or isn't faithful to the provided context.")
    relevance_score: float = Field(description="A score from 0.0 to 1.0 indicating if the answer directly and accurately addresses the user's question.")
    relevance_reasoning: str = Field(description="Brief explanation of why the answer is or isn't relevant to the user's question.")

class RAGEvaluator:
    def __init__(self, provider: str = "Azure OpenAI", model_name: str = "", api_key: str = None):
        """
        Initializes the Evaluation agent capable of scoring RAG responses.
        """
        self.llm = get_chat_model(provider, model_name, api_key)
        self.parser = JsonOutputParser(pydantic_object=EvaluationReport)
        
        # System prompt for strict evaluation
        template = """You are an expert, impartial AI response evaluator.
        Your task is to evaluate a generated response based on the provided retrieved context and the user's original question.
        
        You will evaluate two specific metrics:
        1. Faithfulness: Is the generated Answer entirely supported by the Context? (0.0 = completely hallucinated, 1.0 = completely supported)
        2. Relevance: Does the generated Answer actually address the User's Question directly? (0.0 = completely off-topic, 1.0 = perfectly addresses the question)
        
        Provide your evaluation exactly matching the following JSON format:
        {format_instructions}
        
        ---
        Question: {question}
        
        Context:
        {context}
        
        Answer:
        {answer}
        """
        
        self.prompt = ChatPromptTemplate.from_template(template)
        
        # LLM Chain
        self.chain = self.prompt | self.llm | self.parser
        
    async def aevaluate(self, question: str, context: str, answer: str) -> dict:
        """
        Asynchronously evaluate the generated answer against the question and retrieved context.
        """
        try:
            result = await self.chain.ainvoke({
                "question": question,
                "context": context,
                "answer": answer,
                "format_instructions": self.parser.get_format_instructions()
            })
            return result
        except Exception as e:
            return {
                "faithfulness_score": 0.0,
                "faithfulness_reasoning": f"Evaluation parsing failed or timed out: {str(e)}",
                "relevance_score": 0.0,
                "relevance_reasoning": "Could not extract relevance score."
            }
