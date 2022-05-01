#include "aes_gcm.h"


AESGCM:: ~AESGCM(){
    Cleanup();
}

// Freebie: initialize AES class
AESGCM::AESGCM( BYTE key[AES_256_KEY_SIZE]){
    hAlg = 0;
    hKey = NULL;

    // create a handle to an AES-GCM provider
    nStatus = ::BCryptOpenAlgorithmProvider(
        &hAlg, 
        BCRYPT_AES_ALGORITHM, 
        NULL, 
        0);
    if (! NT_SUCCESS(nStatus))
    {
        printf("**** Error 0x%x returned by BCryptOpenAlgorithmProvider\n", nStatus);
        Cleanup();
        return;
    }
    if (!hAlg){
        printf("Invalid handle!\n");
    }
    nStatus = ::BCryptSetProperty(
        hAlg, 
        BCRYPT_CHAINING_MODE, 
        (BYTE*)BCRYPT_CHAIN_MODE_GCM, 
        sizeof(BCRYPT_CHAIN_MODE_GCM), 
        0);
    if (!NT_SUCCESS(nStatus)){
         printf("**** Error 0x%x returned by BCryptGetProperty ><\n", nStatus);
         Cleanup();
         return;
    }
  

    nStatus = ::BCryptGenerateSymmetricKey(
        hAlg, 
        &hKey, 
        NULL, 
        0, 
        key, 
        AES_256_KEY_SIZE, 
        0);
    if (!NT_SUCCESS(nStatus)){
        printf("**** Error 0x%x returned by BCryptGenerateSymmetricKey\n", nStatus);
        Cleanup();
        return;
    }
    DWORD cbResult = 0;
     nStatus = ::BCryptGetProperty(
         hAlg, 
         BCRYPT_AUTH_TAG_LENGTH, 
         (BYTE*)&authTagLengths, 
         sizeof(authTagLengths), 
         &cbResult, 
         0);
    if (!NT_SUCCESS(nStatus)){
        printf("**** Error 0x%x returned by BCryptGetProperty when calculating auth tag len\n", nStatus);
    }

   
}


void AESGCM::Decrypt(BYTE* nonce, size_t nonceLen, BYTE* data, size_t dataLen, BYTE* macTag, size_t macTagLen){
    // change me

    BCRYPT_AUTHENTICATED_CIPHER_MODE_INFO authInfo;
    BCRYPT_INIT_AUTH_MODE_INFO(authInfo);
    authInfo.pbNonce = nonce;
    authInfo.cbNonce = nonceLen;
    authInfo.pbTag = macTag;
    authInfo.cbTag = macTagLen;

    // get the output buffer size
    nStatus = ::BCryptDecrypt(
        hKey,
        data,
        dataLen,
        &authInfo,
        nonce,
        nonceLen,
        NULL,
        0,
        &ptBufferSize,
        0
    );

    if (!NT_SUCCESS(nStatus)) {
        printf("Error decrypt 0x%x: could not get output buffer size\n", nStatus);
    } 

    plaintext = (BYTE *)malloc(ptBufferSize);

    if (plaintext == NULL) {
        printf("Error: could not allocate memory\n");
    }

    nStatus = ::BCryptDecrypt(
        hKey,
        data,
        dataLen,
        &authInfo,
        nonce,
        nonceLen,
        plaintext,
        ptBufferSize,
        &ptBufferSize,
        0
    );

    if (!NT_SUCCESS(nStatus)) {
        printf("Error 0x%x: could not decrypt\n", nStatus);
    } 

}

void AESGCM::Encrypt(BYTE* nonce, size_t nonceLen, BYTE* data, size_t dataLen){
   // change me

    ULONG bufferSize;

    // create a buffer for tag
    tag = (BYTE*)malloc(authTagLengths.dwMaxLength);

    if (tag == NULL) {
        printf("Error: could not allocate memory\n");
    }

    // initialize authentification info
    BCRYPT_AUTHENTICATED_CIPHER_MODE_INFO authInfo;
    BCRYPT_INIT_AUTH_MODE_INFO(authInfo);
    authInfo.pbNonce = nonce;
    authInfo.cbNonce = nonceLen;
    authInfo.pbTag = tag;
    authInfo.cbTag = authTagLengths.dwMaxLength;


    // get the output buffer size
    nStatus = ::BCryptEncrypt(
        hKey,
        data,
        dataLen,
        &authInfo,
        nonce,
        nonceLen,
        NULL,
        0,
        &bufferSize,
        0
    );

    if (!NT_SUCCESS(nStatus)) {
        printf("Error encrypt 0x%x: could not get output buffer size\n", nStatus);
    } 

    ciphertext = (BYTE*)malloc(bufferSize);
    ciphertextSize = bufferSize;

    if (ciphertext == NULL) {
        printf("Error: could not allocate memory\n");
    }

    ULONG result;
    nStatus = ::BCryptEncrypt(
        hKey,
        data,
        dataLen,
        &authInfo,
        nonce,
        nonceLen,
        ciphertext,
        bufferSize,
        &result,
        0
    );

    if (!NT_SUCCESS(nStatus)) {
        printf("Error 0x%x: could not encrypt\n", nStatus);
    } 

}

void AESGCM::Cleanup(){
    if(hAlg){
        ::BCryptCloseAlgorithmProvider(hAlg,0);
        hAlg = NULL;
    }
    if(hKey){
        ::BCryptDestroyKey(hKey);
        hKey = NULL;
    }
    if(tag){
          ::HeapFree(GetProcessHeap(), 0, tag);
          tag = NULL;
    }
    if(ciphertext){
        ::HeapFree(GetProcessHeap(), 0, tag);
        ciphertext = NULL;
    }
    if(plaintext){
        ::HeapFree(GetProcessHeap(), 0, plaintext);
        plaintext = NULL;
    }
}