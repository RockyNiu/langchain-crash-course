import os

from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI

####################################################################################################
# The problem of this example is that 'chat_history' is not updated after each conversation.
# For example, it couldn't find the answer to the question "Who is Brandon Hancock".

# Load environment variables from .env file
load_dotenv()

# Load the existing Chroma vector store
current_dir = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(current_dir, '..', '..', '4_rag', 'db')
persistent_directory = os.path.join(db_dir, 'chroma_db_with_metadata_multi_threading')

# Check if the Chroma vector store already exists
if os.path.exists(persistent_directory):
    print('Loading existing vector store...')
    db = Chroma(persist_directory=persistent_directory, embedding_function=None)
else:
    raise FileNotFoundError(
        f'The directory {persistent_directory} does not exist. Please check the path.'
    )

# Define the embedding model
embeddings = OllamaEmbeddings(model='nomic-embed-text')

# Load the existing vector store with the embedding function
db = Chroma(persist_directory=persistent_directory, embedding_function=embeddings)

# Create a retriever for querying the vector store
# `search_type` specifies the type of search (e.g., similarity)
# `search_kwargs` contains additional arguments for the search (e.g., number of results to return)
retriever = db.as_retriever(
    search_type='similarity',
    search_kwargs={'k': 3},
)

# Create a ChatOpenAI model
llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)

# Contextualize question prompt
# This system prompt helps the AI understand that it should reformulate the question
# based on the chat history to make it a standalone question
contextualize_q_system_prompt = (
    'Given a chat history and the latest user question '
    'which might reference context in the chat history, '
    'formulate a standalone question which can be understood '
    'without the chat history. Do NOT answer the question, just '
    'reformulate it if needed and otherwise return it as is.'
)

# Create a prompt template for contextualizing questions
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ('system', contextualize_q_system_prompt),
        MessagesPlaceholder('chat_history'),
        ('human', '{input}'),
    ]
)

# Create a history-aware retriever
# This uses the LLM to help reformulate the question based on chat history
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

# Answer question prompt
# This system prompt helps the AI understand that it should provide concise answers
# based on the retrieved context and indicates what to do if the answer is unknown
qa_system_prompt = (
    'You are an assistant for question-answering tasks. Use '
    'the following pieces of retrieved context to answer the '
    "question. If you don't know the answer, just say that you "
    "don't know. Use three sentences maximum and keep the answer "
    'concise.'
    '\n\n'
    '{context}'
)

# Create a prompt template for answering questions
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ('system', qa_system_prompt),
        MessagesPlaceholder('chat_history'),
        ('human', '{input}'),
    ]
)

# Create a chain to combine documents for question answering
# `create_stuff_documents_chain` feeds all retrieved context into the LLM
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

# Create a retrieval chain that combines the history-aware retriever and the question answering chain
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)


# Set Up ReAct Agent with Document Store Retriever
# Load the ReAct Docstore Prompt
react_docstore_prompt = hub.pull('hwchase17/react')

tools = [
    Tool(
        name='Answer Question',
        func=lambda **kwargs: rag_chain.invoke(
            {
                'input': kwargs.get('input'),
                'chat_history': kwargs.get('chat_history', []),
            }
        ),
        description='useful for when you need to answer questions about the context',
    )
]

chat_history = []

# Create the ReAct Agent with document store retriever
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=react_docstore_prompt,
)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    handle_parsing_errors=True,
    verbose=True,
)

while True:
    query = input('You: ')
    if query.lower() == 'exit':
        break
    response = agent_executor.invoke({'input': query, 'chat_history': chat_history})
    print(f"AI: {response['output']}")

    # Update history
    chat_history.append(query)
    chat_history.append(response['output'])
