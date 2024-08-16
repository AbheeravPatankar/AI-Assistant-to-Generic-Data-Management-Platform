import streamlit as st
import json
from streamlit.components.v1 import html
import re
from streamlit_chat import message
from core import run_llm


# Function to extract attributes and template name
def extract_attributes_and_template(json_obj):
    """
    Extracts attribute names, types, and template name from JSON data.

    Args:
        json_obj (dict): JSON object to be processed.

    Returns:
        dict: Filtered JSON object with template_name and only attribute_name and attribute_type.
    """
    filtered_data = []
    template_name = json_obj.get("template_name", "")

    if isinstance(json_obj, dict) and "attributes" in json_obj:
        attributes = json_obj["attributes"]
        for attr in attributes:
            if "attribute_name" in attr and "attribute_type" in attr:
                filtered_data.append(
                    {
                        "attribute_name": attr["attribute_name"],
                        "attribute_type": attr["attribute_type"],
                    }
                )

    return {"template_name": template_name, "attributes": filtered_data}


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
                    items.append(
                        f'<li><span class="indentation">{prefix}<strong>{attr["attribute_name"]}:</strong> <span class="{attr["attribute_type"]}">{attr["attribute_type"]}</span></span></li>'
                    )
                html_content += f'<ul class="tree-list">{"".join(items)}</ul>'

            return html_content
        return ""

    # Add CSS for styling
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
    .integer {
        color: red;
    }
    .float {
        color: orange;
    }
    .boolean {
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
    </style>
    """

    return f"{css}<div>{json_to_html(json_obj)}</div>"


# Streamlit Chat Header


# Create two columns for the assistant's responses and the JSON tree representation
col1, col2 = st.columns([3, 3])

# Column 1: Assistant's responses
with col1:
    st.header("Generic data management platform assistant")
    prompt = st.text_input("Prompt", placeholder="Enter the prompt....")

    if "prompt_history" not in st.session_state:
        st.session_state["prompt_history"] = []

    if "response_history" not in st.session_state:
        st.session_state["response_history"] = []

    if "response_json" not in st.session_state:
        st.session_state["response_json"] = []

    if prompt:
        with st.spinner("Generating response...."):
            st.write("Calling LLM...")
            json_wc, response = run_llm(query=prompt)
            st.write("Received response from LLM")
            st.session_state["prompt_history"].append(prompt)
            st.session_state["response_history"].append(response)
            st.session_state["response_json"].append(json_wc)

    if st.session_state["response_history"]:
        for response, prompt in zip(
            st.session_state["response_history"], st.session_state["prompt_history"]
        ):
            st.write("Printing output .....")
            message(prompt, is_user=True)
            message(response)

# Column 2: JSON Tree Representation
with col2:
    st.title("JSON Tree Representation")
    # Render JSON data if available
    if st.session_state["response_json"]:
        # Retrieve the last JSON entry
        last_json_data = st.session_state["response_json"][-1]

        # Remove comments and parse JSON
        json_obj = json.loads(last_json_data)
        filtered_json_obj = extract_attributes_and_template(json_obj)

        # Convert to HTML tree and render
        html_tree = json_to_html_tree(filtered_json_obj)
        html(html_tree, height=400)
