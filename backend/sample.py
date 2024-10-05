import re
import json


def update_obj_name(json_strings):
    updated_json_strings = []

    for index, json_str in enumerate(json_strings):
        try:
            # Load the JSON data into a Python dictionary
            data = json.loads(json_str)

            # Update the 'obj_name' key with a new value
            data['object_name'] = f"obj{index + 1}"

            # Convert the updated dictionary back to a JSON string
            updated_json_str = json.dumps(data, indent=4)
            updated_json_strings.append(updated_json_str)
        except json.JSONDecodeError:
            # Handle invalid JSON
            print(f"Invalid JSON data: {json_str}")
            updated_json_strings.append(json_str)

    return updated_json_strings


def key_exists(json_obj, key_to_find):
    # If the JSON object is a dictionary, check its keys
    if isinstance(json_obj, dict):
        if key_to_find in json_obj:
            return True  # Key found
        # Recursively check in each value
        for value in json_obj.values():
            if key_exists(value, key_to_find):
                return True
    return False


def get_first_key(json_data):
    json_data = json.loads(json_data)
    if isinstance(json_data, dict):

        return list(json_data.keys())[0]
    else:
        return None


def find_text_after_token(text, token):
    pattern = f"{token}:\s*(.*)"

    # Find all matches in the text
    matches = re.findall(pattern, text)

    # Print the matches
    for match in matches:
        return match


def update_key_in_json_list(json_list, key, new_value):
    updated_json_list = []

    for json_str in json_list:
        try:
            # Load the JSON data into a Python dictionary
            data = json.loads(json_str)

            # Update the value for the specified key
            data[key] = new_value

            # Convert the updated dictionary back to a JSON string
            updated_json_str = json.dumps(data, indent=4)
            updated_json_list.append(updated_json_str)
        except json.JSONDecodeError:
            # Handle invalid JSON
            print(f"Invalid JSON data: {json_str}")
            updated_json_list.append(json_str)

    return updated_json_list


def extract_value_from_json(json_str, key):
    try:
        # Load the JSON data into a Python dictionary
        data = json.loads(json_str)

        # Extract and return the value for the specified key
        return data.get(key, None)
    except json.JSONDecodeError:
        # Handle invalid JSON
        print("Invalid JSON data")
        return None


def extract_object_json(text):
    pattern = r'\$\$([\s\S]*?)\$\$'

    # Find all matches
    matches = re.findall(pattern, text)

    # Strip leading/trailing whitespace from each match
    raw_json_list = [match.strip() for match in matches]

    return raw_json_list


def parse_csv(input_text):
    # Use regular expression to find all values between $ signs
    csv_values = re.findall(r'\$(.*?)\$', input_text)

    # Join these values with a newline character to create the CSV string
    csv_string = "\n".join(csv_values)

    return csv_string


def remove_json_comments(json_str):
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
    json_string = input_string[json_start_index: json_end_index + 1].strip()

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
                input_string[action_index: action_end_index + 1].strip() + "\n"
        )

    if description_index != -1:
        # Extract the description tag section
        description_end_index = input_string.find("\n", description_index)
        if description_end_index == -1:
            description_end_index = len(input_string)
        preserved_text += (
                input_string[description_index: description_end_index + 1].strip() + "\n"
        )

    # Remove the JSON body and everything before it from the original input string
    text_after_json = input_string[json_end_index + 1:].strip()

    # Combine preserved text with text after JSON
    result_text = preserved_text + text_after_json

    return json_string, result_text
