import sys
import 

def main():
    filepath = sys.argv[1]
    
    print("before donut")
    shellcode = donut.create(
        file = filepath,
        method = "_Z14IAmAGoodNoodlev",
    )

    print(shellcode)

if __name__ == "__main__":
    print("before main")
    main()