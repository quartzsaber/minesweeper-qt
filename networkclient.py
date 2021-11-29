import hashlib
import json
import struct
import socket
import threading
import time

from typing import Optional

from clientrole import IClientRole
from constants import ImageType, DEFAULT_PORT, MAGIC_STRING
from gameaction import GameAction
from gameboard import GameBoard


class NetworkClient(IClientRole):
    def __init__(self, addr: str, pin: int):
        super().__init__()

        self.disconnectedCallback = None

        # 아직 서버가 확인해주지 않은 액션들
        # 사용자에게서 레이턴시를 감추는데 사용됨
        self.pendingActions = dict()

        self.action = GameAction()
        self.lock = threading.Lock()
        self.socket = None  # type: Optional[socket.socket]
        self.nodeId = -1
        self.seqId = 1
        self.board = GameBoard()
        self.startTime = -1
        self.endTime = -1

        self.thread = threading.Thread(target=self.run, args=(addr, pin), daemon=True)
        self.thread.start()

    def setDisconnectedCallback(self, fn):
        self.disconnectedCallback = fn

    def run(self, addr, pin):
        try:
            port = pin // 10000
            pin %= 10000
            if port == 0:
                port = DEFAULT_PORT

            sock = socket.socket()
            sock.connect((addr, port))
            sock.sendall(MAGIC_STRING)

            nonce = b''
            while len(nonce) < 16:
                buf = sock.recv(4096)
                if len(buf) == 0:
                    self.disconnectedCallback('알 수 없는 연결 오류가 발생했습니다')
                    return
                nonce += buf

            auth = hashlib.sha224(pin.to_bytes(2, byteorder='little', signed=False) + nonce).digest()
            sock.sendall(auth)

            recvBuf = b''
            while len(recvBuf) < 4:
                buf = sock.recv(4096)
                if len(buf) == 0:
                    self.disconnectedCallback('핀 번호가 올바르지 않습니다')
                    return
                recvBuf += buf

            self.nodeId = struct.unpack('!L', recvBuf[:4])[0]
            recvBuf = recvBuf[4:]

            self.socket = sock

            while True:
                while len(recvBuf) < 28:
                    buf = sock.recv(4096)
                    if len(buf) == 0:
                        self.disconnectedCallback('알 수 없는 연결 오류가 발생했습니다')
                        return
                    recvBuf += buf

                # 시계가 완벽히 동기화되지는 않겠지만, 적어도 게임이 끝난 후에 뜨는 '걸린 시간'은 정확함
                currTime = time.monotonic()
                nodeId, seqId, startTime, endTime, msgLen = struct.unpack('!2L2dL', recvBuf[:28])
                if startTime >= 0:
                    startTime = currTime - startTime
                if endTime >= 0:
                    endTime = currTime - endTime

                if len(recvBuf) - 28 < msgLen:
                    buf = sock.recv(4096)
                    if len(buf) == 0:
                        self.disconnectedCallback('알 수 없는 연결 오류가 발생했습니다')
                        return
                    recvBuf += buf

                self.updateBoard(nodeId, seqId, startTime, endTime, recvBuf[28:28+msgLen])
                recvBuf = recvBuf[28+msgLen:]
        except ConnectionError as e:
            self.disconnectedCallback(e.strerror)

    def updateBoard(self, nodeId, seqId, startTime, endTime, data):
        with self.lock:
            self.startTime = startTime
            self.endTime = endTime
            if seqId == 0:
                self.pendingActions = dict()
            elif nodeId == self.nodeId:
                if seqId in self.pendingActions:
                    del self.pendingActions[seqId]

            w = self.board.width()
            h = self.board.height()
            self.board.deserializeGame(data)

            for action in self.pendingActions.values():
                self.board.doAction(action)

        if w != self.board.width() or h != self.board.height():
            self.rebuildCallback()
        else:
            self.refreshCallback()

    def performAction(self, action: dict):
        with self.lock:
            seqId = self.seqId
            self.seqId += 1
            self.pendingActions[seqId] = action

        msg = json.dumps(action).encode('utf-8')
        self.socket.sendall(struct.pack('!2L', seqId, len(msg)) + msg)

        self.board.doAction(action)
        self.refreshCallback()

    def cycleCellImage(self, x: int, y: int):
        self.performAction(self.action.cycleCellImage(x, y))

    def openCell(self, x: int, y: int):
        self.performAction(self.action.openCell(x, y))

    def openCellAdjacent(self, x: int, y: int):
        self.performAction(self.action.openCellAdjacent(x, y))

    def countRemainingMine(self) -> int:
        with self.lock:
            return self.board.countRemainingMine()

    def countMine(self) -> int:
        with self.lock:
            return self.board.countMine()

    def checkFinished(self) -> bool:
        with self.lock:
            return self.board.checkFinished()

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
