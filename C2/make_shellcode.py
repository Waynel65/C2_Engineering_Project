import donut
import sys

def main():
    filepath = sys.argv[1]
    
    shellcode = donut.create(
        file = filepath,
        method = "exec"
    )

if __name__ == "__main__":
    main()