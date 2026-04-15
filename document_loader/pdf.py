from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter

data = PyPDFLoader("document_loader/Gaurav_updated.pdf")

docs = data.load()


#characyter text splitter
text_splitter = CharacterTextSplitter(
    separator="",
    chunk_size=20,
    chunk_overlap=1,
)

chunks = text_splitter.split_documents(docs)

# print(docs[0].page_content)
# print(chunks[0].page_content)

for i in chunks:
    print(i.page_content)
    print()