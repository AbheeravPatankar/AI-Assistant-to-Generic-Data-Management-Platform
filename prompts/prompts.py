get_template_name_prompt = """
    From the given query generate response by identifying the template name and extracting the COMMA SEPARATED VALUES.
    Generate response only from the information provided in the query given below.
    {input}
    Generate response only in the below given format:
    Template name: 
    CSV values : (could be multiple lines)
    Use a '$' sign at the start of every csv line and end the line with a '$' sign. Put the $ sign after every line not 
    after every comma separated value. 
    Use the above output format for all the csv lines 
    Do not make up a response if adequate information is not available in the prompt. 
"""


create_template_prompt = """  
    Answer any user questions based solely on the context below:
    {documentation}
    Question: {question} 
    Strictly generate a response only in the following format:
    Action: (The Action mentioned in the documentation)
    JSON body : The JSON created from the information provided in the prompt.
    Description :  description of the action
    The response generated should only follow the above format.
"""

template = {
  "template_name": "",
  "attributes": [
    {
      "attribute_name": "",
      "attribute_type": "",
      "expression": ""
    },
    {
      "attribute_name": "",
      "attribute_type": "",
      "expression": ""
    },
    {
      "attribute_name": "",
      "attribute_type": "",
      "expression": ""
    }
  ],
  "expressionList": [
    {
      "dataType": "",
      "name": "",
      "expressionString": "",
      "type": ""
    }
  ]
}

attach_expression_template_prompt = """
Fill the expression in the template json provided. Do not modify the template. Only fill the template with the values.
The template is given below : 
{template}
Strictly generate a response only in the following format:
    Action: 
    JSON body : The JSON created from the information provided in the prompt.
    Description :  description of the action
Do not add unnecessary expressions where not asked to.
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

sample_template_2 = """Do as the user says 
    This is the question
    {question}
    This is the input
    {input}
    Do not add uncessary pleasantries. Reply in a way that you are talking to the human. Only output the entire summary.
"""


OBJECT_JSON_format = """
    {
  "obj_template": "",
  "obj_name": "",
  "attributes": [
    {
      "val": ,
      "name": "",

    },
    {
      "val": "",
      "name": "",

    },
    {
      "val": ,
      "name": "",

    }
  ]
}
"""
