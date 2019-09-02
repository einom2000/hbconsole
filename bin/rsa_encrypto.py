from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP


def encryption(data, recipient_pub, crypted_file):  # key in PEM
    recipient_key = RSA.importKey(recipient_pub)
    session_key = get_random_bytes(16)
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data.encode('utf-8'))

    with open(crypted_file, 'wb') as f:
        [f.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)]
    return


def decryption(crypted_file, local_pri): # key in PEM
    private_key = RSA.import_key(local_pri)
    with open(crypted_file, 'rb') as f:
        enc_s_key, nonce, tag, ciphered = [f.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]

    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_s_key)

    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphered, tag)
    return data.decode("utf-8")


def main():
    print('there is no main here!')


if __name__ == '__main__':
    main()
