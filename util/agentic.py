from typing import TypedDict, Literal
from langgraph.graph import END, StateGraph
from typing import Annotated, Literal, TypedDict
from langgraph.graph.message import add_messages
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import functools
from langgraph.prebuilt import ToolNode
from util import agentic_templates, loader
from dotenv import load_dotenv
load_dotenv()

#####################################
## STATE ##
#####################################
class NMAgentState(TypedDict):
  """
  Encapsulates state in our agentic workflow
  """
  messages: Annotated[list, add_messages]

#####################################
## TOOLS ##
#####################################
google_search_tool = TavilySearchResults(max_results=5, include_answer=True, include_raw_content=True, include_images=True,)

#####################################
## AGENTS ##
#####################################

"""
The LLMs used by the agents
"""
granite_llm = loader.init_llm(agentic=True)

def create_agent(llm, tools, system_message: str):
    """
    Creates an agent with the given LLM, tools, and system message
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "{system_message}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    if tools:
      return prompt | llm.bind_tools(tools)
    else:
      return prompt | llm

search_agent = create_agent(granite_llm, [google_search_tool], agentic_templates.search_template)
outliner_agent = create_agent(granite_llm, [], agentic_templates.outliner_template)
writer_agent = create_agent(granite_llm, [], agentic_templates.writer_template)
critic_agent = create_agent(granite_llm, [], agentic_templates.critic_template)

#####################################
## NODES ##
#####################################
def agent_node(state, agent, name):
  result = agent.invoke(state)
  return { "messages": [result] }

search_node = functools.partial(agent_node, agent=search_agent, name="Search Agent")
outliner_node = functools.partial(agent_node, agent=outliner_agent, name="Outliner Agent")
writer_node = functools.partial(agent_node, agent=writer_agent, name="Writer Agent")
tool_node = ToolNode([google_search_tool])
critic_node = functools.partial(agent_node, agent=critic_agent, name="Critic Agent")

#####################################
## EDGES ##
#####################################
def should_search(state) -> Literal['tools', 'outliner']:
  if len(state['messages']) and state['messages'][-1].tool_calls:
    return "tools"
  else:
    return "outliner"

def should_edit(state) -> Literal['writer', END]:
  if len(state['messages']) and 'DONE' in state['messages'][-1].content:
    return END
  else:
    return "writer"

#####################################
## DEFINING THE WORKFLOW GRAPH ##
#####################################
def invoke_graph():
    workflow = StateGraph(NMAgentState)

    # nodes
    workflow.add_node("searcher", search_node)
    workflow.add_node("outliner", outliner_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("tools", tool_node)
    
    # entrypoint
    workflow.set_entry_point("searcher")
    
    # edges
    workflow.add_conditional_edges("searcher", should_search)
    workflow.add_edge("tools", "searcher")
    workflow.add_edge("outliner", "writer")
    
    # compile the workflow into a graph
    graph = workflow.compile()
    return graph