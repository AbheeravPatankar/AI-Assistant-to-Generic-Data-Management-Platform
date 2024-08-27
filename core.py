import os
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import OllamaEmbeddings
from langchain.prompts import PromptTemplate
from prompts.prompts import *
from backend.sample import *
from backend.sample import remove_json_comments
from langchain_groq import ChatGroq
load_dotenv()

# Define the template for the prompt
# Initialize the embeddings and vector store
embeddings = OllamaEmbeddings(model="llama3")

# Initialize the language model
#llm = ChatOllama(model="llama3")
llm = ChatGroq(model="llama3-8b-8192")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def create_template(query: str):
    try:
        documentation = PineconeVectorStore(
            index_name=os.getenv("INDEX_NAME1"), embedding=embeddings
        )
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
        documentation = PineconeVectorStore(
            index_name=os.getenv("INDEX_NAME2"), embedding=embeddings
        )
        prompt1 = PromptTemplate.from_template(get_template_name_prompt)

        chain = (
                {
                    "input": RunnablePassthrough(),
                }
                | prompt1
                | llm
        )
        # Invoke the retrieval chain with the query
        result1 = chain.invoke(input={"input": query})
        csv_values = parse_csv(result1.content)
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

        prompt2 = PromptTemplate.from_template(create_object_from_template)
        chain2 = (
                {
                    "documentation": documentation.as_retriever() | format_docs,
                    "csv": RunnablePassthrough(),
                    "template JSON": RunnablePassthrough(),
                    "OBJECT_JSON_format": RunnablePassthrough()
                }
                | prompt2
                | llm
        )

        #Define your input data
        input_data = {
            "OBJECT_JSON_format": OBJECT_JSON_format,
            "csv": csv_values,
            "template JSON": template_json
        }

        # Ensure chain2 has the correct invoke method and pass the input correctly
        result = chain2.invoke(input_data)

        template_name = extract_value_from_json(template_json, "template_name")
        object_json_list = extract_object_json(result.content)
        object_json_list = update_key_in_json_list(object_json_list, "obj_template", template_name)
        object_json_list = update_obj_name(object_json_list)
        return object_json_list

    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Return None if an error occurs



def attach_expression(query: str):
    # try:
        prompt1 = PromptTemplate.from_template(get_template_name_prompt)

        chain = (
            {
                "input": RunnablePassthrough(),
            }
            | prompt1
            | llm
        )
        result1 = chain.invoke(input={"input": query})
        result_text = result1.content

        # Extract the template name from the output
        lines = result_text.splitlines()
        for line in lines:
            if "Template name:" in line:
                template_name = line.split("Template name:")[1].strip()
                break

        template_json = {
            "template_name": "Employee",
            "attributes": [
                {"attribute_name": "ID", "attribute_type": "int", "expression": ""},
                {"attribute_name": "firstName", "attribute_type": "string", "expression": ""},
                {"attribute_name": "lastName", "attribute_type": "string", "expression": ""},
                {"attribute_name": "age", "attribute_type": "int", "expression": ""},
                {"attribute_name": "department", "attribute_type": "string", "expression": ""},
                {"attribute_name": "baseSalary", "attribute_type": "float", "expression": ""},
                {"attribute_name": "totalSalary", "attribute_type": "double", "expression": ""}
            ],
            "expressionList": []
        }

        prompt2 = PromptTemplate.from_template(attach_expression_template_prompt)
        chain = (
            {
                "input": RunnablePassthrough(),
                "template": RunnablePassthrough(),
            }
            | prompt2
            | llm
        )

        input_data = {
            "input": query,
            "template": template_json
        }

        result2 = chain.invoke(input_data)

        json_with_comment, response = extract_and_remove_json(
            result2.content, "JSON Body:"
        )

        json_without_comment = remove_json_comments(json_with_comment)
        json_dict = json.loads(json_without_comment)

        # Remove the "input" key if it exists
        if "input" in json_dict:
            del json_dict["input"]

        # Convert the dictionary back to JSON string
        final_json = json.dumps(json_dict, indent=4)
        
        print(final_json)
        return final_json, response
        
    # except Exception as e:
    #     print(f"An error occurred: {e}")
    #     return None  # Return None if an error occurs

if __name__ == "__main__":
    # res = create_template(
    #     query="create Employee template. An Employee has ID firstName lastName age totalSalary baseSalary(boolean)"
    # )
    # res = create_template(
    #     query="Explain the procedure to create a template. Also explain the JSON format for the template."
    # )
    # res2 = create_objects(
    #     query="""
    #     Generate objects for template Library.
    #     Death on the Nile, Agatha Christie, 12.34,
    #     James Bond, Ian Fleming, 23.43
    #     Man eaters of kumaon, Jim Corbett, 56.67,
    #     Let us C, Yashwant Kanetkar, 100
    # """
    # )
    res3 = attach_expression(query="""Attach the expression totalSalary = baseSalary * 100""")


