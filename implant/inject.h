#ifndef INJECT_PROC
#define INJECT_PROC


#include <windows.h>
#include <stdio.h>
#include <string>
#include <tchar.h>
#include <psapi.h>

// function to inject shellcode into process
void inject(char* shellcode);
void inject(std::string exePath, unsigned char* shellcode);

// function to get remote process ID for injection
int getProcID();

void spawnProcess(std::string exePath);

#endif