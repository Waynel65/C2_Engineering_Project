#ifndef HTTP_H
#define HTTP_H

#include <windows.h>
#include <string>
#include <vector>

std::vector<BYTE> encryptPayload(std::string message); 

std::string decryptPayload(std::vector<BYTE> payload);

std::string httpGet(LPCWSTR fqdn, int port, LPCWSTR uri);

std::string httpPost(LPCWSTR fqdn, int port, LPCWSTR uri, std::string data);

std::string httpRequest(LPCWSTR verb, LPCWSTR fqdn, int port, LPCWSTR uri, std::string data);

#endif