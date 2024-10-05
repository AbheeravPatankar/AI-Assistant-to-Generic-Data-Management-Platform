import json
import streamlit as st
from streamlit.components.v1 import html
from streamlit_chat import message
from core import *
from grpc_client import *

st.set_page_config(layout="wide")

def extract_attributes_and_template_expr(json_obj):
    filtered_data = []

    # Check for the "template" structure
    template_data = json_obj.get("template", {})
    template_name = template_data.get('template_name', '')

    # If template exists, process its attributes
    if template_name:  # Only add if template_name exists
        attributes = template_data.get('attributes', [])
        template_attr = []
        for attr in attributes:
            if 'attribute_name' in attr and 'attribute_type' in attr:
                template_attr.append({
                    'attribute_name': attr['attribute_name'],
                    'attribute_type': attr['attribute_type'],
                    'expression': attr.get('expression', "")
                })
        # Only add attributes if they exist
        if template_attr:
            filtered_data.append({
                'template_name': template_name,
                'attributes': template_attr
            })

    # Check for the Conditional structure with 'name', 'expressionString', etc.
    if 'name' in json_obj and 'expressionString' in json_obj:
        filtered_data.append({
            'name': json_obj['name'],
            'type': json_obj.get('type', ''),
            'expressionString': json_obj.get('expressionString', ''),
            'dataType': json_obj.get('dataType', '')
        })

    return filtered_data  # Return only relevant data


def json_to_html_tree_obj(json_obj):
    def json_to_html(json_obj, level=0):
        html_content = ""
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                # Generate prefix for indentation based on level
                prefix = "| " * level + "|_ "  # Uniformly use '|_ ' for all levels

                # If the value is a dictionary or list, recurse into it
                if isinstance(value, dict):
                    html_content += f'<li><span class="indentation">{prefix}<strong>{key}:</strong></span></li>'
                    html_content += f'<ul class="tree-list">{json_to_html(value, level + 1)}</ul>'
                elif isinstance(value, list):
                    html_content += f'<li><span class="indentation">{prefix}<strong>{key}:</strong></span></li>'
                    for item in value:
                        html_content += f'<ul class="tree-list">{json_to_html(item, level + 1)}</ul>'
                else:
                    # Print the key-value pair
                    html_content += f'<li><span class="indentation">{prefix}<strong>{key}:</strong> <span class="value">{value}</span></li>'
        elif isinstance(json_obj, list):
            for item in json_obj:
                html_content += json_to_html(item, level)
        return html_content

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
    .value {
        color: #333;
        font-family: monospace;
    }
    </style>
    """

    return f"{css}<div><ul class='tree-list'>{json_to_html(json_obj)}</ul></div>"


def json_to_html_tree_expr(json_obj):
    def json_to_html(json_obj, level=0):
        html_content = ""
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                # Generate prefix for indentation based on level
                prefix = "| " * level + "|_ "

                # If the value is a dictionary or list, recurse into it
                if isinstance(value, dict):
                    html_content += f'<li><span class="indentation">{prefix}<strong>{key}:</strong></span></li>'
                    html_content += f'<ul class="tree-list">{json_to_html(value, level + 1)}</ul>'
                elif isinstance(value, list):
                    html_content += f'<li><span class="indentation">{prefix}<strong>{key}:</strong></span></li>'
                    for item in value:
                        html_content += f'<ul class="tree-list">{json_to_html(item, level + 1)}</ul>'
                else:
                    # Print the key-value pair
                    html_content += f'<li><span class="indentation">{prefix}<strong>{key}:</strong> <span class="value">{value}</span></li>'
        elif isinstance(json_obj, list):
            for item in json_obj:
                html_content += json_to_html(item, level)
        return html_content

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
    .datatype {
        color: brown;
        font-family: monospace;
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

    return f"{css}<div><ul class='tree-list'>{json_to_html(json_obj)}</ul></div>"


# Function to extract attributes and template name
def extract_attributes_and_template(json_obj):
    filtered_data = []
    template_name = json_obj.get("template_name", "")

    if isinstance(json_obj, dict) and "attributes" in json_obj:
        attributes = json_obj["attributes"]
        for attr in attributes:
            if "attribute_name" in attr and "attribute_type" in attr:
                filtered_data.append({
                    "attribute_name": attr["attribute_name"],
                    "attribute_type": attr["attribute_type"],
                })

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
    .bool {
        color: blue;
    }
    .template-name {
        color: #333.
        font-family: monospace.
        font-weight: bold.
    }
    .value {
        color: #333.
        font-family: monospace.
    }
    .blue-button {
        background-color: #007bff.
        color: white.
        border: none.
        padding: 10px 20px.
        font-size: 16px.
        cursor: pointer.
        border-radius: 5px.
        text-align: center.
        display: inline-block.
        margin-top: 20px.
    }
    .blue-button:hover {
        background-color: #0056b3.
    }
    </style>
    """

    return f"{css}<div>{json_to_html(json_obj)}</div>"


