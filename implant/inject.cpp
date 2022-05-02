#include "inject.h"
#include <iostream>

void inject(char* shellcode)
{
    HANDLE processHandle;
    HANDLE remoteThread;
    PVOID remoteBuffer;

    printf("Injecting to PID: %i", 1);
};

int getProcID()
{
    // Get a list of process indentifiers

    DWORD aProcesses[1024], cbNeeded, cProcesses;
    unsigned int i;

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
    return cProcesses;
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