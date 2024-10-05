import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings

load_dotenv()

if __name__ == "__main__":
    print("Hello world vector-dbs")
    loader = TextLoader("/home/abheeravsubuntu/documentation-helper/documentation/create_object.txt")
    document = loader.load()
    print("Splitting....")
    text_splitter = CharacterTextSplitter(chunk_size=600, chunk_overlap=50)
    texts = text_splitter.split_documents(document)
    print(f"created {len(texts)} chunks")

    embeddings = OllamaEmbeddings(model="llama3")

    print(embeddings)
    print("ingesting....")
    PineconeVectorStore.from_documents(
        texts, embeddings, index_name=os.environ["INDEX_NAME"], namespace="create object"
    )
    print("done!")
