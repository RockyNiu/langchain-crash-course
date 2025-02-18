from dotenv import load_dotenv
from langchain_community.chat_models import ChatPerplexity
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# Load environment variables from .env
load_dotenv()

# Create a Perplexity model
model = ChatPerplexity(timeout=30)

# SystemMessage:
#   Message for priming AI behavior, usually passed in as the first of a sequenc of input messages.
# HumanMessagse:
#   Message from a human to the AI model.
messages = [
    SystemMessage(
        content='Solve the following math problems'
    ),  # must be the first message
    HumanMessage(content='What is 81 divided by 9?'),
]

# Invoke the model with messages
# result = model.invoke(messages)
# print(f"Answer from AI: {result.content}")


# AIMessage:
#   Message from an AI.
messages = [
    SystemMessage(content='Solve the following math problems'),
    HumanMessage(content='What is 81 divided by 9?'),
    AIMessage(content='81 divided by 9 is 9.'),
    HumanMessage(content='What is 10 times 5?'),
]

# Invoke the model with messages
# result = model.invoke(messages)
# print(f"Answer from AI: {result.content}")


# AIMessage:
#   Message from an AI.
messages = [
    SystemMessage(
        content='Solve the following math problems. For each question, provide the answer in the following format: { "answer": <number> }'
    ),
    HumanMessage(content='What is 81 divided by 9?'),
    AIMessage(content='{ "answer": 9 }'),
    HumanMessage(content='What is 10 times 5?'),
]

# Invoke the model with messages
result = model.invoke(messages)
print(f'Answer from AI: {result.content}')
