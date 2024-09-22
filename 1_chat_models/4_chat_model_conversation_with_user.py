from dotenv import load_dotenv
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_community.chat_models import ChatPerplexity

# Load environment variables from .env
load_dotenv()

# Create a Perplexity model
model = ChatPerplexity(timeout=30)


chat_history = []  # Use a list to store messages

# Set an initial system message (optional)
system_message = SystemMessage(content='You are a helpful AI assistant.')
chat_history.append(system_message)  # Add system message to chat history

# Chat loop
while True:
    query = input('You: ')
    if query.lower() == 'exit':
        break
    chat_history.append(HumanMessage(content=query))  # Add user message

    # Get AI response using history
    result = model.invoke(chat_history)
    response = result.content
    chat_history.append(AIMessage(content=response))  # Add AI message

    print(f'AI: {response}')


print('---- Message History ----')
print(chat_history)
