#ifndef INJECT_PROC
#define INJECT_PROC


#include <windows.h>
#include <stdio.h>
#include <string>
#include <tchar.h>
#include <psapi.h>

// function to inject shellcode into process
BOOL inject(std::string exePath, char* shellcode, int size);

#endif