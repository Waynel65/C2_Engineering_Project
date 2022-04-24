#include <windows.h>
#include <string>
#include <iostream>
#include <winhttp.h>
#include "http.h"

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
    std::string result;

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
        header = L"Content-Type: application/json\r\n";
        headerLen = -1L;
        opData = (LPVOID) data.data();
        opDataLen = data.size();
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
            result += std::string(buffer, bytesRead);
        }              
    } 

    return result;
}