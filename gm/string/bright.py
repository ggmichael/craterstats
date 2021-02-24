
import colorama

def bright(txt):
    if "init" not in bright.__dict__:
        colorama.init()
        bright.init = True
    return colorama.Style.BRIGHT+txt+colorama.Style.RESET_ALL

if __name__ == '__main__':
    print(bright("bright") + " normal")
    print(bright.init)
    print(bright("bright") + " normal")