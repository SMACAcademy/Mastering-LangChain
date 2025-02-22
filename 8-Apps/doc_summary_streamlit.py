import os, tempfile, streamlit as st
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import PyPDFLoader

from langchain_ollama import OllamaLLM

# Configure Ollama LLM
llm = OllamaLLM(
    model="llama3.2:latest",
    base_url="http://localhost:11434",
    temperature=0.1
)

from langchain_ollama import OllamaEmbeddings

# Configure embedding model
embeddings = OllamaEmbeddings(
    model="nomic-embed-text:latest",  # Correct parameter name is `model`
    base_url="http://localhost:11434",  # Base URL for the Ollama service
)

# Streamlit app
st.subheader('Summarize Document')

# Get OpenAI API key and source document input
#with st.sidebar:
    #openai_api_key = st.text_input("OpenAI API key", value="", type="password")
source_doc = st.file_uploader("Source Document", label_visibility="collapsed", type="pdf")

# If the 'Summarize' button is clicked
if st.button("Summarize"):
    # Validate inputs
    #if not openai_api_key.strip() or not source_doc:
    if not source_doc:
        st.error(f"Please provide the missing fields.")
    else:
        try:
            with st.spinner('Please wait...'):
              # Save uploaded file temporarily to disk, load and split the file into pages, delete temp file
              with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                  tmp_file.write(source_doc.read())
              loader = PyPDFLoader(tmp_file.name)
              pages = loader.load_and_split()
              os.remove(tmp_file.name)

              # Create embeddings for the pages and insert into Chroma database
              #embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
              vectordb = Chroma.from_documents(pages, embeddings)

              # Initialize the OpenAI module, load and run the summarize chain
              #llm = ChatOpenAI(temperature=0, openai_api_key=openai_api_key)
              chain = load_summarize_chain(llm, chain_type="stuff")
              search = vectordb.similarity_search(" ")
              summary = chain.run(input_documents=search, question="Write a summary within 200 words.")

              st.success(summary)
        except Exception as e:
            st.exception(f"An error occurred: {e}")