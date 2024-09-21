# Chat Model Documents: https://python.langchain.com/v0.2/docs/integrations/chat/
# OpenAI Chat Model Documents: https://python.langchain.com/v0.2/docs/integrations/chat/openai/
from dotenv import load_dotenv
from langchain_community.chat_models import ChatPerplexity

# Load environment variables from .env
load_dotenv()

# Create a Perplexity model
model = ChatPerplexity(timeout=30)

# Invoke the model with a message
result = model.invoke('What is 81 divided by 9?')
print('Full result:')
print(result)
print('Content only:')
print(result.content)
