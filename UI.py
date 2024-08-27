import json
import streamlit as st
from streamlit.components.v1 import html
from streamlit_chat import message
from core import *
# from grpc_client import send_encrypted_request

# Function to extract attributes and template name
def extract_attributes_and_template(json_obj):
    """
    Extracts attribute names, types, expressions, and template name from JSON data.

    Args:
        json_obj (dict): JSON object to be processed.

    Returns:
        dict: Filtered JSON object with template_name and attributes.
    """
    filtered_data = []
    template_name = json_obj.get("template", {}).get('template_name', '')

    attributes = json_obj.get("template", {}).get('attributes', [])
    for attr in attributes:
        if 'attribute_name' in attr and 'attribute_type' in attr:
            filtered_data.append({
                'attribute_name': attr['attribute_name'],
                'attribute_type': attr['attribute_type'],
                'expression': attr.get('expression', "")
            })

    return {'template_name': template_name, 'attributes': filtered_data}


# Function to convert JSON to HTML tree with styling
def json_to_html_tree(json_obj):
    def json_to_html(json_obj, level=0):
        if isinstance(json_obj, dict):
            template_name = json_obj.get("template_name", "")
            attributes = json_obj.get("attributes", [])

            # Display template_name
            html_content = f'<h2>Template Name: <span class="template-name">{template_name}</span></h2>'

            if attributes:
                items = []
                for index, attr in enumerate(attributes):
                    prefix = "| " * level + "|_ "
                    expression = attr.get("expression", "")

                    if expression:
                        items.append(
                            f'<li><span class="indentation">{prefix}<strong>{attr["attribute_name"]}:</strong> <span class="{attr["attribute_type"]}">{attr["attribute_type"]}</span></span> <span class="expression">Expression: {expression}</span></li>'
                        )
                    else:
                        items.append(
                            f'<li><span class="indentation">{prefix}<strong>{attr["attribute_name"]}:</strong> <span class="{attr["attribute_type"]}">{attr["attribute_type"]}</span></span></li>'
                        )

                html_content += f'<ul class="tree-list">{"".join(items)}</ul>'

            return html_content
        return ""

    css = """
    <style>
    .tree-list {
        list-style-type: none;
        margin: 0;
        padding: 0;
    }
    .tree-list li {
        margin: 5px 0;
        padding-left: 20px;
        position: relative;
    }
    .tree-list ul {
        margin-left: 20px;
        padding-left: 10px;
    }
    .indentation {
        font-family: monospace;
    }
    .string {
        color: green;
    }
    .int {
        color: red;
    }
    .float {
        color: orange;
    }
    .double {
        color: purple;
    }
    .bool {
        color: blue;
    }
    .template-name {
        color: #333;
        font-family: monospace;
        font-weight: bold;
    }
    .value {
        color: #333;
        font-family: monospace;
    }
    .expression {
        color: purple;
        font-family: monospace;
        font-style: italic;
        margin-left: 10px;
    }
    .blue-button {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
        border-radius: 5px;
        text-align: center;
        display: inline-block;
        margin-top: 20px;
    }
    .blue-button:hover {
        background-color: #0056b3;
    }
    </style>
    """

    return f"{css}<div>{json_to_html(json_obj)}</div>"


# Streamlit Chat Header

col1, col2 = st.columns([3, 3])

with col1:
    st.header("Generic data management platform assistant")
    prompt = st.text_input("Prompt", placeholder="Enter the prompt....")

    if "prompt_history" not in st.session_state:
        st.session_state["prompt_history"] = []

    if "response_history" not in st.session_state:
        st.session_state["response_history"] = []

    if "response_json" not in st.session_state:
        st.session_state["response_json"] = []

    if prompt and st.session_state.get("last_prompt") != prompt:
        # Check if prompt is new and not the same as the last one
        st.session_state["last_prompt"] = prompt
        with st.spinner("Generating response...."):
            st.write("Calling LLM...")
            json_wc, response = attach_expression(query=prompt)
            st.write("Received response from LLM")
            st.session_state["prompt_history"].append(prompt)
            st.session_state["response_history"].append(response)
            st.session_state["response_json"].append(json_wc)

    if st.session_state["response_history"]:
        for i, (response, prompt) in enumerate(
                zip(st.session_state["response_history"], st.session_state["prompt_history"])):
            st.write("Printing output .....")
            message(prompt, is_user=True, key=f"user_{i}")
            message(response, key=f"response_{i}")

with col2:
    st.title("JSON Tree Representation")

    if st.session_state["response_json"]:
        last_json_data = st.session_state["response_json"][-1]

        json_obj = json.loads(last_json_data)
        filtered_json_obj = extract_attributes_and_template(json_obj)

        html_tree = json_to_html_tree(filtered_json_obj)
        html(html_tree, height=400)

    if st.button("Authenticate"):
        st.write("Sending request and JSON to the API")
        latest_json = st.session_state["response_json"][-1]   # JSON that is to be transferred
        route = "/create/template"                            # API route (currently hardcoded)
        # Pass the latest JSON and the route to the grpc layer to generate a request for the web application
# send_encrypted_request(latest_json, route) #Calls the gRPC layer function to encrypt and send the data
