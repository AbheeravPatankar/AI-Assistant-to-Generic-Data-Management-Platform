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
# llm = ChatOllama(model="llama3")
llm = ChatGroq(model="llama3-8b-8192")


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def give_information(query: str):
    try:
        prompt = PromptTemplate.from_template(give_information_prompt)
        create_template_doc = PineconeVectorStore(
            index_name=os.getenv("INDEX_NAME1"), embedding=embeddings
        )
        create_obj_doc = PineconeVectorStore(
            index_name=os.getenv("INDEX_NAME2"), embedding=embeddings
        )
        chain = (
                {
                    "create_template_doc": create_template_doc.as_retriever() | format_docs,
                    "create_obj_doc": create_obj_doc.as_retriever() | format_docs,
                    "question": RunnablePassthrough(),
                }
                | prompt
                | llm
        )
        # Invoke the retrieval chain with the query
        result = chain.invoke(input={"question": query})
        return result.content

    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Return None if an error occurs


def identify_function(query: str):
    try:
        prompt = PromptTemplate.from_template(define_operation_prompt)
        introduction = """
        1> Create Template – the schema for the input data is designed
2> Attach attribute expressions - the expression that generate values for a particular attribute
3> Create Objects which are instances of a template
4>Attaching template level expressions
5>Expression evaluation and result stage
"""
        chain = (
                {
                    "documentation": RunnablePassthrough(),
                    "prompt": RunnablePassthrough(),
                }
                | prompt
                | llm
        )
        # Invoke the retrieval chain with the query
        input_data = {
            "documentation": introduction,
            "question": query
        }
        result = chain.invoke(input_data)
        result = find_text_after_token(result.content, "Action")
        return result

    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Return None if an error occurs


def create_template(query: str):
    try:
        documentation = PineconeVectorStore(
            index_name=os.getenv("INDEX_NAME"), embedding=embeddings, namespace="create template"
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
        print(json_without_comment)
        return json_without_comment, response

    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Return None if an error occurs


def create_objects(query: str):
    try:
        documentation = PineconeVectorStore(
            index_name=os.getenv("INDEX_NAME"), embedding=embeddings, namespace="create object"
        )
        prompt1 = PromptTemplate.from_template(get_template_name_prompt)
        prompt2 = PromptTemplate.from_template(get_csv_lines)
        chain1 = (
                {
                    "input": RunnablePassthrough(),
                }
                | prompt1
                | llm
        )
        # Invoke the retrieval chain with the query
        chain2 = (
                {
                    "input": RunnablePassthrough(),
                }
                | prompt2
                | llm
        )

        result1 = chain1.invoke(input={"input": query})
        result2 = chain2.invoke(input={"input": query})
        csv_values = result2.content
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

        # Define your input data
        input_data = {
            "OBJECT_JSON_format": OBJECT_JSON_format,
            "csv": csv_values,
            "template JSON": template_json
        }

        # Ensure chain2 has the correct invoke method and pass the input correctly
        result = chain2.invoke(input_data)

        template_name = extract_value_from_json(template_json, "template_name")
        object_json_list = extract_object_json(result.content)
        object_json_list = update_key_in_json_list(object_json_list, "template_name", template_name)
        object_json_list = update_obj_name(object_json_list)
        result_string = "$".join(object_json_list)
        return object_json_list[0], result_string

    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Return None if an error occurs


def attach_template_expression(query: str):
    # identify the template name
    documentation = PineconeVectorStore(
        index_name=os.getenv("INDEX_NAME"), embedding=embeddings, namespace="template expression"
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
    result = chain.invoke(input={"input": query})
    template_name = find_text_after_token(result.content, "Template name")
    # identify the expression string conditional or arithmetic
    print(template_name)
    prompt2 = PromptTemplate.from_template(get_expression_string_and_type)

    chain2 = (
            {
                "documentation": documentation.as_retriever() | format_docs,
                "query": RunnablePassthrough(),
            }
            | prompt2
            | llm
    )

    result = chain2.invoke(input={"query": query})
    expression_string = find_text_after_token(result.content, "Expression String ")
    expression_type = find_text_after_token(result.content, "Expression Type ")
    print(expression_string)
    print(expression_type)

    prompt3 = PromptTemplate.from_template(get_expression_datatype)

    chain3 = (
            {
                "documentation": documentation.as_retriever() | format_docs,
                "query": RunnablePassthrough(),
            }
            | prompt3
            | llm
    )
    result = chain3.invoke(input={"query": query})
    expression_datatype = find_text_after_token(result.content, "Expression DataType ")
    print(expression_datatype)

    if expression_type == "Conditional":
        expression_json = f"""
        {{
            "name": "sample",
            "expressionString": "{expression_string}",
            "type": "Conditional",
            "dataType": "{expression_datatype}"
        }}
        """

    else:
        expression_json = f"""
                {{
                    "name": "sample",
                    "expressionString": "{expression_string}",
                    "type": "Arithmetic",
                    "dataType": "float"
                }}
                """
    print(expression_json)
    return expression_json, "Attached template"


if __name__ == "__main__":
    print("calling the llm ")
    # res = create_template(
    #     query="Create an Employee Template. Employee has ID(int) firstName lastName age gender (boolean) baseSalary totalSalary department"
    # )
    # res = identify_function(
    #     query="""
    #         Generate objects for template Library.
    #         Death on the Nile, Agatha Christie, 12.34,
    #         James Bond, Ian Fleming, 23.43
    #         Man eaters of kumaon, Jim Corbett, 56.67,
    #         Let us C, Yashwant Kanetkar, 100
    #     """
    # )
    # res2 = give_information(
    #     query=""" 'Give information' on the procedure to define a template.
    #             """
    # )
    # res = create_template(
    #     query="Explain the procedure to create a template. Also explain the JSON format for the template."
    # )
    res2 = create_objects(
        query="""
        Generate objects for template Library.
        Death on the Nile, Agatha Christie, 12.34,
        James Bond, Ian Fleming, 23.43
        Man eaters of kumaon, Jim Corbett, 56.67,
        Let us C, Yashwant Kanetkar, 100
    """
    )
    # attach_template_expression(
    #     query="""Attach a Conditional template expression with data type int to the template 'Employee'. The expression is
    #           'incomeTax == totalSalary'. """
    # )
