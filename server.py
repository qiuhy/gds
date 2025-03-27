import threading
import socket
import time
import player
from event import *
import logging
import game

logger = logging.getLogger()

GDPORT = 9999


class GDC(player.Player):
    def __init__(self, socket: socket.socket, addr):
        super().__init__()
        self.socket = socket
        self.address = addr
        self.closed = False
        self.name = self.address[0]
        self.socket.settimeout(30)

        logger.info(f"GDC: {self.address} connected")

        if self.sendMessage_recvOK(Messgae(Game_Event_Cate.GE_Name)):
            # self.socket.setblocking(True)
            threading.Thread(target=self.process).start()
        else:
            logger.warning(f"GDC: {self.address} check FAIL!")
            self.close()

    def process(self):
        while not self.closed:
            msg = self.recvMessage_sendOK()
            self.onMessage(msg)

    def onMessage(self, msg: Messgae):
        if msg is None:
            return
        if msg.e == Game_Event_Cate.GE_Name:
            self.name = msg.info
            threading.Thread(target=game.new, args=(self,)).start()
        elif msg.e == Game_Event_Cate.GE_Quit:
            logger.info(f"GDC: {self.address} quit")
            self.close()

    def onEvent(self, e, info):
        super().onEvent(e, info)
        self.sendMessage(Messgae(e, info))

    def play(self, desk_outs):
        # if self.closed:
        return super().play(desk_outs)
        # else:
        #     info = desk_outs[-1] if len(desk_outs) else None
        #     msg = Messgae(Game_Event_Cate.GE_Playing,info)
        #     if self.sendMessage_recvOK(msg):
        #         out = self.recvMessage_sendOK()
        #         if out.e == Game_Event_Cate.GE_Playing:
        #             return out.info

    def give(self):
        return super().give()

    def back(self, c):
        return super().back(c)

    def recvMessage(self):
        if self.closed:
            return
        try:
            data = None
            data = str(self.socket.recv(1024), "utf-8")
            if not data:
                logger.info(f"GDC: {self.address} no data")
                self.close()
                return

            msg = Messgae.fromJson(data)
            if msg:
                logger.debug(f"GDC: {self.address} 收到消息 {msg}")
                return msg
            else:
                logger.warning(f"GDC: {self.address} 无效消息 {data}")
                return
        except socket.timeout:
            pass
        except Exception as e:
            logger.error(f"GDC: {self.address} {str(e)} recv {data}")
            self.close()
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
            logger.debug(f"GDC: {self.address} 发出消息 {msg}")
            return True
        except Exception as e:
            logger.error(f"GDC: {self.address} {str(e)} send {msg}")
            return False

    def sendMessage_recvOK(self, msg):
        if not self.sendMessage(msg):
            return False
        msg = self.recvMessage()
        if not msg:
            return False
        elif msg.e != Game_Event_Cate.GE_OK:
            return False

        return True

    def close(self):
        if not self.closed:
            self.closed = True
            self.socket.close()
            logger.info(f"GDC: {self.address} close")

    def set_cards(self, cards):
        super().set_cards(cards)
        msg = Messgae(Game_Event_Cate.GE_Dealing, cards)
        self.sendMessage(msg)


class GDS:
    def __init__(self):
        self.clients: dict[str, GDC] = {}
        self.server = socket.create_server(("", GDPORT))
        self.address = self.server.getsockname()
        self.onTableUser = []
        threading.Thread(target=self.accept).start()
        threading.Thread(target=self.check, daemon=True).start()
        logger.info(f"GDS: start {self.address}")
        pass

    def accept(self):
        while True:
            try:
                (socket, addr) = self.server.accept()
                ip = addr[0]
                gdc = self.clients.get("ip")
                if gdc:
                    gdc.close()
                gdc = GDC(socket, addr)
                self.clients[ip] = gdc
            except OSError:
                break
            except Exception as e:
                logger.error(f"GDS:accept {str(e)}")
                

    def check(self):
        def is_connected(c: GDC):
            if c.closed:
                return False
            try:
                c.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                return True
            except socket.timeout:
                return False
            except socket.error:
                return False

        for ip, c in self.clients.items():
            if not is_connected(c):
                logger.warning(f"GDS: client {c.address} lost connect")
                c.close()
                self.clients.pop(ip)
        time.sleep(60)

    @property
    def freeUser(self):
        for ip, user in self.clients.items():
            if user in self.onTableUser:
                yield user

    def close(self):
        for c in self.clients.values():
            c.close()
        self.server.close()
        logger.info("GDS: close")


def main():
    gd = GDS()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logger.warning("捕获到Ctrl+C! 正在退出...")
    except SystemExit as e:
        logger.warning(f"检测到退出信号 exit({e.code}) 正在退出...")
    gd.close()


if __name__ == "__main__":
    main()
    pass
