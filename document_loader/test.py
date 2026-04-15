from langchain_community.document_loaders import TextLoader

data = TextLoader("document_loader/gaurav_profile.txt")
# load the data and have list of objects of type Document which has page_content and metadata as attributes
docs = data.load()

#splitting by token 

print(docs[0])
