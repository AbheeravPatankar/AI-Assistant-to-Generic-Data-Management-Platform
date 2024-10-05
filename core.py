import os
import json
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

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "Lecture"

# Initialize embeddings and the language model
embeddings = OllamaEmbeddings(model="llama3")
llm = ChatGroq(model="llama3-8b-8192",temperature=0)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def remove_json(input: str):
    try:
        query = "Remove all json from the input and only output the comments in well structed manner."
        prompt = PromptTemplate.from_template(sample_template_2)
        print(query)
        chain = (
                {
                    "question": RunnablePassthrough(),
                    "input": RunnablePassthrough(),
                }
                | prompt
                | llm
        )
        # Invoke the retrieval chain with the query
        result = chain.invoke(input={"question": query, "input": input})
        # json_with_comment, response = extract_and_remove_json(
        #     result.content, "JSON Body:"
        # )
        # json_without_comment = remove_json_comments(json_with_comment)
        print(result.content)
        return result.content

    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Return None if an error occurs

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

import json

def extract_json_from_text(text):
    """Extracts the first JSON object from a given text."""
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
        json_str = text[start_idx:end_idx+1]
        return json_str
    else:
        raise ValueError("No valid JSON object found in the response.")

def attach_expression(query: str):
    # First prompt to extract template name
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

    print("First prompt result:", result_text)

    # Extract template name from the result
    template_name = None
    lines = result_text.splitlines()
    for line in lines:
        if "Template name:" in line:
            template_name = line.split("Template name:")[1].strip()
            break

    print(f"Extracted template name: {template_name}")

    # Define the template JSON for Employee
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

    # Second prompt to attach the expression
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

    # Get the result of the second chain
    result2 = chain.invoke(input_data)

    # Debug: Print the entire result2 content
    print("Second prompt result:", result2.content)

    json_with_comment, response = extract_and_remove_json(
            result2.content, "JSON Body:"
        )

    # Attempt to extract the JSON part of the response
    try:
        json_str = extract_json_from_text(result2.content)
        json_dict = json.loads(json_str)

        # Optional: Remove the "input" key if it exists
        json_dict.pop("input", None)

        # Convert the dictionary back to JSON string for the final output
        final_json = json.dumps(json_dict, indent=4)
        print("Final JSON:", final_json)
        print(response)
        return final_json,response

    except ValueError as e:
        print(f"An error occurred: {e}")
        return None, "Error: No valid JSON found."

if __name__ == "__main__":
    res3 = attach_expression(query="""Attach the expression totalSalary = baseSalary * 100, Template Name : employee""")
