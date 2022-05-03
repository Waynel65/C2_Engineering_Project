import sys
import donut

def main():
    
    print("before donut")
    shellcode = donut.create(
        file = "test.dll",
        method = "IAmAGoodNoodle",
    )

    print(shellcode)

if __name__ == "__main__":
    print("before main")
    main()