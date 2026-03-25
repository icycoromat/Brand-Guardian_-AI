import os
import glob
import logging
from dotenv import load_dotenv
load_dotenv(override=True)

#document loaders and splitters
from langchain_classic.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

#Azure components
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch

#1: Setting logging framework
logging.basicConfig(
    level= logging.INFO,
    format= "%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("indexer")

def index_docs():
    """
    reads pdf's from backend/data -> chunks them -> uploads vector to azure ai search.
    """

    #defining paths
    #looking for 'data' folder relative to scripts location
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(current_dir, "../../backend/data")

    #3: Debugging setup: checking all env variables
    logger.info("=" * 60)
    logger.info("Environment Configuration Check:")
    logger.info(f"AZURE_OPENAI_ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
    logger.info(f"AZURE_OPENAI_API_VERSION: {os.getenv('AZURE_OPENAI_API_VERSION')}")
    logger.info(f"Embedding Deployment: {os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 
                                                   'text-embedding-3-small')}")
    logger.info(f"AZURE_SEARCH_ENDPOINT: {os.getenv('AZURE_SEARCH_ENDPOINT')}")
    logger.info(f"AZURE_SEARCH_INDEX_NAME: {os.getenv('AZURE_SEARCH_INDEX_NAME')}")
    logger.info("=" * 60)

    #4: Validating required qnv variables
    required_keys = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_API_KEY",
        "AZURE_SEARCH_INDEX_NAME"
    ]

    missing_vars = [var for var in required_keys if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required enviroment variables: {missing_vars}")
        logger.error(f"Please check your .env file and ensure all variables are set.")
        return

    #5: Initialize embedding model (Turns texts into numbers(vectors))
    try:
        logger.info("Initializing Azure OpenAI Embeddings.....")
        embeddings = AzureOpenAIEmbeddings(
            azure_deployment= os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small"),
            azure_endpoint= os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key= os.getenv("AZURE_OPENAI_API_KEY"),
            openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),

        )
        logger.info("Embedding Model Initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize embeddings: {e}")
        logger.error(f"Please verify your Azure OpenAI deployment name and endpoint.")
        return
    
    #6: Initialize Azure Search 
    try:
        logger.info("Initializing Azure AI Search vector store....")
        index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
        vector_store = AzureSearch(
            zure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            azure_search_key=os.getenv("AZURE_SEARCH_API_KEY"),
            index_name=index_name,
            embedding_function=embeddings.embed_query
        )
        logger.info(f"Vector store initialized for index: {index_name}")
    except Exception as e:
        logger.error(f"Failed to initialized Azure Search: {e}")
        logger.error(f"Please verify your Azure Search endpoint, API key, and index name.")
        return

    #7: Find PDF Files
    pdf_files = glob.glob(os.path.join(data_folder, "*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDFs found in {data_folder}. Please add files.")
        return
    
    logger.info(f"Found {len(pdf_files)} PDFs to process: {[os.path.basename(f) for f in pdf_files]}")
    all_splits = []

    #8: Process each split
    for pdf_path in pdf_files:
        try:
            logger.info(f"Loading : {os.path.basename(pdf_path)}....")
            loader = PyPDFLoader(pdf_path)
            raw_docs = loader.load()

            #Chunking: 1000 chars chunks with 200 overlap to avoid context loss
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size = 1000,
                chunk_overlap = 200
            )  
            splits = text_splitter.split_documents(raw_docs)

            #Tagginh the source for citation later
            for split in splits:
                split.metadata["source"] = os.path.basename(pdf_path)
            
            all_splits.extend(splits)
            logger.info(f"-> Split into {len(splits)} chunks.")
        except Exception as e:
            logger.info(f"Failed to process {pdf_path}: {e}")

    #9 : uPLOADING TO azure
    if all_splits:
        logger.info(f"Uploading {len(all_splits)} chunks to Azure AI Search Search Index '{index_name}'....")
        try:
            # Azure Search accepts batches automatically 
            vector_store.add_documents(documents=all_splits)
            logger.info('='* 60)
            logger.info(" Indexing Complete! Knowledge Base is ready.")
            logger.info(f"Total chunks indexed: {len(all_splits)}")
            logger.info("="*60)
        except Exception as e:
            logger.error(f"Failed to upload docs to Azure Search. {e}")
            logger.error("Please check your Azure Search configuration and try again.")
    else:
        logger.warning("No documents were processed.")
    
if __name__ == "__main__":
    index_docs()

