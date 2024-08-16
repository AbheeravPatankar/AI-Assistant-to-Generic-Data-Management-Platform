import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import OllamaEmbeddings
from langchain.prompts import PromptTemplate
from prompts.prompts import *
from backend.sample import extract_and_remove_json
from backend.sample import remove_json_comments

load_dotenv()

# Define the template for the prompt
# Initialize the embeddings and vector store
embeddings = OllamaEmbeddings(model="llama3")
documentation = PineconeVectorStore(
    index_name=os.getenv("INDEX_NAME"), embedding=embeddings
)

# Initialize the language model
llm = ChatOllama(model="llama3")


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def create_template(query: str):
    try:

        prompt = PromptTemplate.from_template(create_template_prompt)

        chain = (
                {
                    "documentation": documentation.as_retriever() | format_docs,
                    "question": RunnablePassthrough(),
                }
                | prompt
                | llm
        )
        # Invoke the retrieval chain with the query
        result = chain.invoke(input={"input": query})
        json_with_comment, response = extract_and_remove_json(
            result.content, "JSON Body:"
        )
        json_without_comment = remove_json_comments(json_with_comment)

        return json_without_comment, response

    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Return None if an error occurs


def create_objects(query: str):
    try:

        prompt1 = PromptTemplate.from_template(get_template_name_prompt)

        chain = (
                {
                    "documentation": documentation.as_retriever() | format_docs,
                    "question": RunnablePassthrough(),
                }
                | prompt1
                | llm
        )
        # Invoke the retrieval chain with the query
        #result1 = chain.invoke(input={"input": query})
        #print(result1.content)
        template_json = """
        {
  "template_name": "Library",
  "attributes": [
    {
      "attribute_name": "bookName",
      "attribute_type": "string",
      "expression": ""
    },
    {
      "attribute_name": "bookAuthor",
      "attribute_type": "string",
      "expression": ""
    },
    {
      "attribute_name": "bookRentPrice",
      "attribute_type": "float",
      "expression": ""
    }
  ],
  "expressionList": []
}
        """
        csv_values = """
        harry potter, J.K Rowling, 12.34,
        Man eaters of kumaon, Jim Corbett, 56.67,
        Let us C, Yashwant Kanetkar, 100
        """
        prompt2 = PromptTemplate.from_template(create_object_from_template)
        chain2 = (
                {
                    "documentation": RunnablePassthrough(),
                    "csv": RunnablePassthrough(),
                    "OBJECT_JSON_format": RunnablePassthrough(),
                    "template JSON": RunnablePassthrough()
                }
                | prompt2
                | llm
        )

        # Define your input data
        input_data = {
            "documentation": documentation.as_retriever() | format_docs,
            "csv": csv_values,
            "OBJECT_JSON_format": OBJECT_JSON_format,
            "template JSON": template_json
        }

        # Ensure chain2 has the correct invoke method and pass the input correctly
        result = chain2.invoke(input_data)

        return result

    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Return None if an error occurs


if __name__ == "__main__":
    # res = create_template(
    #     # query="create template"
    #     query="create template Library. The Library template has bookName bookAuthor bookRentPrice"
    # )

    res2 = create_objects(

        query="""
        Generate objects for template Library.
        harry potter, J.K Rowling, 12.34
        Man eaters of kumaon, Jim Corbett, 56.67
        Let us C, Yashwant Kanetkar, 100
    """
    )
