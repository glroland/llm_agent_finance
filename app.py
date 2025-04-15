import streamlit as st
from langchain_chroma import Chroma
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import (
    StreamlitChatMessageHistory,
)
import chromadb
import os
from util import embedding, query, loader
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages import trim_messages
import time
import traceback
from dotenv import load_dotenv
load_dotenv()

# Load environment variables
chroma_collection_name = os.getenv("CHROMA_COLLECTION_NAME")
chroma_host = os.getenv("CHROMA_HOST")
embedding_model = embedding.init_embedding_model()
llm = loader.init_llm()

# Load data from vector db
client = chromadb.HttpClient(host=chroma_host, port=os.getenv("CHROMA_PORT"))


# # Setup Chroma DB
db = Chroma(
    client=client,
    collection_name=chroma_collection_name,
    embedding_function=embedding_model,
    collection_metadata={"hnsw:space": "cosine"},
)


st.title("Financial Analysis Assistant")

st.title("Financial Analysis Assistant")

st.subheader("Supporting documents", divider=True)
text='''The following documents from the Neuberger Berman website were used to populate the RAG grounding dataset.
Try asking the chatbot questions related to these documents.    

    1. Fixed Income Investment Outlook 1Q 2025    
    2. 2025 Summary of Material Changes to Proxy Voting Guidelines  
    3. Asset Allocation Committee Outlook 1Q 2025  
    4. Firm Stakeholder Metrics  
    5. Proxy Policy Procedures  
    6. Net-Zero Alignment: Beyond the Numbers  
    7. Solving for 2025  
    8. Equity Market Outlook 2Q 2025  
    9. The State of Decarbonization 2024  
    10. 2023 Neuberger Berman Group TCFD Report    
    11. 2023 Annual Report    
    12. 2023 Stewardship and Sustainability Report
    '''
st.markdown(text)
st.divider()

msgs = StreamlitChatMessageHistory(key="special_app_key")

if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I help you?")


template = query.chat_history_template
trimmer = trim_messages(
    max_tokens=45,
    strategy="last",
    token_counter=llm,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

chain = query.query_rag_streamlit(db, llm, template)
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: msgs,
    input_messages_key="question",
    history_messages_key="history",
    history_transformer=trimmer,
)

for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

if prompt := st.chat_input(key='rag'):
    st.chat_message("human").write(prompt)

    try:
        config = {"configurable": {"session_id": "any"}}
        response = chain_with_history.stream({"question": prompt}, config)
        st.chat_message("ai").write_stream(response)
    except Exception as e:
        st.write(f"Error generating response: {str(e)}")
