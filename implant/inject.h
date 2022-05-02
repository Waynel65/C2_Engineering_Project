#ifndef INJECT_PROC
#define INJECT_PROC


#include <windows.h>
#include <stdio.h>
#include <string>
#include <tchar.h>
#include <psapi.h>

// function to inject shellcode into process
void inject(char* shellcode);
void inject(char* shellcode, int pid);

// function to get remote process ID for injection
int getProcID();

#endif