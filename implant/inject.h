#ifndef EXEC_SHELL
#define EXEC_SHELL


#define BUF_SIZE 4096

#include <windows.h>
#include <stdio.h>
#include <string>

// function to inject shellcode into process
void inject(char* shellcode);
void inject(char* shellcode, int pid);

#endif