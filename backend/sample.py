import re


def remove_json_comments(json_str):
    """
    Remove comments from JSON string.

    Args:
        json_str (str): The JSON string with comments.

    Returns:
        str: The JSON string without comments.
    """
    # Remove single-line comments
    json_str = re.sub(r"//.*", "", json_str)

    # Remove multi-line comments
    json_str = re.sub(r"/\*.*?\*/", "", json_str, flags=re.DOTALL)

    return json_str


def extract_and_remove_json(input_string, token):
    # Find the start of the JSON body
    start_index = input_string.find(token)

    if start_index == -1:
        start_index = input_string.find("JSON body:")
        if start_index == -1:
            return None, input_string

    # Find the start of the JSON block
    json_start_index = input_string.find("{", start_index)

    if json_start_index == -1:
        return None, input_string

    # Find the end of the JSON block
    json_end_index = input_string.rfind("}", json_start_index)

    if json_end_index == -1:
        return None, input_string

    # Extract the JSON substring
    json_string = input_string[json_start_index : json_end_index + 1].strip()

    # Find and preserve the "action:" and "description:" tags
    action_tag = "Action:"
    description_tag = "Description:"

    action_index = input_string.find(action_tag)
    description_index = input_string.find(description_tag)

    # Extract the text up to the start of JSON
    text_before_json = input_string[:start_index].strip()

    # Initialize preserved text as empty
    preserved_text = ""

    if action_index != -1:
        # Extract the action tag section
        action_end_index = input_string.find("\n", action_index)
        if action_end_index == -1:
            action_end_index = len(input_string)
        preserved_text += (
            input_string[action_index : action_end_index + 1].strip() + "\n"
        )

    if description_index != -1:
        # Extract the description tag section
        description_end_index = input_string.find("\n", description_index)
        if description_end_index == -1:
            description_end_index = len(input_string)
        preserved_text += (
            input_string[description_index : description_end_index + 1].strip() + "\n"
        )

    # Remove the JSON body and everything before it from the original input string
    text_after_json = input_string[json_end_index + 1 :].strip()

    # Combine preserved text with text after JSON
    result_text = preserved_text + text_after_json

    return json_string, result_text
