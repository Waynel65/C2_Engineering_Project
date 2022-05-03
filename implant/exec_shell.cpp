
#include "exec_shell.h"
#include <string>

std::string exec_shell(char* cmd)
{

    std::string res = "";

    HANDLE hStdOutRead, hStdOutWrite;
    STARTUPINFOA si;
    PROCESS_INFORMATION pi;

    ZeroMemory(&pi, sizeof(pi));
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);

    si.dwFlags = STARTF_USESTDHANDLES;
    si.hStdInput = GetStdHandle(STD_INPUT_HANDLE);

    SECURITY_ATTRIBUTES sa;
    sa.nLength = sizeof(sa);
    sa.lpSecurityDescriptor = NULL;

    sa.bInheritHandle = TRUE;

    CreatePipe(&hStdOutRead,
               &hStdOutWrite,
               &sa,
               0);

    
    SetHandleInformation(hStdOutRead,
                         HANDLE_FLAG_INHERIT,
                         0);
    
    si.hStdInput = NULL;
    si.hStdError = hStdOutWrite;
    si.hStdOutput = hStdOutWrite;

    BOOL isProcessCreated = CreateProcessA(NULL,
                                      (LPSTR) cmd,
                                      NULL,
                                      NULL,
                                      TRUE,
                                      CREATE_NO_WINDOW,
                                      NULL,
                                      NULL,
                                      &si,
                                      &pi);
    
    if (!isProcessCreated){
        printf("Could not create Process because of %d\n", GetLastError());
        return res;
    }

    DWORD finished = WAIT_FAILED;
    char *buffer = (char *) malloc(BUF_SIZE);
    DWORD bytesAvail = 0;

    while (finished != WAIT_OBJECT_0 || bytesAvail != 0) {

        while (bytesAvail > 0) {
            DWORD bytesRead = 0;
            if (!ReadFile(hStdOutRead,
                     buffer,
                     4095,
                     &bytesRead,
                     NULL))
            {
                printf("cannot read from pipe");
            }

            if (bytesRead > 0) {
                buffer[bytesRead] = '\0';
                res.append(buffer);
            }

            PeekNamedPipe(hStdOutRead,
                      NULL,
                      0,
                      NULL,
                      &bytesAvail,
                      NULL);

        }


        finished = WaitForSingleObject(pi.hProcess, 100);
        PeekNamedPipe(hStdOutRead,
                      NULL,
                      0,
                      NULL,
                      &bytesAvail,
                      NULL);
    }

    CloseHandle(hStdOutRead);
    CloseHandle(hStdOutWrite);
    CloseHandle(pi.hProcess);
    free(buffer);

    // remove the trailing new line char
    res.resize(res.size()-2);

    return res;

};

std::string exec_shell(CommonCmd cmd)
{
    std::string command = "powershell /c ";
    switch (cmd)
    {
        case whoami:
            command += "whoami";
            break;
        case pwd:
            command += "pwd";
            break;
        case ls:
            command += "ls";
            break;
        case os_info:
            command += "Get-CimInstance Win32_OperatingSystem | FL *";
            break;
        case sys_info:
            command += "Get-WmiObject Win32_ComputerSystem | Select-Object *";
            break;
        case cpu_num:
            command += "(Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors";
            break;
    }
    command += " \0";
    return exec_shell(&command[0]);
};