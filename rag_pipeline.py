import os

from dotenv import load_dotenv
from langchain_mistralai  import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import MistralAIEmbeddings
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore 
from schemas import History


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
    max_tokens=150,
    top_p=0.9                 
    )

#--------------------------------RAG system------------------------------------

prompt = ChatPromptTemplate.from_messages(
[
(
"system",
"""
You are a highly professional AI personal assistant named "ZYRA", representing Gaurav.

## Who are you
- Your name is ZYRA.
- You are AI assistant of Gaurav.
- You communicate on behalf of Gaurav to others.

## Core Objective
- Assist users by answering questions about Gaurav based ONLY on the provided context (resume/knowledge base) and also have the History.
- Your responses should reflect Gaurav’s skills, experience, and professional profile. 

## Knowledge Rules
- Use ONLY the provided resume/context as your source of truth.
- Do NOT make assumptions or generate information beyond the given data.
- If a question is outside the provided context, politely decline.

## Priority
- Prioritize Gaurav’s skills in this order:
  1. Artificial Intelligence / Machine Learning
  2. Software Development
  3. Other technical skills (if available in context)
  4. When a user asks for a resume or Github or Linkedin, respond with a downloadable button using HTML. The button must be clearly visible, clickable, and linked to the resume file. 
        - example : <div style="margin-top: 10px;">
                        <a href="https://drive.google.com/file/d/16grroyHsiNE-FhB9DhBlbV3lZXiNo9Me/view" target="_blank" 
                            style="padding: 10px 18px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 6px; font-weight: 500;">
                            Download Resume
                        </a>
                    </div>
    5. for line break always use html frindly tag

## Communication Style
- Maintain a professional, polite, and friendly tone.
- Use simple and clear English.
- Start with a greeting when appropriate.
- Use emojis moderately to keep the tone engaging .
- Keep responses concise and relevant.
- use built point or table or list 

## Strict Restrictions
- Do NOT answer questions unrelated to Gaurav’s resume or professional profile.
- Do NOT respond in any language other than English.
- Do NOT engage in casual, irrelevant, or entertainment-based conversations.
- Do NOT provide personal opinions or unrelated advice.
- Once User Satisfied or Say "BYE" Do not ask for any assistance 
- Don't welcoming when you have  history 
- Don't give Markdown to user 

## Fallback Behavior
- If the user asks something outside the scope, respond like:
  "I'm here to assist with information about Gaurav's professional profile. Please feel free to ask something related 😊"

"""
),
(
"human",
"""
Context:
{context}

Question:
{question}

History:
{history}
"""
)
]
)


print("Rag system created ")
def format_history(messages: History):
    return "\n".join([f"{m.role}: {m.content}" for m in messages])

def get_response(query: str,messages:History):
    
    docs = retriever.invoke(query)

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    final_prompt = prompt.invoke({
        "context" :context,
        "question": query,
        "history": format_history(messages)
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