# Streamlit Chat Header

col1, col2 = st.columns([6, 6])

with col1:
    st.header("Generic data management platform assistant")
    prompt = st.text_area("Prompt", placeholder="Enter the prompt...", height=200)

    if "prompt_history" not in st.session_state:
        st.session_state["prompt_history"] = []

    if "response_history" not in st.session_state:
        st.session_state["response_history"] = []

    if "response_json" not in st.session_state:
        st.session_state["response_json"] = []

    if "object_json" not in st.session_state:
        st.session_state["object_json"] = []

    if "flag" not in st.session_state:
        st.session_state["flag"] = []

    if prompt and st.session_state.get("last_prompt") != prompt:
        # Check if prompt is new and not the same as the last one
        st.session_state["last_prompt"] = prompt
        with st.spinner("Generating response...."):
            st.write("identifying Action .....")
            action = identify_function(prompt)

            if action == "Create Template":
                st.write("calling create_template.....")
                json_wc, response = create_template(query=prompt)
                st.write("Received response from LLM")
                st.session_state["prompt_history"].append(prompt)
                st.session_state["response_history"].append(response)
                st.session_state["response_json"].append(json_wc)
                st.session_state["flag"].append(0)

            elif action == "Attach Attribute Level Expressions":
                create_template(query=prompt)  # Attach Leevan's code on this line
                st.session_state["flag"].append(1)

            elif action == "Create Objects":
                st.write("calling create_object.....")
                first_json, list_json = create_objects(query=prompt)
                st.write("Received response from LLM")
                st.session_state["prompt_history"].append(prompt)
                st.session_state["response_history"].append("Produced objects")
                st.session_state["response_json"].append(first_json)
                st.session_state["object_json"].append(list_json)
                st.session_state["flag"].append(2)

            elif action == "Attach template expression":
                st.write("calling attach template expr.....")
                json, response = attach_template_expression(query=prompt)
                st.write("Received response from LLM")
                st.write(json)
                st.session_state["prompt_history"].append(prompt)
                st.session_state["response_history"].append(response)
                st.session_state["response_json"].append(json)
                st.session_state["flag"].append(3)

            elif action == "Give Information":
                st.write("calling give_information.....")
                st.session_state["prompt_history"].append(prompt)
                response = give_information(prompt)
                st.write("Received response from LLM")
                st.session_state["response_history"].append(response)
                st.session_state["flag"].append(4)

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

        first_key = get_first_key(last_json_data)
        if first_key == "template_name":
            if key_exists(last_json_data, "object_name"):
                json_obj = json.loads(last_json_data)
                filtered_json_obj = extract_attributes_and_template(json_obj)
                html_tree = json_to_html_tree(filtered_json_obj)
                html(html_tree, height=400)
            else:
                json_obj = json.loads(last_json_data)
                html_tree = json_to_html_tree_obj(json_obj)
                html(html_tree, height=400)
        elif first_key == "name":
            json_obj = json.loads(last_json_data)
            filtered_json_obj = extract_attributes_and_template_expr(json_obj)
            html_tree = json_to_html_tree_expr(filtered_json_obj)
            html(html_tree, height=400)

    if st.button("Authenticate"):
        if st.session_state["flag"][-1] == 0:
            st.write("Sending request create template")
            latest_json = st.session_state["response_json"][-1]  # JSON that is to be transferred
            route = "/create/template"  # API route (currently hardcoded)
            send_encrypted_request(latest_json, route)
        elif st.session_state["flag"][-1] == 2:
            st.write("Sending request create object")
            latest_json = st.session_state["object_json"][-1]  # JSON that is to be transferred
            route = "/create/object"  # API route (currently hardcoded)
            send_encrypted_request(latest_json, route)
