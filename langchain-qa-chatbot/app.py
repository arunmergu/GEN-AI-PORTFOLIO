import streamlit as st
from langchain.schema import SystemMessage,HumanMessage,AIMessage
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os

#load_dotenv()



st.set_page_config(page_title='Conversational Q&A Chatbot')

st.header('Hey Lets chat')

chat=ChatOpenAI(temperature=0.5)

if 'flowmessages' not in st.session_state:
    st.session_state['flowmessages']=[SystemMessage(content='You are a comedy AI Assistant')]

def get_ai_reponse(question):
    st.session_state['flowmessages'].append(HumanMessage(content=question))
    answer=chat(st.session_state['flowmessages'])
    st.session_state['flowmessages'].append(AIMessage(content=answer.content))
    return answer.content

input_text=st.text_input("Input :",key='Input')

response=get_ai_reponse(input_text)

submit=st.button("Ask me question")

if submit:
    st.subheader("Response is :")
    st.write(response)