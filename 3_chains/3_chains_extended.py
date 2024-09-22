from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableLambda
from langchain_community.chat_models import ChatPerplexity

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

# Define additional processing steps using RunnableLambda
uppercase_output = RunnableLambda(lambda x: x.upper() if isinstance(x, str) else None)
count_words = RunnableLambda(
    lambda x: f'Word count: {len(x.split())}\n{x}' if isinstance(x, str) else None
)

# Create the combined chain using LangChain Expression Language (LCEL)
chain = prompt_template | model | StrOutputParser() | uppercase_output | count_words

# Run the chain
result = chain.invoke({'topic': 'lawyers', 'joke_count': 3})

# Output
print(result)
