from dotenv import load_dotenv
from typing import List, Dict
import os
import time
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings, Document, StorageContext, load_index_from_storage
from llama_index.core import VectorStoreIndex
from llama_index.readers.mongodb import SimpleMongoReader
from slugify import slugify
from .llm_enum import LLM_ENUM

# Configure env for ALIA BOT
ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=ENV_PATH)
DATA_PATH = os.getenv("DATA_PATH") or './data'

PERSIST_DIR = os.getenv("PERSIST_DIR") or  "./storage"


def get_documents(query=Dict) -> List[Document]:
    reader = SimpleMongoReader(
        uri=os.getenv("MONGO_URI")
    )
    return reader.lazy_load_data(
        db_name=os.getenv("MONGO_DOCUMENTS_DBNAME"),
        field_names=["desc_text"],
        collection_name=os.getenv("MONGO_DOCUMENTS_COLLECTION"),
        query_dict=query
    )

def is_math(text:str) -> bool:
    pass

def image_to_text(image_path: str):
    pass

def find(query: str, promotion: str, course: str = "", subject: str= "", source: str= "", model: str = "gpt-3.5-turbo-0125", llm=LLM_ENUM.OPENAI) -> VectorStoreIndex:
    if llm == LLM_ENUM.OPENAI:
        Settings.llm = OpenAI(temperature=0.2, model=model)
    
    # create index storage for each promotion+course as a cache
    course = slugify(course) if course else ""
    source = slugify(source) if source else ""
    subject = slugify(subject) if subject else ""
    doc_query = {"promotion": promotion, "course": course} if course else {"promotion": promotion}
    documents = [doc for doc in get_documents(query=doc_query)]
    index = VectorStoreIndex.from_documents(documents)
    # store it for later
    # index.storage_context.persist(persist_dir=storage_path)
    # storage_path = os.path.join(PERSIST_DIR, source, subject, promotion, course) 
    # if not os.path.exists(storage_path):
    #     # load the documents and create the index
    #     doc_query = {"promotion": promotion, "course": course} if course else {"promotion": promotion}
    #     documents = [doc for doc in get_documents(query=doc_query)]
    #     index = VectorStoreIndex.from_documents(documents)
    #     # store it for later
    #     index.storage_context.persist(persist_dir=storage_path)
    # else:
    #     # load the existing index
    #     storage_context = StorageContext.from_defaults(persist_dir=storage_path)
    #     index = load_index_from_storage(storage_context)
        
    query_engine = index.as_query_engine()
    return query_engine.query(query)

if __name__ == "__main__":
    start = time.time()
    cours = "POLITIQUE ET STRATEGIE D'ENTREPRISE"
    question = "Décrire en 1 page les principes de la politique d'entreprise"
    response = find(query=question)
    end = time.time()
    print(f"Question: {question} \nRéponse: {response}")
    print(f"\n\n Durée: {int(end - start)} secondes")

