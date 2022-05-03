import donut

def make_shellcode(file, method):
    """
        generate shellcode from a dll file using donut in order to perform dll injection
    """

    shellcode = donut.create(
        file=file,
        method=method
    )

    with open("test.bin", "wb") as f:
        f.write(shellcode)
    print(shellcode)
    return shellcode

if __name__ == "__main__":
    make_shellcode("test.dll", "IAmAGoodNoodle")
