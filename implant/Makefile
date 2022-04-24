CC=gcc
cXX=g++

ifeq ($(OS),Windows_NT)
	RM=powershell /c rm
else	
	RM=rm
endif

implant:
	if [ -d "bin"]; then \
		$(CXX) implant.cpp http.cpp exec_shell.cpp -lwinhttp -o bin/implant.exe; \
	else \
		mkdir bin; \
		$(CXX) implant.cpp http.cpp exec_shell.cpp -lwinhttp -o bin/implant.exe; \
	fi

clean:
	$(RM) bin/*.exe