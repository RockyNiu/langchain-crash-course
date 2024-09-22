from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableLambda, RunnableSequence
from langchain_community.chat_models import ChatPerplexity
from langchain_core.messages import BaseMessage
from langchain_core.prompt_values import PromptValue

# Load environment variables from .env
load_dotenv()

# Create a Perplexity model
model = ChatPerplexity(timeout=30)

# Define prompt templates
prompt_template = ChatPromptTemplate.from_messages(
    [
        ('system', 'You are a comedian who tells jokes about {topic}.'),
        ('human', 'Tell me {joke_count} jokes.'),
    ]
)

# Create individual runnables (steps in the chain)
format_prompt = RunnableLambda(lambda x: prompt_template.format_prompt(**x))
invoke_model = RunnableLambda(
    lambda x: model.invoke(x.to_messages()) if isinstance(x, PromptValue) else None
)
parse_output = RunnableLambda(
    lambda x: x.content if isinstance(x, BaseMessage) else None
)

# Create the RunnableSequence (equivalent to the LCEL chain)
chain = RunnableSequence(first=format_prompt, middle=[invoke_model], last=parse_output)
# chain = RunnableSequence(format_prompt, invoke_model, parse_output)

# Run the chain
response = chain.invoke({'topic': 'lawyers', 'joke_count': 3})

# Output
print(response)
