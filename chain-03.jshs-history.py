from dotenv import load_dotenv 

from langchain.vectorstores.faiss import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
import asyncio

import pdfplumber
from collections import namedtuple

load_dotenv()


from transformers import GPT2Tokenizer
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

def tiktoken_len(text):
    tokens = tokenizer.tokenize(text)
    return len(tokens )

# loader = PyPDFLoader("files\jshs-history.pdf")
# documents = loader.load() 
Document = namedtuple('Document', ['page_content', 'metadata'])
documents =[]
with pdfplumber.open("data/해수의 물리적 성질.pdf") as pdf_document:
    for page_number, page in enumerate(pdf_document.pages):
        text = page.extract_text()

        metadata = {
            'source': 'data/해수의 물리적 성질.pdf',
            'page': page_number + 1
        }
        document = Document(page_content=text, metadata=metadata)
        documents.append(document)
        
text_splitter = RecursiveCharacterTextSplitter(
        chunk_size =50,
        chunk_overlap  = 0,
        separators=["."],
        length_function =tiktoken_len
    )

pages = text_splitter.split_documents(documents)
print( len(pages) )
i=0
for p in pages:
    i=i+1
    print( "{:02d} {:02d} ".format(i, tiktoken_len(p.page_content)), p.page_content, p.metadata['source'])

print("="*00)
index = FAISS.from_documents(pages , OpenAIEmbeddings())

index.save_local("faiss-jshs-history-pdf")

from langchain.chat_models import ChatOpenAI

llm_model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)  

chain = load_qa_chain(llm_model, verbose=False)

query = "해수의 물리적 성질에 대한 빈칸 채우기 문제를 5개 정도 만들어줘 "
docs = index.similarity_search(query)
res = chain.run(input_documents=docs, question=query)
print( query,res)
