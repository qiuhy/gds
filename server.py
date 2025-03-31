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

        if self.getReply(Messgae(Game_Event.GE_Name)):
            logger.info(f"GDC: {self.address} Name {self.name}")
        else:
            logger.warning(f"GDC: {self.address} check FAIL!")
            self.close()

    def onMessage(self, msg: Messgae):
        if not msg is None:
            if msg.e == Game_Event.GE_Name:
                self.name = msg.info
            elif msg.e == Game_Event.GE_Quit:
                logger.info(f"GDC: {self.address} quit")
                self.close()

    def onEvent(self, e, info):
        super().onEvent(e, info)
        msg = self.getReply(Messgae(e, info))

    def play(self, desk_outs):
        if len(desk_outs):
            lastout = (desk_outs[-1].player, desk_outs[-1].cardValues)
        else:
            lastout = None
        msg = self.getReply(Messgae(Game_Event.GE_Playing, lastout))
        if msg:
            return msg.info
        else:
            return []
        # return super().play(desk_outs)

    def give(self):
        msg = self.getReply(Messgae(Game_Event.GE_Giveing, None))
        givecard=msg.info
        self.removeCards([givecard])
        return givecard
        # return super().give()

    def back(self, c):
        msg = self.getReply(Messgae(Game_Event.GE_Backing, c))
        backcard = msg.info
        self.get_card(c)
        self.removeCards([backcard])
        return backcard
        

    def recvMessage(self):
        if self.closed:
            return
        retry = 0
        while retry < 3:
            try:
                data = None
                data = str(self.socket.recv(1024), "utf-8")
                if not data:
                    logger.info(f"GDC: {self.address} no data")
                    self.close()
                    return

                msg = Messgae.fromJson(data)
                if not msg:
                    logger.warning(f"GDC: {self.address} 无效消息 {data}")
                return msg
            except socket.timeout:
                retry += 1
                logger.warning(f"GDC: {self.address} time out retry {retry}")
            except Exception as e:
                logger.error(f"GDC: {self.address} {str(e)} recv {data}")
                self.close()
                return
        return

    def sendMessage(self, msg: Messgae):
        if self.closed:
            return False
        try:
            msgJson = msg.toJson()
            self.socket.sendall(bytes(msgJson, "utf-8"))
            return True
        except Exception as e:
            logger.error(f"GDC: {self.address} {str(e)} send {msg}")
            return False

    def getReply(self, msg: Messgae):
        if self.sendMessage(msg):
            rep = self.recvMessage()
            if rep:
                logger.debug(f"GDC: {self.address} 发送消息 {msg} 回复 {rep}")
                self.onMessage(rep)
                return rep
            else:
                logger.info(f"GDC: {self.address} 发送消息 {msg} 回复 {rep}")

    def close(self):
        if not self.closed:
            self.closed = True
            self.socket.close()
            logger.info(f"GDC: {self.address} close")

    def set_cards(self, cards):
        super().set_cards(cards)
        self.getReply(Messgae(Game_Event.GE_Dealing, cards))


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
                threading.Thread(target=game.new, args=(gdc,), daemon=True).start()
            except OSError as e:
                logger.error(f"GDS:accept {str(e)}")
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
