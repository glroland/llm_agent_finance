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
