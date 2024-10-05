import grpc
import mygrpc_pb2_grpc
import mygrpc_pb2
from crypto_utils import aes_encrypt, aes_decrypt
from Crypto.Random import get_random_bytes
import json


def send_encrypted_request(api_route, json_data):
    key = get_random_bytes(32)  #AES-256

    print("\n*** ENTERING LAYER 1 ***\n")
    print("Now setting up a gRPC channel...\n")
    channel = grpc.insecure_channel('192.168.205.231:9090')
    print("Creating a stub to send requests and receiving responses from the server...\n")
    stub = mygrpc_pb2_grpc.ReqResServiceStub(channel)

    # Convert API route and JSON data to string if not already a string
    api_route_str = json.dumps(api_route) if isinstance(api_route, dict) else api_route
    json_data_str = json.dumps(json_data) if isinstance(json_data, dict) else json_data

    print("Received API route and JSON from the LLM:")
    print("API Route:", api_route_str)
    print("\n")
    print("JSON Data:", json_data_str)
    print("-------------------------------------------------------------------\n")

    print("*** ENTERING LAYER 2- Encryption ***\n")
    print("Passing API route and JSON to encryption function...")
    iv_route, encrypted_route = aes_encrypt(api_route_str, key)
    iv_json, encrypted_json = aes_encrypt(json_data_str, key)
    print("Encrytped route: ", encrypted_route)
    print("\n")
    print("Encrytped JSON: ", encrypted_json)
    print("\n")
    print("Encrypted API route and JSON passed to the gRPC layer.")
    print("-------------------------------------------------------------------\n")

    print("*** ENTERING LAYER 3- gRPC Communication ***\n")
    # Create the gRPC request
    request = mygrpc_pb2.Request(route=encrypted_route, jsondata=encrypted_json)

    print("Sending the encrypted request to the server...\n")
    # Send request and receive encrypted response
    response = stub.SaveJson(request)
    print("Encrypted response received from server.\n")

    print("Decrypting the response from the server...\n")
    # Decrypt response
    decrypted_response = aes_decrypt(iv_json, encrypted_json, key)
    print("Decrypted server response:", decrypted_response)
    print("Decrypted response received from server.\n")

    print("Closing the communication channel.")
    channel.close()
    print("-------------------------------------------------------------------")
    return decrypted_response


if __name__ == '__main__':
    api_route = '/create/template'
    json_data = {
        "template_name": "Employee",
        "attributes": [
            {"attribute_name": "ID", "attribute_type": "int", "expression": None},
            {"attribute_name": "firstName", "attribute_type": "string", "expression": None},
            {"attribute_name": "lastName", "attribute_type": "string", "expression": None},
            {"attribute_name": "age", "attribute_type": "int", "expression": None},
            {"attribute_name": "gender", "attribute_type": "boolean", "expression": None},
            {"attribute_name": "baseSalary", "attribute_type": "int", "expression": None},
            {"attribute_name": "totalSalary", "attribute_type": "int", "expression": None},
            {"attribute_name": "department", "attribute_type": "string", "expression": None}
        ],
        "expressionList": []
    }

    json_data_str = json.dumps(json_data)

    #Send the request and process the response
    response = send_encrypted_request(api_route, json_data_str)
    #print("Final response to UI:", response)
    print("Final response to UI received!")
