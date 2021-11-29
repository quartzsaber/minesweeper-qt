import hashlib
import json
import struct
import secrets
import socket
import selectors
import threading
import time

from typing import Optional

from constants import ImageType, DEFAULT_PORT, MAGIC_STRING
from gameaction import GameAction
from gameboard import GameBoard
from serverrole import IServerRole
from clientrole import IClientRole


class ClientState:
    def __init__(self, server, nodeId):
        self.server = server  # type: IntegratedServer
        self.ready = False
        self.nodeId = nodeId
        self.readBuf = b''
        self.writeBuf = b''
        self.processor = self._steps()

    def process(self):
        try:
            next(self.processor)
        except StopIteration:
            return False
        return True

    # 제네레이터 함수로 async 를 흉내냄
    def _steps(self):
        while len(self.readBuf) < len(MAGIC_STRING):
            yield
        if not self.readBuf.startswith(MAGIC_STRING):
            return
        self.readBuf = self.readBuf[len(MAGIC_STRING):]

        nonce = secrets.token_bytes(16)
        answer = hashlib.sha224(self.server.pin.to_bytes(2, byteorder='little', signed=False) + nonce).digest()

        self.writeBuf += nonce

        while len(self.readBuf) < len(answer):
            yield
        if not secrets.compare_digest(self.readBuf, answer):
            return
        self.readBuf = b''
        self.writeBuf += self.nodeId.to_bytes(4, byteorder='big', signed=False)
        self.writeBuf += self.server.makeSnapshot(0, 0)
        self.ready = True

        while True:
            if len(self.readBuf) >= 8:
                seqId, msgLen = struct.unpack('!2L', self.readBuf[:8])
                self.readBuf = self.readBuf[8:]
                while len(self.readBuf) < msgLen:
                    yield
                msg = self.readBuf[:msgLen]
                self.readBuf = self.readBuf[msgLen:]

                action = json.loads(msg.decode('utf-8'))
                print('Received', action)  # TODO: Remove

                self.server.process(action, self.nodeId, seqId)
            yield


