import os
from llama_index.readers.json import JSONReader
from llama_index.core import (
    SimpleDirectoryReader, 
    VectorStoreIndex, 
    StorageContext, 
    load_index_from_storage,
)

################################### Loading Data ##########################################
documents = JSONReader().load_data(input_file='prompt_content/prompt_content.json')   
print(documents)

print("------------------------------------------------------------------")
doc_file_path = 'prompt_content/'
documents_ = SimpleDirectoryReader(input_dir=doc_file_path).load_data()
print(documents_)

############################################### Ollama e Hugging Face ################################################
# from llama_index.llms.ollama import Ollama
# llm = Ollama(model="llama3.2:1b ", request_timeout=120.0)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-mpnet-base-v2", device="cpu")

#################################################### AZURE LLM #######################################################
from dotenv import load_dotenv
load_dotenv()
from llama_index.llms.azure_openai import AzureOpenAI
llm = AzureOpenAI(
        model="gpt-4o-mini",
        deployment_name="gpt-4o-mini",
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version="2024-02-01",
    )

#################################################### SETTINGS #######################################################
from llama_index.core import Settings
Settings.llm = llm
Settings.embed_model = embed_model

####################################### Indexing #############################################
from llama_index.core import VectorStoreIndex

vector_index_doc = VectorStoreIndex.from_documents(documents)
query_engine_doc = vector_index_doc.as_query_engine()
response = query_engine_doc.query(
    "Make a Summary of the Friends episode in my docs"
)
print(response)

print("--------------------------------------------------------")
vector_index = VectorStoreIndex.from_documents(documents_) # Auto Splitter
query_engine = vector_index.as_query_engine()
response = query_engine.query(
    "Make a Summary of the Friends episode in my docs"
)
print(response)