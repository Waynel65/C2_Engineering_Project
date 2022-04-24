CC=gcc
cXX=g++

ifeq ($(OS),Windows_NT)
	RM=powershell /c rm
else	
	RM=rm
endif

implant:
	$(CXX) implant.cpp http.cpp -lwinhttp -o bin/implant.exe

clean:
	$(RM) bin/*.exe