import platform

def GetClearCommandInstruction():
    a = platform.system()
    if a == "Linux":
        return "clear"
    elif a == "Windows":
        return "cls"
    else:
        return "clear"