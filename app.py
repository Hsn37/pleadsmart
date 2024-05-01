import os
import streamlit as st
from openai import OpenAI
from glob import glob
from time import sleep
from cases import *
from prompts import *
import json


client = OpenAI(
    base_url="https://api.together.xyz/v1",
)

model_options = {
    "Llama 3": "meta-llama/Llama-3-70b-chat-hf", 
    "Mixtral 8x22B": "mistralai/Mixtral-8x22B-Instruct-v0.1", 
}

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.session_state["chat_model"] = model_options[st.selectbox("Select Model", model_options.keys())]
    st.session_state["top-k"] = st.slider(
        label='Relevant Cases',
        min_value=1,
        max_value=5,
    )

if not st.session_state['messages']:
    st.header("Your case details")
    if (query:= st.text_area("Enter you case details", height=150)) or st.button("Submit"):
        raw_cases = search_corpus(query, k=st.session_state["top-k"])
        cases_text = []
        for item in raw_cases:
            if 'result' in item and 'responseSet' in item['result'] and item['result']['responseSet']:
                documents = item['result']['responseSet']['document']
                for doc in documents:
                    metadata = doc['metadata']
                    full_case_text = next((m['value'] for m in metadata if m['name'] == 'full_case_text'), "No full case text available")
                    title = next((m['value'] for m in metadata if m['name'] == 'title'), "No title found")
                    # Adding both title and full case text to context messages
                    cases_text.append(f"{title}\n\n{full_case_text}")
        
        cases = "\n\n".join([f"Case {i+1}:\n{case}" for i, case in enumerate(cases_text)])
        st.session_state.messages = [
            {
                "role": "system",
                "content": system_prompt.format(cases=cases)
            },
            {
                "role": "assistant",
                "content": f"""Here are the relevant cases I have found:\n\n{cases}"""
            }
        ]
        st.rerun()
else:
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.write(message["content"])

    if prompts := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompts})
        with st.chat_message("user"):
            st.write(st.session_state.messages[-1]["content"])
            
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["chat_model"],
                messages=st.session_state.messages,
                stream=True
            )
            
        response = st.write_stream(stream)
        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)

