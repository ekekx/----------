import json
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.document_loaders import WebBaseLoader,UnstructuredURLLoader
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv;load_dotenv() # openai_key  .env 선언 사용 
import jedol1Fun as jshs
from datetime import datetime, timedelta
from langchain.memory import ChatMessageHistory
import jedol2ChatDbFun as chatDB
import pdfplumber
from collections import namedtuple


def vectorDB_create(vector_folder="", selected_file=''):
    print(selected_file)
    # AI 역할
    Document = namedtuple('Document', ['page_content', 'metadata'])
    documents =[]
    
    with pdfplumber.open(f"data/{selected_file}") as pdf_document:
        for page_number, page in enumerate(pdf_document.pages):
            text = page.extract_text()

            metadata = {
                'source': f"data/{selected_file}",
                'page': page_number + 1
            }
            document = Document(page_content=text, metadata=metadata)
            documents.append(document)



    #  문서를 페이지로 -----------------------------------
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size =50,
        chunk_overlap  = 0,
        separators=["\n"],
        length_function = jshs.tiktoken_len
    )

    pages = text_splitter.split_documents(documents)

    # jshs.splitter_pages_viewer(pages);quit()

    vectorDB = FAISS.from_documents(pages , OpenAIEmbeddings())
    vectorDB.save_local(vector_folder)
    return  vector_folder

def ai_reponse( vector_folder, query, token ):
    
    vectorDB = FAISS.load_local(vector_folder, OpenAIEmbeddings())

    llm_model = ChatOpenAI(model_name="gpt-4", temperature=0)  

    chain = load_qa_chain(llm_model, chain_type="stuff")
    
    docs = vectorDB.similarity_search(query)

   # AI 역할
    chat_history=chatDB.query_history(token)

    if  chat_history !="":
        print( "token=",token )
        print( chat_history )
        chat_history=Document(
                        page_content=f" {  chat_history }", 
                        metadata={'source': 'chat history'}
                        )   
        docs.append(chat_history)

    res = chain.run(input_documents=docs, question=query)
    new_history=' 질문: '+ query +'\n  답변: '+ res
    chatDB.update_history(token,new_history,4000)
         
    return res

if __name__ == "__main__":
      today = str( datetime.now().date().today())
      print( f"vectorDB-faiss-jshs-{today}")
      token="run-jedolAi_function" 
      chatDB.setup_db()
      chatDB.new_user(token)
      print(ai_reponse(f"vectorDB-faiss-jshs-{today}", "안녕 ?",token))