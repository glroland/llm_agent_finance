import streamlit as st
from langchain_chroma import Chroma
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import (
    StreamlitChatMessageHistory,
)
import chromadb
import os
from util import embedding, query, loader
from langchain_community.llms import Ollama
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
client = chromadb.HttpClient(host=chroma_host, port=8000)


# # Setup Chroma DB
db = Chroma(
    client=client,
    collection_name=chroma_collection_name,
    embedding_function=embedding_model,
    collection_metadata={"hnsw:space": "cosine"},
)

tab1, tab2 = st.tabs(["Q&A Assistant", "Article Writer"])
with tab1:

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
    
        # Debug: Show what documents are being retrieved
        # try:
        #     docs = db.similarity_search(prompt, k=3)
        #     st.write("Retrieved Documents:")
        #     for i, doc in enumerate(docs):
        #         st.write(f"Document {i+1}:")
        #         st.write(f"Content: {doc.page_content[:200]}...")
        #         st.write(f"Metadata: {doc.metadata}")
        # except Exception as e:
        #     st.write(f"Error retrieving documents: {str(e)}")
    
        # As usual, new messages are added to StreamlitChatMessageHistory
        # when the Chain is called.
        try:
            config = {"configurable": {"session_id": "any"}}
            response = chain_with_history.invoke({"question": prompt}, config)
            st.chat_message("ai").write(response)
        except Exception as e:
            st.write(f"Error generating response: {str(e)}")

with tab2:
    st.title("Financial Article Writer")
    msgs2 = StreamlitChatMessageHistory(key="article_key")
    # history = StreamlitChatMessageHistory(key="article_messages")
    
    # def stream_graph_text():
    #     config = {"configurable": {"thread_id": 12, "recursion_limit": 10}}
    #     graph = query.agentic_graph_streamlit()
    #     for event in graph.stream({"messages": [HumanMessage(content=prompt)]}, config, stream_mode="values"):
    #         response = event['messages'][-1]
    #         if 'content' in response and response['content']:
    #             yield response['content']
    #         time.sleep(0.02)
    
    if len(msgs2.messages) == 0:
        msgs2.add_ai_message("I can help you write a financial article. What topic are you interested in?")
        
    for msg in msgs2.messages:
        st.chat_message(msg.type).write(msg.content)
        
    if prompt := st.chat_input(key='articles'):
        msgs.add_user_message(HumanMessage(content=prompt))
        st.chat_message("human").write(prompt)
        try:
            with st.spinner("Generating article...", show_time=True):
                config = {"configurable": {"thread_id": 12, "recursion_limit": 10}}
                graph = query.agentic_graph_streamlit()
                for event in graph.stream({"messages": [HumanMessage(content=prompt)]}, config, stream_mode="values"):
                    response = event['messages'][-1]
                    if response.content:
                        st.chat_message("ai").write(response.content)
            st.success('Done!')
        except Exception as e:
            traceback.print_exc()
            st.write(f"Error generating response: {str(e)}")