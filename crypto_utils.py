from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import json
import base64

def aes_encrypt(plaintext, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(plaintext.encode('utf-8'), AES.block_size))
    iv_b64 = base64.b64encode(cipher.iv).decode('utf-8')  # Base64 encode the IV during encryption
    ct_b64 = base64.b64encode(ct_bytes).decode('utf-8')  # Base64 encode the ciphertext to be decrypted
    return iv_b64, ct_b64

def aes_decrypt(iv_b64, ct_b64, key):
    iv = base64.b64decode(iv_b64)
    ct = base64.b64decode(ct_b64)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode('utf-8')

if __name__ == "__main__":
    route = "/create/template"
    original_message = {
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
    print("\n")
    json_message = json.dumps(original_message)  #convert JSON to string

    # Generate a random AES key for encryption
    key = get_random_bytes(32)  # AES-256

    # Encrypt the JSON message
    iv_message, ciphertext_message = aes_encrypt(json_message, key)
    print("Encrypted JSON:", ciphertext_message)  
    print("\n")

    # Encrypt the route
    iv_route, ciphertext_route = aes_encrypt(route, key)
    print("Encrypted route:", ciphertext_route)  
    print("\n")

    # Decrypt the message
    decrypted_message = aes_decrypt(iv_message, ciphertext_message, key)
    print("Decrypted JSON:", decrypted_message)
    print("\n")

    # Decrypt the route
    decrypted_route = aes_decrypt(iv_route, ciphertext_route, key)
    print("Decrypted route:", decrypted_route)
