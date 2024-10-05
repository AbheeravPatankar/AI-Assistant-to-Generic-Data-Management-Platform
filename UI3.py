
import streamlit as st
from dataclasses import dataclass
from typing import Literal
from core import attach_expression, create_template, remove_json
import streamlit.components.v1 as components
from streamlit.components.v1 import html
import json

st.set_page_config(layout="wide")


@dataclass
class Message:
    """Class for keeping track of chat messages."""
    origin: Literal["human", "ai"]
    message: str


def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "conversation" not in st.session_state:
        st.session_state.conversation = attach_expression
    if "response_json" not in st.session_state:
        st.session_state["response_json"] = []
        


def on_click_callback():
    
    human_prompt = st.session_state.human_prompt
    json_string, llm_response =  attach_expression(human_prompt)
    llm_response = st.session_state.conversation(llm_response
       )
    
    try:
        json_string = json.loads(json_string)
        st.session_state["response_json"].append(json_string)
    except json.JSONDecodeError:
        pass
    st.session_state.history.append(Message("human", human_prompt))
    st.session_state.history.append(Message("ai", llm_response))


def load_css():
    with open("static/styles.css", "r") as f:
        css = f"<style> {f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)


def extract_attributes_and_template(json_obj):
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


def json_to_html_tree(json_obj):
    def json_to_html(json_obj, level=0):
        if isinstance(json_obj, dict):
            template_name = json_obj.get("template_name", "")
            attributes = json_obj.get("attributes", [])

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
    .expression {
        color: purple;
        font-family: monospace;
        font-style: italic;
        margin-left: 10px;
    }
    .scrollable-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 8px;
    }
    </style>
    """

    return f"{css}<div class='scrollable-container'>{json_to_html(json_obj)}</div>"


load_css()
initialize_session_state()

st.title("Data Management Chat Bot")

# Define the two columns, ensure proper ratio for width
col1, col2 = st.columns([2, 5])

# Left column (col1) for JSON tree representation
with col1:
    st.subheader("JSON Tree Representation")
    if st.session_state["response_json"]:
        last_json_data = st.session_state["response_json"][-1]

        # Extract attributes and template
        filtered_json_obj = extract_attributes_and_template(last_json_data)

        # Convert JSON to HTML tree
        html_tree = json_to_html_tree(filtered_json_obj)
        html(html_tree, height=400)

# Right column (col2) for chat
with col2:
    # st.subheader("Chat")
    with st.container():  # Wrap chat in a container for better layout control
        for chat in st.session_state.history:
            if isinstance(chat.message, dict):
                # Display JSON message using st.json()
                st.markdown(f"**{chat.origin.capitalize()}**:")
                st.json(chat.message)
            else:
                message = remove_json(chat.message) if chat.origin == 'ai' else chat.message
                div = f"""<div class="chat-row {'' if chat.origin == 'ai' else 'row-reverse'}">
                <img src="app/static/{'bot.png' if chat.origin == 'ai' else 'user.png'}" width="32" height="32" />
                <div class="chat-bubble {'ai-bubble' if chat.origin == 'ai' else 'human-bubble'}"> &#8203;{message}</div></div>"""
                st.markdown(div, unsafe_allow_html=True)

    # Form for submitting user input
    with st.form("chat-form"):
        st.markdown("**Chat** - _press Enter to Submit_")
        cols = st.columns((6, 1))
        cols[0].text_input("Chat", placeholder="Write your prompt here", label_visibility="collapsed", key="human_prompt")
        cols[1].form_submit_button("Submit", type="primary", on_click=on_click_callback)

# JavaScript to handle Enter key submit
components.html("""
<script>
const streamlitDoc = window.parent.document;

const buttons = Array.from(
    streamlitDoc.querySelectorAll('.stButton > button')
);
const submitButton = buttons.find(
    el => el.innerText === 'Submit'
);

streamlitDoc.addEventListener('keydown', function(e) {
    switch (e.key) {
        case 'Enter':
            submitButton.click();
            break;
    }
});
</script>
""", height=0, width=0)
