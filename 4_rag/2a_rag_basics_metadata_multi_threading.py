import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from chromadb import PersistentClient
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from tenacity import retry, stop_after_attempt, wait_exponential

# Set up logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define directories
current_dir = os.path.dirname(os.path.abspath(__file__))
books_dir = os.path.join(current_dir, 'books')
db_dir = os.path.join(current_dir, 'db')
persistent_directory = os.path.join(db_dir, 'chroma_db_with_metadata_multi_threading')


def init_chroma_persistent_client():
    if not os.path.exists(persistent_directory):
        os.makedirs(persistent_directory)
        logging.info(f'Created directory: {persistent_directory}')

    try:
        client = PersistentClient(
            path=persistent_directory,
        )
        logging.info('Successfully initialized Chroma PersistentClient')
        return client
    except Exception as e:
        logging.error(f'Failed to initialize Chroma PersistentClient: {str(e)}')
        raise


def load_documents(book_files):
    documents = []
    for book_file in book_files:
        file_path = os.path.join(books_dir, book_file)
        loader = TextLoader(file_path)
        try:
            book_docs = loader.load()
            for doc in book_docs:
                doc.metadata = {'source': book_file}
                documents.append(doc)
            logging.info(f'Successfully loaded {book_file}')
        except Exception as e:
            logging.error(f'Error loading {book_file}: {str(e)}')
    return documents


@retry(stop=stop_after_attempt(10), wait=wait_exponential(multiplier=1, min=2, max=30))
def persist_batch(batch, embeddings, batch_id, client):
    try:
        Chroma.from_documents(batch, embeddings, client=client)
        logging.info(f'Successfully persisted batch {batch_id}')
        return True
    except Exception as e:
        logging.error(f'Failed to persist batch {batch_id}: {str(e)}')
        raise


def process_documents(client):
    if not os.path.exists(books_dir):
        raise FileNotFoundError(
            f'The directory {books_dir} does not exist. Please check the path.'
        )

    # Load documents
    book_files = [f for f in os.listdir(books_dir) if f.endswith('.txt')]
    documents = load_documents(book_files)

    # Split documents
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    logging.info(f'Number of document chunks: {len(docs)}')

    # Create embeddings
    logging.info('Creating embeddings...')
    embeddings = OllamaEmbeddings(
        model='nomic-embed-text',
    )
    logging.info('Finished creating embeddings')

    # Persist documents using multiple threads
    logging.info('Persisting vector store using multiple threads...')
    batch_size = 1000
    max_workers = 5

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i in range(0, len(docs), batch_size):
            batch = docs[i : i + batch_size]
            future = executor.submit(
                persist_batch, batch, embeddings, i // batch_size, client
            )
            futures.append(future)

        for future in as_completed(futures):
            try:
                result = future.result()
                if not result:
                    logging.warning(
                        'A batch failed to persist. Check logs for details.'
                    )
            except Exception as e:
                logging.error(f'An error occurred while persisting a batch: {str(e)}')

    logging.info('Finished persisting vector store')


def main():
    logging.info(f'Books directory: {books_dir}')
    logging.info(f'Persistent directory: {persistent_directory}')

    try:
        # Initialize ChromaDB client
        client = init_chroma_persistent_client()

        # Process documents
        process_documents(client)
    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')


if __name__ == '__main__':
    main()
