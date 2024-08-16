get_template_name_prompt = """
    Answer any use questions based solely on the context below:
    {documentation}
    Do not generate the JSON body if template information or object information does not exist.
    Answer the question only in the given format
    template_name: (The name of the template for which the objects are to be created)
    csv_values: (The comma separated object information.)
    Generate the above input using the following input.
    {question} 
    If enough information is not available prompt the user to provide more information.
    Do not make up a response.
"""

create_template_prompt = """
    Answer any use questions based solely on the context below:
    Do not generate the JSON body if template information does not exist. 
    {documentation}
    Try to answer the question in this format
    Description:
    JSON body: The attribute_type is decided based on the attribute_name.
    Question: {question}
    Generate the JSON body if enough information is available.
    Do not fill the JSON body if information is unavailable instead prompt the user to feed more information.
    Do not assign attributes to the expression list or the expression attribute until not specified.
    The attribute_type property cannot be null in the JSON.This property is decided by the llm judging at the attribute_name 
    property.
"""


create_object_from_template = """
    Only use the below JSON to create object json.
    This is the template JSON.
    {template JSON}
    The object shall be created using the below given JSON format
    {OBJECT_JSON_format} 
    Also refer to the below documentation to create object JSONs using the template JSON
    {documentation}
    Generate object JSONs for the following comma separated values.
    {csv}
    Generate a JSON for each csv line. 
    Output multiple JSONs if there are more than one lines with csv entries.
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
