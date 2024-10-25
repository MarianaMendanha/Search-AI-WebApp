# Standard library imports
import os
import sys
import pickle
import json
import asyncio

# Typing imports
from typing import Optional, Any, Dict

# Environment variable management
from dotenv import load_dotenv

# OpenAI imports
import openai
# from openai import AzureOpenAI

# Multiprocessing imports
from multiprocessing import Lock
from multiprocessing.managers import BaseManager

# Llama Index imports
from llama_index.core import (
    SimpleDirectoryReader, 
    VectorStoreIndex, 
    StorageContext, 
    load_index_from_storage,
    Settings,
    Document
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding

# Azure Cosmos DB imports
# from azure.cosmos.aio import CosmosClient as AsyncCosmos
from azure.cosmos import PartitionKey, CosmosClient
from llama_index.vector_stores.azurecosmosnosql import AzureCosmosDBNoSqlVectorSearch

# Azure Table Storage imports
from llama_index.storage.docstore.azure import AzureDocumentStore
from llama_index.storage.index_store.azure import AzureIndexStore
from llama_index.storage.kvstore.azure.base import ServiceMode

# Load environment variables
load_dotenv()

""" --- FIM DOS IMPORTS --- """

def model_settings():

    llm = AzureOpenAI(
        model="gpt-4o-mini",
        deployment_name="gpt-4o-mini",
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version="2024-02-01",
    ) 
    Settings.llm = llm

    embed_model = AzureOpenAIEmbedding(
        model="text-embedding-3-small",
        deployment_name="text-embedding-3-small",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-02-01",
    )
    Settings.embed_model = embed_model
    
    Settings.text_splitter = SentenceSplitter(chunk_size=1024)

def set_cosmos():
    cosmos_config = {
        "url": os.getenv("COSMOSDB_URL"),
        "key": os.getenv("COSMOSDB_KEY"),
        "database": os.getenv("DATABASE_NAME"),
        "container": os.getenv("CONTAINER_NAME"),
        "partition": os.getenv("PARTITION_KEY"),
    }
    # pprint(cosmos_config)
    
    cosmos_client = CosmosClient(cosmos_config["url"], cosmos_config["key"])

    # specify vector store properties
    indexing_policy = {
        "indexingMode": "consistent",
        "includedPaths": [{"path": "/*"}],
        "excludedPaths": [{"path": '/"_etag"/?'}],
        "vectorIndexes": [{"path": "/embedding", "type": "quantizedFlat"}],
    }

    vector_embedding_policy = {
        "vectorEmbeddings": [
            {
                "path": "/embedding",
                "dataType": "float32",
                "distanceFunction": "cosine",
                "dimensions": 3072,
            }
        ]
    }

    cosmos_container_properties_test = {"partition_key": PartitionKey(path = cosmos_config["partition"])}
    cosmos_database_properties_test: Dict[str, Any] = {}

    storage_context = StorageContext.from_defaults(
        vector_store = AzureCosmosDBNoSqlVectorSearch(
            cosmos_client=cosmos_client,
            vector_embedding_policy=vector_embedding_policy,
            indexing_policy=indexing_policy,
            cosmos_container_properties=cosmos_container_properties_test,
            cosmos_database_properties=cosmos_database_properties_test,
            database_name = cosmos_config["database"],
            container_name = cosmos_config["container"],
            create_container=True,
        )
    )
    print("Storage Context Ready...")

    return storage_context

index: Optional[Any] = None
stored_docs: Optional[Any] = {}
lock = Lock()

index_name = "./saved_index"
pkl_name = "stored_documents.pkl"

def initialize_index():
    """
    This function initializes an index for storing and querying vectors, with the option to load from
    Cosmos DB or create a new local index if loading fails, and also loads stored documents from a
    pickle file.
    """
    
    global index, stored_docs

    model_settings()
    storage_context = set_cosmos()

    # --- Open Source ---
    # embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-mpnet-base-v2", device="cpu")

    with lock:
        try:
            index = VectorStoreIndex.from_vector_store(storage_context.vector_store)
            print("Index loaded from Cosmos DB.")
            # query_index("Qual é o meu nome?")
        except Exception as e:
            print(f"Failed to load index from Cosmos DB: {e} \n Using local index")
            index = VectorStoreIndex(nodes=[])
            index.storage_context.persist(persist_dir=index_name)
            print("New index created and persisted in Cosmos DB.")

        if os.path.exists(pkl_name):
            print("Loading stored docs from pickle...")
            with open(pkl_name, "rb") as f:
                stored_docs = pickle.load(f)

        # if os.path.exists(index_name):
        #     index = load_index_from_storage(
        #         StorageContext.from_defaults(persist_dir=index_name), 
        #         embed_model=embed_model
        #     )

def query_index(query_text):
    """
    Queries the global index using a language model to retrieve relevant information based on the input query text.
    
    :param query_text: The text used to query the global index.
    :return: The response obtained by querying the global index using the provided query_text. The response 
            is generated by utilizing a language model (llm) and the query engine with specified parameters 
            such as similarity_top_k.
    """

    global index

    model_settings()

    query_engine = index.as_query_engine(
        similarity_top_k=2,
    )
    response = query_engine.query(query_text)
    print(response)

    return response

def insert_into_index(doc_file_path, doc_id=None):
    """
    Inserts a new document into a global index, storing the document's text and ID in a dictionary and 
    persisting the index to a directory.
    
    :param doc_file_path: The file path of the document to be inserted into the global index.
    :param doc_id: The unique identifier for the document being inserted. If not provided, a default 
                    ID will be assigned.
    :return: None. This function updates the global index with the new document.
    """
    global index, stored_docs
    documents = SimpleDirectoryReader(input_files=[doc_file_path]).load_data()

    with lock:
        for document in documents:
            if doc_id is not None:
                document.id_ = doc_id
            index.insert(document)

            stored_docs[document.id_] = document.text[0:200]  # only take the first 200 chars

        index.storage_context.persist(persist_dir=index_name)

        first_document = documents[0]
        # Keep track of stored docs -- llama_index doesn't make this easy
        stored_docs[first_document.doc_id] = first_document.text[0:200] # only take the first 200 chars

        with open(pkl_name, "wb") as f:
            pickle.dump(stored_docs, f)

    return

def get_documents_list():
    """
    Retrieves the list of currently stored documents along with their IDs and text.
    
    :return: A list of dictionaries, where each dictionary contains the ID and text of a document stored 
            in the `stored_docs` dictionary.
    """
    global stored_docs
    documents_list = []
    for doc_id, doc_text in stored_docs.items():
        documents_list.append({"id": doc_id, "text": doc_text})

    return documents_list



" --- A desenvolver --- "
def delete_document_from_index():
    print("deletou")


import socket, subprocess    
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

# COMANDOS DO WINDOWS
def get_pid_using_port(port):
    result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if f':{port} ' in line:
            return int(line.split()[-1])
    return None

import time, signal, psutil
from tqdm import tqdm
def kill_task(port):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.net_connections(kind='inet'):
                if conn.laddr.port == port:
                    proc.kill()
                    print(f"Processo {proc.info['name']} (PID {proc.info['pid']}) na porta {port} foi terminado.")
                    return
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    print(f"Nenhum processo encontrado na porta {port}.")

def signal_handler(sig, frame):
    print("Ctrl+C pressionado. Matando a tarefa...")
    kill_task(5002)
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    # init the global index
    print("initializing index...")
    initialize_index()

    # Simular progresso da inicialização do servidor
    for _ in tqdm(range(100), desc="Iniciando servidor", ncols=100):
        time.sleep(0.05)  # Simula a inicialização
        
    # setup server
    # NOTE: you might want to handle the password in a less hardcoded way
    port = 5002
    if is_port_in_use(port):
        pid = get_pid_using_port(port)
        if pid:
            print(f"Porta {port} já está em uso pelo processo {pid}. Terminando o processo.")
            os.system(f"taskkill /PID {pid} /F")
        else:
            print(f"Porta {port} está em uso, mas não foi possível encontrar o PID.")
            
    manager = BaseManager(address=('127.0.0.1', port), authkey=b'password')
    manager.register('query_index', query_index)
    manager.register('insert_into_index', insert_into_index)
    manager.register('get_documents_list', get_documents_list)
    server = manager.get_server()

    print("index server started...")
    server.serve_forever()

