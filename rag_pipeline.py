import os

from dotenv import load_dotenv
from langchain_mistralai  import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import MistralAIEmbeddings
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore 


load_dotenv()

embeddings = MistralAIEmbeddings(
    model="mistral-embed",
)

#-------------------------embeddings and vector store--------------------------

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("gaurav-chatbot")
vector_store = PineconeVectorStore(embedding=embeddings, index=index)


retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "k": 3,
        "score_threshold": 0.4
    }
)

llm = ChatMistralAI(
    model = "mistral-small-2506",
    temperature=0.1,
    max_tokens=100,
    top_p=0.9                 
    )

#--------------------------------RAG system------------------------------------

prompt = ChatPromptTemplate.from_messages(
[
(
"system",
"""
You are an AI personal assistant representing Gaurav Singh respond all the message like a human whatsapp.

Your role is to answer questions based on Gaurav Singh's resume and context.

Behavior Rules:

1. Identity:
- Always respond as if you ARE Gaurav Singh.
- Use a first-person tone when answering professional questions.

2. Context Usage:
- Use ONLY the provided context for resume-related answers.
- Do NOT make up any information.

3. Out-of-Scope Questions:
- If question is NOT related to resume, skills, projects, or career → refuse casually
Examples:
"not related to my work tbh"
"let’s stick to professional stuff 🙂"
"haha not really my area 😅"

  

4. Greetings & Casual Conversation:
- If the user says greetings (hi, hello, hey), respond naturally and friendly.
  Example: "Hi! I'm Gaurav Singh, happy to connect with you."

- If the user asks for a joke or casual talk, respond casually (not resume-restricted).
  Example: "Sure 😄 Here's one..."

5. Tone:
- Professional for interview/resume questions
- Friendly and human-like for casual interaction

6. Do NOT:
- Do not hallucinate achievements
- Do not break character
"""
),
(
"human",
"""
Context:
{context}

Question:
{question}
"""
)
]
)


print("Rag system created ")

def get_response(query: str):
    
    docs = retriever.invoke(query)

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )
    
    final_prompt = prompt.invoke({
        "context" :context,
        "question": query
    })
    
    response = llm.invoke(final_prompt)

    # print(f"🤖: {response.content}")

    return response.content



































































# SYSTEM_PROMPT = """You are a persona AI assistant of Gaurav Singh and you have to reply user_query according to that way."""

# #----------------------------------------------------------------------#

# template = ChatPromptTemplate.from_messages([
#     (
#         "system",SYSTEM_PROMPT
#     ),
#     (
#         "human","{data}"
#     )
# ])


# final_prompt = template.format_messages(data = docs[0].page_content)

# model = ChatMistralAI(model = "mistral-small-2506")

# response = model.invoke(final_prompt)

# print(response.content)