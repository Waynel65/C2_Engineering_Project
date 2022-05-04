CC=gcc
cXX=g++

ifeq ($(OS),Windows_NT)
	RM=powershell /c rm
else	
	RM=rm
endif

implant:
	$(CXX) -std=c++11 -static implant.cpp http.cpp exec_shell.cpp aesgcm.cpp inject.cpp -lwinhttp  -lcrypt32 -lbcrypt -o bin/implant.exe

test:
	$(CXX) -std=c++11 -g test.cpp http.cpp exec_shell.cpp aesgcm.cpp inject.cpp -lwinhttp -lcrypt32 -lbcrypt -liphlpapi -o bin/test.exe

clean:
	$(RM) bin/*.exe