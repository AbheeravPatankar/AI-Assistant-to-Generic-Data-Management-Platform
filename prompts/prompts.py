get_template_name_prompt = """
    From the given query generate response by identifying the template name .
    Generate response only from the information provided in the query given below.
    {input}
    Generate response only in the below given format:
    Template name:  
    Do not make up a response if adequate information is not available in the prompt. 
"""

get_csv_lines = """
    From the given query below extract the CSV content.
    Print only the CSV lines in the output and strictly nothing else.
    Print each CSV line from the input separately in the output also.
    Print nothing else other than the CSV content.
    Below is the user query
    {input}
"""
get_expression_string_and_type = """
    Use the below given documentation to gain information on template expression and the types of template expressions.
    {documentation}
    Extract the expression string.
    Extract the expression type (Conditional or Arithmetic) as mentioned in the above documentation.
    Perform the above mentioned tasks using the below given user query.
    {query}
    If the insufficient information is available to don make up a response instead ask the user to provide sufficient 
    information.
    Generate a response only in the following format
    Expression String : Put the identified expression string over here
    Expression Type : Put the identified expression type over here(Conditional/Arithmetic). 
    DO NOT WRITE ANYTHING ELSE IN THE RESPONSE
"""

get_expression_datatype = """
    Use the below given documentation to gain information on template expression and the types of template expressions.
    {documentation}
    Extract the data type for the expression string. The data type can only be int ,char, string, float, boolean, double. 
    Perform the above mentioned tasks using the below given user query.
    {query}
    If the insufficient information is available to don make up a response instead ask the user to provide sufficient 
    information.
    Generate a response only in the following format
    Expression DataType : Put the identified expression type over here(int ,char, string, float, boolean, double). 
    DO NOT WRITE ANYTHING ELSE IN THE RESPONSE
"""

create_template_prompt = """  
    Answer any user questions based solely on the context below:
    {documentation}
    Question: {question} 
    Strictly generate a response only in the following format:
    Action: (The Action mentioned in the documentation)
    JSON Body : The JSON created from the information provided in the prompt.
    Description :  description of the action
    The response generated should only follow the above format.
"""


create_object_from_template = """
    To fill the OBJECT_JSON refer to the below template json.
    {template JSON}.
    Generate object JSONs for the following comma separated values.
    {csv}
    Refer to the below documentation to create object JSONs using the template JSON
    {documentation}
    To create OBJECT JSONs use the below given JSON format.
    {OBJECT_JSON_format}
    Generate a JSON for each csv line. 
    Output multiple JSONs if there are more than one lines with csv entries.
    DO NOT OUTPUT A PYTHON CODE. ONLY OUTPUT THE JSON FOR EACH CSV LINE.
    START EACH JSON WITH a '$$' sign and end each JSON with '$$' sign. 
    ALSO FORMAT THE JSON PROPERLY.
"""

sample_template = """Answer the users question only based on the below context
    {documentation}
    This is the question
    {question}
"""


define_operation_prompt = """
    Answer the question only based on the context given below.
    From the given prompt below try to define the action the user want to perform.
    These are the possible actions user can perform.
    Create Template : The user expects the llm to create a template and provides necessary information to create a Template.
    Create Objects : The user passes real time csv values which assign to a particular Template.
    Attribute expression : The user attaches an expression specific to a particular attribute.
        NOTE: For this action the user will specify the attribute to which the expression must be attached.
    Attach template expression : Here the user wants to attach an expression to the template.  
        NOTE : Here the user will only provide the template name with the type of the expression.
    Give Information : User Expects information about the system.
    User prompt: {prompt}
    Generate response in the given format 
    Action:(The action only among the actions defined above.)
"""


OBJECT_JSON_format = """
    {
  "template_name": "",
  "object_name": "",
  "attributes": [
    {
      "attribute_value": ,
      "attribute_name": "",

    },
    {
      "attribute_value": "",
      "attribute_name": "",

    },
    {
      "attribute_value": ,
      "attribute_name": "",

    }
  ]
}

"""

give_information_prompt = """
    Below is the documentation for the processes required to work on the Data Management Platform.
    Create Template Documentation: {create_template_doc}
    Create Object Documentation : {create_obj_doc}
    Respond to the user query only py providing information given in the above documentations.
    Question : {question}
    Do not provide the JSON in the output
    Give a response only under 100 words.And give a point wise response
"""