from UI import *

# Set page layout to wide
st.set_page_config(layout="wide")


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
    .scrollable-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 8px;
    }
    .chat-container {
        background-color: #f9f9f9;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .user-message {
        background-color: #e0f7fa;
        padding: 8px;
        border-radius: 8px;
        margin-bottom: 5px;
    }
    .assistant-message {
        background-color: #f1f8e9;
        padding: 8px;
        border-radius: 8px;
        margin-bottom: 5px;
    }
    </style>
    """

    return f"{css}<div class='scrollable-container'>{json_to_html(json_obj)}</div>"


# # Streamlit Sidebar
# st.sidebar.header("Options")
# st.sidebar.markdown("""
# - You can adjust settings here or view instructions.
# """)

pg_markdown = """
<style>

[data-testid="stHeader"]
{
background-color : rgba(0,0,0,0);
}
 [data-testid="stAppViewContainer"] {

    background: #6F919C;

 }    
    h1 {
        background-color: #fffff;
        color: white;
        padding: 10px;
        text-align: center;
        border-radius: 8px;
    }
</style>
"""

# Main Layout
st.title("Generic Data Management Assistant")

st.markdown(pg_markdown, unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])

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