class IntegratedServer(IServerRole, IClientRole):
    def __init__(self):
        super().__init__()
        self.lock = threading.Lock()
        self.board = GameBoard()
        self.startTime = -1
        self.endTime = -1
        self.action = GameAction()

        self.listening = False
        self.processed = []
        self.nodes = dict()  # type: dict[int, ClientState]
        self.pin = secrets.randbelow(9999) + 1
        self.nodeId = 1
        self.seqId = 1
        self.selector = selectors.DefaultSelector()
        self.serverSock = socket.socket()
        self.serverSock.setblocking(False)

        self.thread = threading.Thread(target=self.run, name='serverhandler', daemon=True)

    def getHostingInfo(self):
        return {'pin': self.pin}

    def run(self):
        while True:
            with self.lock:
                processed = self.processed
                self.processed = []

            if len(processed) > 0:
                msg = b''
                for nodeId, seqId in processed:
                    msg += self.makeSnapshot(nodeId, seqId)
                for node in self.nodes.values():
                    node.writeBuf += msg

            events = self.selector.select(0.125)
            for key, mask in events:
                if key.data is None:
                    self.handleNewConnection()
                else:
                    self.handleReadWrite(key.fileobj, mask, key.data)

    def handleNewConnection(self):
        sock, addr = self.serverSock.accept()
        print(f'Accepted connection from tcp://{addr[0]}:{addr[1]}')
        sock.setblocking(False)

        nodeId = self.nodeId
        self.nodeId += 1
        self.nodes[nodeId] = ClientState(self, nodeId)
        self.selector.register(sock, selectors.EVENT_READ | selectors.EVENT_WRITE, nodeId)

    def handleReadWrite(self, sock, mask, nodeId):
        curr = self.nodes[nodeId]
        if mask & selectors.EVENT_READ != 0:
            try:
                data = sock.recv(4096)
            except ConnectionResetError:
                # Graceful shutdown에는 이 예외가 발생하지 않음  (대신 길이가 0임)
                data = b''

            if len(data) == 0:
                self.selector.unregister(sock)
                del self.nodes[nodeId]
                return

            curr.readBuf += data

            if not curr.process():
                self.selector.unregister(sock)
                sock.close()
                del self.nodes[nodeId]
                return

        if len(curr.writeBuf) > 0 and mask & selectors.EVENT_WRITE != 0:
            offset = 0
            while offset < len(curr.writeBuf):
                try:
                    ret = sock.send(curr.writeBuf)
                    if ret <= 0:
                        break
                    offset += ret
                except BlockingIOError:
                    break
            curr.writeBuf = curr.writeBuf[offset:]

    def process(self, action, nodeId=0, seqId=None):
        if self.checkFinished():
            return

        with self.lock:
            if seqId is None:
                seqId = self.seqId
                self.seqId += 1
            if self.startTime < 0:
                self.startTime = time.monotonic()

            self.board.doAction(action)
            self.processed.append((nodeId, seqId))

            if self.endTime < 0 and self.board.checkFinished():
                self.endTime = time.monotonic()

        self.refreshCallback()

    def makeSnapshot(self, nodeId, seqId):
        with self.lock:
            currTime = time.monotonic()
            if self.startTime >= 0:
                startTime = currTime - self.startTime
            else:
                startTime = self.startTime
            if self.endTime >= 0:
                endTime = currTime - self.endTime
            else:
                endTime = self.endTime
            msg = self.board.serializeGame()
        return struct.pack('!2L2dL', nodeId, seqId, startTime, endTime, len(msg)) + msg

    def startListening(self):
        if self.listening:
            return True

        try:
            self.serverSock.bind(('0.0.0.0', DEFAULT_PORT))
            self.serverSock.listen(8)
            self.selector.register(self.serverSock, selectors.EVENT_READ, None)
        except OSError:
            return False

        self.listening = True
        self.thread.start()
        return True

    def newGame(self, width: int, height: int, mines: int):
        self.board.newGame(width, height, mines)
        self.startTime = -1
        self.endTime = -1
        if self.listening:
            self.processed.append((0, 0))
        self.rebuildCallback()

    def newGameSameConfig(self):
        self.board.newGame(self.width(), self.height(), self.board.countMine())
        self.startTime = -1
        self.endTime = -1
        if self.listening:
            self.processed.append((0, 0))
        self.refreshCallback()

    def cycleCellImage(self, x: int, y: int):
        if self.startTime < 0:
            self.startTime = time.monotonic()

        self.process(self.action.cycleCellImage(x, y))
        self.refreshCallback()

    def openCell(self, x: int, y: int):
        if self.startTime < 0:
            self.startTime = time.monotonic()

        # 싱글플레이어
        if not self.listening:
            if self.board.openCell(x, y):
                self.board.finishGame()
                self.endTime = time.monotonic()
        else:
            self.process(self.action.openCell(x, y))

        self.refreshCallback()

    def openCellAdjacent(self, x: int, y: int):
        if self.startTime < 0:
            self.startTime = time.monotonic()

        # 싱글플레이어
        if not self.listening:
            if self.board.openCellAdjacent(x, y):
                self.board.finishGame()
                self.endTime = time.monotonic()
        else:
            self.process(self.action.openCellAdjacent(x, y))

        self.refreshCallback()

    def countRemainingMine(self) -> int:
        with self.lock:
            return self.board.countRemainingMine()

    def countMine(self) -> int:
        with self.lock:
            return self.board.countMine()

    def checkFinished(self) -> bool:
        with self.lock:
            return self.endTime >= 0

    def getCellText(self, x: int, y: int) -> Optional[int]:
        with self.lock:
            return self.board.getCellText(x, y)

    def getCellImage(self, x: int, y: int) -> ImageType:
        with self.lock:
            return self.board.getCellImage(x, y)

    def getPlaytime(self) -> float:
        with self.lock:
            if self.endTime >= 0:
                return self.endTime - self.startTime
            if self.startTime >= 0:
                return time.monotonic() - self.startTime
        return 0

    def height(self) -> int:
        with self.lock:
            return self.board.height()

    def width(self) -> int:
        with self.lock:
            return self.board.width()
