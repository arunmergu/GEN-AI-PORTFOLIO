import os
from langchain_community.llms import OpenAI
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from langchain import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from langchain.memory import ConversationBufferMemory

os.environ['OPENAI_API_KEY']=os.getenv('OPENAI_API_KEY')


st.title('Lanchain with OpenAI')
input_text=st.text_input('search about celebrity')

first_input_prompt=PromptTemplate(
    input_variables=['name'],
    template='tell me about the celebrity {name}'
    )

person_memory = ConversationBufferMemory(input_key='name', memory_key='chat_history')
dob_memory = ConversationBufferMemory(input_key='person', memory_key='chat_history')
descr_memory = ConversationBufferMemory(input_key='dob', memory_key='description_history')
#Intialize OpenAI LLM
llm=OpenAI(temperature=0.8)

chain1=LLMChain(llm=llm,prompt=first_input_prompt,verbose=True,output_key='person',memory=person_memory)

second_input_prompt=PromptTemplate(
    input_variables=['name'],
    template='when was {name} born'
    )


chain2=LLMChain(llm=llm,prompt=second_input_prompt,verbose=True,output_key='dob',memory=dob_memory)


third_input_prompt=PromptTemplate(
    input_variables=['dob'],
    template='mention 5 major events on this day {dob}'
    )


chain3=LLMChain(llm=llm,prompt=third_input_prompt,verbose=True,output_key='description',memory=descr_memory)


parentchain=SequentialChain(chains=[chain1,chain2,chain3],input_variables=['name'],output_variables=['person','dob','description'], verbose=True)

if input_text:
    st.write(parentchain({'name':input_text}))

    with st.expander('Person name'):
        st.info(person_memory.buffer)

    with st.expander('Major events'):
        st.info(descr_memory.buffer)