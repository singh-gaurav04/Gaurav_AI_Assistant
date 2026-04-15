from dotenv import load_dotenv
from langchain_mistralai  import ChatMistralAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
import os

load_dotenv()


data = PyPDFLoader("document_loader\Gaurav_updated.pdf")
docs = data.load()

#-------------------------split the data--------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100, 
    chunk_overlap=10
)
texts = text_splitter.split_documents( docs)

#-------------------------embeddings and vector store--------------------------

embeddings = MistralAIEmbeddings(
    model="mistral-embed",
)


pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("gaurav-chatbot")


vector_store = PineconeVectorStore(embedding=embeddings, index=index)
vector_store.add_documents(texts)

