from langgraph.graph import StateGraph ,START,END
from langchain_huggingface import HuggingFaceEndpoint , ChatHuggingFace
from typing import TypedDict , Annotated
from dotenv import load_dotenv
from pydantic import Field , BaseModel
import operator
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import BaseMessage
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import add_messages
from langgraph.checkpoint.memory import InMemorySaver
load_dotenv()  # Load environment variables from .env file
checkpointer=InMemorySaver()
llm = HuggingFaceEndpoint(
repo_id="Qwen/Qwen2.5-7B-Instruct",
task="text-generation",
provider="featherless-ai",
max_new_tokens=1024
) # type: ignore
model = ChatHuggingFace(llm=llm)

class chatbotState(TypedDict):
    message: Annotated[list[BaseMessage], add_messages]

def generate_reply(state: chatbotState) -> dict:
    response = model.invoke(state["message"])
    return {"message": [AIMessage(content=response.content)]}

graph=StateGraph(chatbotState)
thread_id=1
config={'configurable':{'thread_id':thread_id}}

graph.add_node("chat",generate_reply)

graph.add_edge(START,"chat")
graph.add_edge("chat",END)
workflow=graph.compile(checkpointer=checkpointer)

while True:
    user_input = input("Enter input: ").strip()

    if user_input.lower() in ["exit", "stop"]:
        print("Exiting chat.")
        break

    state = {"message": [HumanMessage(content=user_input)]}
    result = workflow.invoke(state, config=config)

    messages = result["message"]
    if isinstance(messages, list) and messages:
        print(messages[-1].content)

list(workflow.get_state_history(config))
