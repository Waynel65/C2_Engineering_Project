#include <windows.h>
#include <string>
#include <vector>
#include <iostream>
#include <winhttp.h>
#include "http.h"
#include "aes_gcm.h"

BYTE key[] = {0x41, 0x13, 0xcd, 0xa3, 0xa0, 0xe0, 0xab, 0x5e, 0x19, 0xf1, 0xc0, 0x1c, 0x6d, 0x4e, 0x77, 0xc5, 0xe5, 0x20, 0xd2, 0x44, 0xe, 0x52, 0xae, 0x87, 0xaa, 0xa, 0x96, 0x67, 0x28, 0x82, 0xea, 0x8};

void printBytes(BYTE* bytes, int size) {
    for (int i = 0; i < size; i++) {
        if (i == 12 || i == 28) {
            printf("\n");
        }
        printf("\\x%x", bytes[i]);
    }
    printf("\n");
}

// encrypt the payload to a byte array
std::vector<BYTE> encryptPayload(std::string message) {
    BYTE textIV[] = {0x87, 0xb8, 0xa9, 0xa6, 0xc2, 0x39, 0x42, 0x5f, 0xc2, 0xda, 0x8c, 0xc1};
    
    BYTE* ptMessage = (BYTE*)message.data();
    DWORD messageSize = message.size();

    auto box = new AESGCM(key);

    box->Encrypt( (BYTE*) textIV, sizeof(textIV), ptMessage, messageSize);

    BYTE* ciphertext = (BYTE*) malloc(box->ciphertextSize);
    int ciphertextSize = box->ciphertextSize;
    std::copy(box->ciphertext, box->ciphertext + box->ciphertextSize, ciphertext);

    BYTE* tag = (BYTE*) malloc(16);
    std::copy(box->tag, box->tag + 16, tag);

    std::vector<BYTE> encryptedBytes;
    encryptedBytes.insert(encryptedBytes.end(), textIV, textIV + 12);
    encryptedBytes.insert(encryptedBytes.end(), box->tag, box->tag + 16);
    encryptedBytes.insert(encryptedBytes.end(), ciphertext, ciphertext + ciphertextSize);

    // printBytes(encryptedBytes.data(), encryptedBytes.size());

    // delete box;

    return encryptedBytes;
}

std::string decryptPayload(std::vector<BYTE> payload) {
    auto box = new AESGCM(key);
    DWORD ciphertextSize = payload.size() - 28;

    BYTE* iv = (BYTE*) malloc(12);
    BYTE* tag = (BYTE*) malloc(16);
    BYTE* ciphertext = (BYTE*) malloc(ciphertextSize);

    std::copy(payload.begin(), payload.begin() + 12, iv);
    std::copy(payload.begin() + 12, payload.begin() + 28, tag);
    std::copy(payload.begin() + 28, payload.end(), ciphertext);

    // printBytes(iv, 12);
    // printBytes(tag, 16);
    // printBytes(ciphertext, ciphertextSize);

    box->Decrypt(iv, 12, ciphertext, ciphertextSize, tag, 16);

    std::string message(box->plaintext, box->plaintext + box->ptBufferSize);

    free(iv);
    free(tag);
    free(ciphertext);

    return message;
}

std::string httpGet(LPCWSTR fqdn, int port, LPCWSTR uri, BOOL useTLS){
    return httpRequest(L"GET", fqdn, port, uri, "", useTLS);
}

std::string httpPost(LPCWSTR fqdn, int port, LPCWSTR uri, std::string data, BOOL useTLS) {
    return httpRequest(L"POST", fqdn, port, uri, data, useTLS);
}

/**
 * @brief make an http request
 * 
 * @param verb http verb, eg. GET, POST
 * @param fqdn domain name
 * @param port port number
 * @param uri  uri
 * @param data optional data used only in POST request
 * @return std::string data receive from server
 */
std::string httpRequest(LPCWSTR verb, LPCWSTR fqdn, int port, LPCWSTR uri, std::string data, BOOL useTLS){
    std::vector<BYTE> result;

    HINTERNET hSession = WinHttpOpen(
        L"sample",
        WINHTTP_ACCESS_TYPE_NO_PROXY,
        WINHTTP_NO_PROXY_NAME,
        WINHTTP_NO_PROXY_BYPASS,
        0);

    if (hSession == NULL) {
        printf("Error %d: could not create http session\n", GetLastError());
        return "Error";
    } 

    HINTERNET hConnect = WinHttpConnect(
        hSession,
        fqdn,
        port,
        0
    );

    if (hConnect == NULL) {
        printf("Error %d: could not connect to server\n", GetLastError());
        return "Error";
    } 

    DWORD tlsFlag;
    if (useTLS) {
        tlsFlag = WINHTTP_FLAG_SECURE;
    } else {
        tlsFlag = 0;
    }
    HINTERNET hRequest = WinHttpOpenRequest(
        hConnect,
        verb,
        uri,
        NULL,
        WINHTTP_NO_REFERER,
        WINHTTP_DEFAULT_ACCEPT_TYPES,
        tlsFlag
    );

    if (hRequest == NULL) {
        printf("Error %d: could not open request\n", GetLastError());
        return "Error";
    } 

    // LPVOID options = SECURITY_FLAG_IGNORE_UNKNOWN_CA | 
    //     SECURITY_FLAG_IGNORE_CERT_DATE_INVALID | 
    //     SECURITY_FLAG_IGNORE_CERT_CN_INVALID | 
    //     SECURITY_FLAG_IGNORE_CERT_WRONG_USAGE;

    LPCWSTR header = WINHTTP_NO_ADDITIONAL_HEADERS;
    DWORD headerLen = 0;
    LPVOID opData = WINHTTP_NO_REQUEST_DATA;
    DWORD opDataLen = 0;
    std::vector<BYTE> opDataVec;
    if (verb == L"POST") {
        header = L"Content-Type: text/plain\r\n";
        headerLen = -1L;
        std::cout << data << std::endl;
        opDataVec = encryptPayload(data);
        // printBytes(opDataVec.data(), opDataVec.size());
        opData = opDataVec.data();
        opDataLen = opDataVec.size();
    }
    BOOL bResults = WinHttpSendRequest(
        hRequest,
        header,
        headerLen,
        opData,
        opDataLen,
        opDataLen,
        0
    );
    char* cp = (char*)opData;

    if (!bResults) {
        printf("Error %d: could not send request\n", GetLastError());
        return "Error";
    } 

    bResults = WinHttpReceiveResponse(hRequest, NULL);

    if (!bResults) {
        printf("Error %d: could not receive response\n", GetLastError());
        return "Error";
    }

    DWORD dwSize = 0;
    char* buffer = (char*)malloc(4096);
    
    if (buffer == NULL) {
        printf("Error %d: could not allocate memory\n", GetLastError());
        return "Error";
    }

    while (TRUE) {
        dwSize = 0;

        if (!WinHttpQueryDataAvailable( hRequest, &dwSize)) {
            printf( "Error %d: WinHttpQueryDataAvailable.\n", GetLastError());
            return "Error";
        }

        if (dwSize <= 0) break;

        DWORD bytesRead;

        if (!WinHttpReadData(hRequest, buffer, 4096, &bytesRead)) {
            printf("Error %d: could not read data\n", GetLastError());
        }

        if (bytesRead > 0) {
            result.insert(result.end(), buffer, buffer + bytesRead);
        }              
    } 

    std::string resultString = decryptPayload(result);
    return resultString;
}