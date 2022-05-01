#include <windows.h>
#include <string>
#include <vector>
#include <iostream>
#include <winhttp.h>
#include "http.h"
#include "aes_gcm.h"

BYTE textIV[] = {0x87, 0xb8, 0xa9, 0xa6, 0xc2, 0x39, 0x42, 0x5f, 0xc2, 0xda, 0x8c, 0xc1};
BYTE key[] = {0x41, 0x13, 0xcd, 0xa3, 0xa0, 0xe0, 0xab, 0x5e, 0x19, 0xf1, 0xc0, 0x1c, 0x6d, 0x4e, 0x77, 0xc5, 0xe5, 0x20, 0xd2, 0x44, 0xe, 0x52, 0xae, 0x87, 0xaa, 0xa, 0x96, 0x67, 0x28, 0x82, 0xea, 0x8};

// encrypt the payload to a byte array
std::vector<BYTE> encryptPayload(std::string message) {
    BYTE* ptMessage = (BYTE*)message.data();
    DWORD messageSize = message.size();

    auto box = new AESGCM(key);

    box->Encrypt( (BYTE*) textIV, sizeof(textIV), ptMessage, messageSize);

    BYTE* ciphertext = (BYTE*) malloc(box->ciphertextSize);
    std::copy(box->ciphertext, box->ciphertext + box->ciphertextSize, ciphertext);
    std::vector ciphertextVec(ciphertext, ciphertext + box->ciphertextSize);

    delete box;

    return ciphertextVec;
}

std::string decryptPayload(std::vector<BYTE> payload) {
    auto box = new AESGCM(key);
    DWORD ciphertextSize = payload.size() - 28;

    BYTE* textIV = (BYTE*) malloc(12);
    BYTE* tag = (BYTE*) malloc(16);
    BYTE* ciphertext = (BYTE*) malloc(ciphertextSize);

    std::copy(payload.begin(), payload.begin() + 12, textIV);
    std::copy(payload.begin() + 13, payload.begin() + 29, tag);
    std::copy(payload.begin() + 30, payload.end(), ciphertextSize);

    box->Decrypt(textIV, sizeof(textIV), ciphertext, ciphertextSize, tag, 16);

    std::string message(box->plaintext, box->plaintext + box->ptBufferSize);

    return message;
}

std::string httpGet(LPCWSTR fqdn, int port, LPCWSTR uri){
    return httpRequest(L"GET", fqdn, port, uri, "");
}

std::string httpPost(LPCWSTR fqdn, int port, LPCWSTR uri, std::string data) {
    return httpRequest(L"POST", fqdn, port, uri, data);
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
std::string httpRequest(LPCWSTR verb, LPCWSTR fqdn, int port, LPCWSTR uri, std::string data){
    std::vector<BYTE> result;

    HINTERNET hSession = WinHttpOpen(
        L"sample",
        WINHTTP_ACCESS_TYPE_NO_PROXY,
        WINHTTP_NO_PROXY_NAME,
        WINHTTP_NO_PROXY_BYPASS,
        0);

    if (hSession == NULL) {
        printf("Error: could not create http session\n");
        return NULL;
    }

    HINTERNET hConnect = WinHttpConnect(
        hSession,
        fqdn,
        port,
        0
    );

    if (hConnect == NULL) {
        printf("Error: could not connect to server\n");
        return NULL;
    }

    DWORD useTLS = 0;
    // DWORD useTLS = WINHTTP_FLAG_SECURE;
    HINTERNET hRequest = WinHttpOpenRequest(
        hConnect,
        verb,
        uri,
        NULL,
        WINHTTP_NO_REFERER,
        WINHTTP_DEFAULT_ACCEPT_TYPES,
        useTLS
    );

    if (hRequest == NULL) {
        printf("Error: could not open request\n");
        return NULL;
    }

    // LPVOID options = SECURITY_FLAG_IGNORE_UNKNOWN_CA | 
    //     SECURITY_FLAG_IGNORE_CERT_DATE_INVALID | 
    //     SECURITY_FLAG_IGNORE_CERT_CN_INVALID | 
    //     SECURITY_FLAG_IGNORE_CERT_WRONG_USAGE;

    LPCWSTR header = WINHTTP_NO_ADDITIONAL_HEADERS;
    DWORD headerLen = 0;
    LPVOID opData = WINHTTP_NO_REQUEST_DATA;
    DWORD opDataLen = 0;
    if (verb == L"POST") {
        header = L"Content-Type: text/plain\r\n";
        headerLen = -1L;
        std::vector<BYTE> opDataVec = encryptPayload(data);
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
        printf("Error: could not send request\n");
        return NULL;
    }

    bResults = WinHttpReceiveResponse(hRequest, NULL);

    if (!bResults) {
        printf("Error: could not receive response\n");
        return NULL;
    }

    DWORD dwSize = 0;
    char* buffer = (char*)malloc(4096);
    
    if (buffer == NULL) {
        printf("Error: could not allocate memory\n");
        return NULL;
    }

    while (TRUE) {
        dwSize = 0;

        if (!WinHttpQueryDataAvailable( hRequest, &dwSize)) {
            printf( "Error: WinHttpQueryDataAvailable.\n");
            return NULL;
        }

        if (dwSize <= 0) break;

        DWORD bytesRead;

        if (!WinHttpReadData(hRequest, buffer, 4096, &bytesRead)) {
            printf("Error: could not read data because %d\n", GetLastError());
        }

        if (bytesRead > 0) {
            result.insert(result.end(), buffer, buffer + bytesRead);
        }              
    } 

    std::string resultString = decryptPayload(result);
    return resultString;
}