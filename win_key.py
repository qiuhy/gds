import msvcrt
import threading

KEY_NAME = {
    "ctrl+a": b"\x01",
    "ctrl+b": b"\x02",
    "ctrl+c": b"\x03",
    "ctrl+d": b"\x04",
    "ctrl+e": b"\x05",
    "ctrl+f": b"\x06",
    "ctrl+g": b"\x07",
    # "ctrl+h": b"\x08", as back
    # "ctrl+i": b"\x09", as tab
    # "ctrl+j": b"\x0a", as "ctrl+enter"
    "ctrl+k": b"\x0b",
    "ctrl+l": b"\x0c",
    # "ctrl+m": b"\x0d", as enter
    "ctrl+n": b"\x0e",
    "ctrl+o": b"\x0f",
    "ctrl+p": b"\x10",
    "ctrl+q": b"\x11",
    "ctrl+r": b"\x12",
    "ctrl+s": b"\x13",
    "ctrl+t": b"\x14",
    "ctrl+u": b"\x15",
    "ctrl+v": b"\x16",
    # "ctrl+w": b"\x17", as ctrl+back
    "ctrl+x": b"\x18",
    "ctrl+y": b"\x19",
    "ctrl+z": b"\x1a",
    # "ctrl+2": b'\x00\x03'
    "ctrl+back": b"\x7f",
    "ctrl+up": b"\xe0\x8d",
    "ctrl+down": b"\xe0\x91",
    "ctrl+left": b"\xe0s",
    "ctrl+right": b"\xe0t",
    "ctrl+ins": b"\xe0\x92",
    "ctrl+del": b"\xe0\x93",
    "ctrl+home": b"\xe0w",
    "ctrl+end": b"\xe0u",
    # "ctrl+pgup": b"\xe0\x86", as f12
    "ctrl+pgdn": b"\xe0v",
    "ctrl+enter": b"\n",
    "enter": b"\r",
    "space": b" ",
    "esc": b"\x1b",
    "tab": b"\t",
    "back": b"\x08",
    "up": b"\x00H",
    "down": b"\x00P",
    "left": b"\x00K",
    "right": b"\x00M",
    "ins": b"\00R",
    "del": b"\00S",
    "home": b"\00G",
    "end": b"\00O",
    "pgup": b"\00I",
    "pgdn": b"\00Q",
    "f12": b"\xe0\x86",
    "f11": b"\xe0\x85",
    "f10": b"\x00D",
    "f9": b"\x00C",
    "f8": b"\x00B",
    "f7": b"\x00A",
    "f6": b"\x00@",
    "f5": b"\x00?",
    "f4": b"\x00>",
    "f3": b"\x00:",
    "f2": b"\x00<",
    "f1": b"\x00;",
}


def getch(block=False):
    if msvcrt.kbhit() or block:
        ch = msvcrt.getch()
        if ch == b"\xe0" or ch == b"\x00":
            ch += msvcrt.getch()
        return ch
    else:
        return None


def ch2key(ch):
    if ch is None:
        return None
    for key, val in KEY_NAME.items():
        if len(val) != len(ch):
            continue
        elif len(ch) == 2:
            if val[0] == 0xE0 or val[0] == 0:
                if ch[0] == 0xE0 or ch[0] == 0:
                    if ch[1] == val[1]:
                        return key
        
        if ch == val:
            return key
    else:
        return str(ch, "gbk")


def getKey(block=False):
    ch = getch(block)
    return ch2key(ch)


class Listener:
    _instance_lock = threading.Lock()

    def __new__(cls):
        if not hasattr(Listener, "_instance"):
            with Listener._instance_lock:
                if not hasattr(Listener, "_instance"):
                    Listener._instance = super().__new__(cls)
        return Listener._instance

    def __init__(self):
        self.hotkey = {}
        self.listen = []
        self.waitting = {}
        self.listen_thread = threading.Thread(target=self._listen, daemon=True)
        self.listen_thread.start()
        self.stop_event = threading.Event()
        pass

    def _listen(self):
        while True:
            key = getKey(True)
            if key in self.waitting.keys():
                fun = self.waitting.pop(key)
                fun()

            if None in self.waitting.keys():
                fun = self.waitting.pop(None)
                fun()

            if key in self.hotkey.keys():
                fun = self.hotkey[key]
                fun(key)

            for fun in self.listen:
                if not fun(key):
                    break


_listener = Listener()


def add_hotkey(key, callback):
    with _listener._instance_lock:
        _listener.hotkey[key] = callback


def add_listen(callback):
    with _listener._instance_lock:
        _listener.listen.append(callback)


def clear():
    with _listener._instance_lock:
        _listener.listen.clear()
        _listener.hotkey.clear()


def wait(key=None):
    if not isinstance(key, str):
        if key:
            return

    wait_event = threading.Event()

    def _wait():
        wait_event.set()

    with _listener._instance_lock:
        _listener.waitting[key] = _wait
    wait_event.wait()


def main():
    quit = threading.Event()

    def onhotkey(key):
        print(f"hotkey {key} pressed")

    def onkey(key):
        print(f"listened key: {key}")

    def onquit(key):
        print("esc pressed quit ...")
        quit.set()

    add_hotkey("f12", onhotkey)
    add_hotkey("esc", onquit)
    add_listen(onkey)

    print("press esc to QUIT")
    quit.wait()

    print("wait for any key")
    wait()

    clear()


if __name__ == "__main__":
    main()
