import donut

def make_shellcode(file, method):
    """
        generate shellcode from a dll file using donut in order to perform dll injection
    """

    shellcode = donut.create(
        file=file,
        method=method
    )

    return shellcode
