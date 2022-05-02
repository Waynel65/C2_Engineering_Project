CC=gcc
cXX=g++

ifeq ($(OS),Windows_NT)
	RM=powershell /c rm
else	
	RM=rm
endif

implant:
	$(CXX) implant.cpp http.cpp exec_shell.cpp -lwinhttp -o bin/implant.exe

test:
	$(CXX) -g test.cpp http.cpp exec_shell.cpp aesgcm.cpp -lwinhttp -lcrypt32 -lbcrypt -o bin/test.exe

clean:
	$(RM) bin/*.exe