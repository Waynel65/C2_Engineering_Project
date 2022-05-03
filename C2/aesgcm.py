import os

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

# key = os.urandom(32)

# iv, ciphertext, tag = encrypt(
#     key,
#     b"a secret message!"
# )

# print(decrypt(
#     key,
#     iv,
#     ciphertext,
#     tag
# ))


# if __name__ == "__main__":
#     key = b"\x41\x13\xcd\xa3\xa0\xe0\xab\x5e\x19\xf1\xc0\x1c\x6d\x4e\x77\xc5\xe5\x20\xd2\x44\x0e\x52\xae\x87\xaa\x0a\x96\x67\x28\x82\xea\x08"
#     iv = b"\x87\xb8\xa9\xa6\xc2\x39\x42\x5f\xc2\xda\x8c\xc1"
#     ciphertext = b"\x30\x83\x55\xb2\x0c\x95\x50\x61\xe7\xc5\x8f\x72\x57\x77\x56\xc7"
#     tag = b"\x99\xb5\x76\xb0\x01\x2e\x7f\xc7\xcf\x69\x57\x5e\xc8\x54\x09\x39"
#     print(decrypt(key, iv, ciphertext, tag))
#     # iv, ct, tag = encrypt(key, b"hello")
#     # print(len(tag))