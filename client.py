import socket
import threading
import logging
from event import *
from looker import *

logger = logging.getLogger()

class client(JPX):
    def __init__(self, name=""):
        if name == "":
            name = "网络键盘侠"
        super().__init__(name)
        self.socket = socket.socket()
        self.closed = True

    def connect(self, hostaddr):
        try:
            self.close()
            self.socket.connect(hostaddr)
            self.hostaddr = self.socket.getpeername()
            self.closed = False
            logger.debug(f"connect to {self.hostaddr}")
            threading.Thread(target=self.process).start()
            return True
        except Exception as e:
            logger.error(f"连接失败 {hostaddr},{str(e)}")
            return False

    def close(self):
        if not self.closed:
            self.closed = True
            self.onQuit()
            self.socket.close()
            logger.debug(f"colse from {self.hostaddr}")

    def process(self):
        while not self.closed:
            msg = self.recvMessage()
            logger.debug(f"recv {msg} ")
            rep = self.getReply(msg)
            logger.debug(f"send {rep}")
            # logger.debug(f"{msg} --> {rep}")
            self.sendMessage(rep)

    def play(self, desk_outs):
        return super().play(desk_outs)

    def getReply(self, msg: Messgae):
        if msg is None:
            return
        elif msg.e == Game_Event.GE_Quit:
            logger.warning("server quit")
            self.close()
        elif msg.e == Game_Event.GE_Name: 
            return Messgae(Game_Event.GE_Name, self.name) 
        elif msg.e == Game_Event.GE_Playing:
            return self.play([msg.info])

        self.onEvent(msg.e, msg.info)
        return Messgae.OK()

    def recvMessage(self):
        if self.closed:
            return
        try:
            data = None
            data = str(self.socket.recv(1024), "utf-8")
            if not data:
                logger.warning(f"no data")
                self.close()
                return

            msg = Messgae.fromJson(data)
            if not msg:
                logger.warning(f"无效消息 {data}")
            return msg
        except Exception as e:
            logger.error(f"{str(e)} recv {data}")
            self.close()
        return

    def sendMessage(self, msg: Messgae):
        if self.closed:
            return False
        if msg is None:
            return False
        try:
            msgJson = msg.toJson()
            self.socket.sendall(bytes(msgJson, "utf-8"))
            return True
        except Exception as e:
            logger.error(f"{str(e)} send {msg}")
            return False

    def onKey(self, e):
        if e.event_type == "up" and e.name == "e":
            self.close()
        return super().onKey(e)

def main():
    c = client()
    hostaddr = ("localhost", 9999)
    if c.connect(hostaddr):
        while not c.closed:
            pass
    c.close()


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s : %(message)s")
    logfilename = f"{os.getcwd()}/log/gds-client.log"
    handler = logging.FileHandler(logfilename, encoding="utf-8")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    main()
    pass
