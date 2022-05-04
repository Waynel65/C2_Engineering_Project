import os
import json
from c2_config import iv_len, aes_key, tag_len

from cryptography.hazmat.primitives.ciphers import (
    Cipher, algorithms, modes
)

def encrypt(key, plaintext):
    # Generate a random 96-bit IV.
    iv = os.urandom(12)

    # Construct an AES-GCM Cipher object with the given key and a
    # randomly generated IV.
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
    ).encryptor()

    # Encrypt the plaintext and get the associated ciphertext.
    # GCM does not require padding.
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    return (iv, ciphertext, encryptor.tag)

def decrypt(key, iv, ciphertext, tag):
    # Construct a Cipher object, with the key, iv, and additionally the
    # GCM tag used for authenticating the message.
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
    ).decryptor()

    # return the decrypted plaintext
    return decryptor.update(ciphertext) + decryptor.finalize()

def serialize(iv, tag, ct):
    """
        function to serialize response data
    """

    res = iv + tag + ct

    return res

def deserialize(byte_str):
    """
        function to deserialize request data
    """
    res = {}
    res["iv"] = byte_str[:iv_len]
    res["tag"] = byte_str[iv_len:tag_len + iv_len]
    res["cipher"] = byte_str[iv_len + tag_len:]
    return res

def decrypt_data(byte_str):

    data = deserialize(byte_str)
    
    plaintext = decrypt(aes_key, data["iv"], data["cipher"], data["tag"])

    plaintext = json.loads(plaintext.decode())

    return plaintext

def encrypt_data(data):

    byte_data = json.dumps(data).encode()
    iv, ct, tag = encrypt(aes_key, byte_data)
    serialized = serialize(iv, tag, ct)
    # print("type of serialized: ", type(serialized))
    return serialized

def encrypt_shellcode(shellcode):
    iv, ct, tag = encrypt(aes_key, shellcode)
    serialized = serialize(iv, tag, ct)
    # print("type of serialized: ", type(serialized))
    return serialized