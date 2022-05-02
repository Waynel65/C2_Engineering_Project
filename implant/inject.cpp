#include "inject.h"
#include <iostream>
#include <windows.h>

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