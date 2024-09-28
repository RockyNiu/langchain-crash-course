from dotenv import load_dotenv
from langchain import hub
from langchain.agents import (
    AgentExecutor,
    create_structured_chat_agent,
)
from langchain_community.chat_models import ChatPerplexity
from langchain_core.tools import StructuredTool

# Load environment variables from .env file
load_dotenv()


# Define a very simple tool functions that can be used by the agent
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


# List of tools available to the agent
tools = [
    StructuredTool.from_function(multiply),
    StructuredTool.from_function(add),
]

# Pull the prompt template from the hub
# https://smith.langchain.com/hub/hwchase17/structured-chat-agent
prompt = hub.pull('hwchase17/structured-chat-agent')

# Initialize a Perplexity model
llm = ChatPerplexity(timeout=30)

# # Initialize a OpenAI model
# llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0)

# # Initialize a Anthropic model
# llm = ChatAnthropic(
#     model_name='claude-3-opus-20240229', timeout=30, stop=[]
# )  # stop=[] to disable stop words

# Create the ReAct agent using the create_react_agent function
agent = create_structured_chat_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
)

# Run the agent with a test query
response = agent_executor.invoke(
    {'input': 'What is 5 multiplied by 3, and then add 10 to the result?'}
)

# Print the response from the agent
print('response:', response)
