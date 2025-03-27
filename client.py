import looker
import socket
import threading
from event import *
import logging

logger = logging.getLogger()


class client(looker.Looker):
    def __init__(self, name=""):
        if name == "":
            name = "网络观察员"
        super().__init__(name)
        self.socket = socket.socket()
        self.socket.settimeout(30)
        self.closed = True

    def connect(self, hostaddr):
        try:
            self.close()
            self.socket.connect(hostaddr)
            self.hostaddr = self.socket.getpeername()
            self.closed = False
            threading.Thread(target=self.process).start()
            return True
        except Exception as e:
            logger.error(f"连接失败 {hostaddr},{str(e)}")
            return False

    def close(self):
        if not self.closed:
            self.sendMessage(Messgae(Game_Event_Cate.GE_Quit, None))
            self.closed = True
            self.socket.close()

    def process(self):
        while not self.closed:
            msg = self.recvMessage_sendOK()
            self.onMessage(msg)

    def onMessage(self, msg: Messgae):
        if msg is None:
            return
        if msg.e == Game_Event_Cate.GE_OK:
            logger.info(f"获得消息:{msg}")
        elif msg.e == Game_Event_Cate.GE_Name:
            self.sendMessage(Messgae(Game_Event_Cate.GE_Name, self.name))
        else:
            self.onEvent(msg.e, msg.info)

    def recvMessage(self):
        if self.closed:
            return
        try:
            data = None
            data = str(self.socket.recv(1024), "utf-8")
            if not data:
                logger.info(f"{self.hostaddr}: no data")
                self.close()
                return

            msg = Messgae.fromJson(data)
            if msg:
                logger.debug(f"{self.hostaddr}: 收到消息 {msg}")
                return msg
            else:
                logger.warning(f"{self.hostaddr}: 无效消息 {data}")
                return
        except socket.timeout:
            pass
        except Exception as e:
            logger.error(f"{self.hostaddr}: {str(e)} recv {data}")
        return

    def recvMessage_sendOK(self):
        msg = self.recvMessage()
        if msg:
            if not (msg.e == Game_Event_Cate.GE_OK and msg.info is None):
                self.sendMessage(Messgae.OK())
            return msg

    def sendMessage(self, msg: Messgae):
        if self.closed:
            return False
        try:
            msgJson = msg.toJson()
            self.socket.sendall(bytes(msgJson, "utf-8"))
            logger.debug(f"{self.hostaddr}: 发出消息 {msg}")
            return True
        except Exception as e:
            logger.error(f"{self.hostaddr}: {str(e)} send {msg}")
            return False

    def sendMessage_recvOK(self, msg: Messgae):
        if not self.sendMessage(msg):
            return False
        if msg.e == Game_Event_Cate.GE_OK and msg.info is None:
            return True
        msg = self.recvMessage()
        if not msg:
            return False
        elif msg.e != Game_Event_Cate.GE_OK:
            return False

        return True


def main():
    c = client()
    hostaddr = ("localhost", 9999)
    if c.connect(hostaddr):
        while not c.closed:
            pass
    c.close()


if __name__ == "__main__":
    main()
    pass
