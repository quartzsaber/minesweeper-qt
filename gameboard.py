import time
import random
import pickle

from collections import deque

IMAGE_NONE = 0  # 특별한 표시가 없음. 닫혔으면 닫힌 모습이, 열렸으면 숫자 혹은 빈칸이 나타남
IMAGE_FLAG = 1  # 지뢰임을 나타내는 깃발
IMAGE_QUESTION = 2  # 물음표 표시. cycle_cell_flag는 여기까지 3개의 이미지만 사용함
IMAGE_BLOWN_UP_MINE = 3  # 폭발해버린 지뢰. 빨간 배경의 지뢰 모습
IMAGE_MISSED_MINE = 4  # 싱글플레이 게임이 끝날때 나타나는, 미처 지뢰라고 표기하지 못했던 지뢰. 회색 배경의 지뢰 모습
IMAGE_WRONG_FLAG = 5  # 싱글플레이 게임이 끝날때 나타나는, 지뢰가 아닌데 지뢰라고 표기한 곳. 빨간 배경의 깃발 모습


# 지뢰찾기 게임판
class GameBoard:
    def __init__(self):
        # 이 변수들은 여기서는 선언만 하고 new_game() 에서 초기화 함
        # 모든 2차원 리스트는 arr[y][x] 처럼 접근함
        self.mines = [[]]  # 2차원 리스트, 지뢰인 칸은 True, 아니면 False
        self.opened = [[]]  # 2차원 리스트, 열린 칸은 True, 아니면 False
        self.images = [[]]  # 2차원 리스트, IMAGE_* 으로 각 칸을 표시함
        self.startTime = 0  # 시작했을때의 시간. 파이썬에 내장된 time.time() 함수 참고

    # w x h 크기의 게임판을 만들고, mines개수의 지뢰를 랜덤하게 배치
    def newGame(self, w: int, h: int, mines: int):
        self.mines = []
        self.opened = []
        self.images = []

        for i in range(h):
            self.mines.append([])
            self.opened.append([])
            self.images.append([])
            for j in range(w):
                self.mines[i].append(False)
                self.opened[i].append(False)
                self.images[i].append(IMAGE_NONE)

        coords = [(x, y) for x in range(w) for y in range(h)]
        for x, y in random.sample(coords, k=mines):
            self.mines[y][x] = True

        self.startTime = time.time()

    # pickle을 이용해 이 게임판을 문자열로 저장해 리턴
    def serializeGame(self):
        return pickle.dumps(self)

    # pickle을 이용해 이 게임판을 불러옴
    def deserializeGame(self, data):
        game = pickle.loads(data)
        self.mines = game.mines
        self.opened = game.opened
        self.images = game.images
        self.startTime = game.startTime

    # gameaction에서 생성한 action을 적용시킴
    def doAction(self, action):
        pass

    # 해당 칸의 플래그 정보를 바꿈
    def cycleCellImage(self, x: int, y: int):
        self.images[y][x] = (self.images[y][x] + 1) % 3

    # 해당 칸을 엶 (좌클릭 함)
    # 해당 칸은 열리고, 만약 빈 칸일 경우 그 주변 빈 칸도 같이 열림 (self.opened가 수정됨)
    # 열린 칸에 지뢰가 있었을 경우 True를 리턴하고 해당 칸의 이미지는 IMAGE_BLOWN_UP_MINE으로 바뀜
    # 단, 지뢰로 표시해놓은 칸은 무시
    def openCell(self, x: int, y: int):
        if not self.opened[y][x] and (self.images[y][x] == IMAGE_NONE or self.images[y][x] == IMAGE_QUESTION):
            for cx, cy in self.iterEmptyAdjacent(x, y):
                self.opened[cy][cx] = True
            if self.mines[y][x]:
                self.images[y][x] = IMAGE_BLOWN_UP_MINE
                return True
        return False

    # 주변 3x3 칸을 엶
    # 지뢰로 표시해놓은 칸은 무시
    # 열린 칸중에 하나라도 지뢰라면 True를 리턴
    # 단, 지뢰로 표시해놓은 칸은 무시
    def openCellAdjacent(self, x: int, y: int):
        count = 0
        for i in range(x - 1, x + 2):
            if 0 <= i < len(self.mines):
                for j in range(y - 1, y + 2):
                    if 0 <= j < len(self.mines):
                        b = self.openCell(i, j)
                        if b:
                            count += 1
        if count:
            return True
        return False

    # 싱글플레이 모드에서 게임을 끝낼때 부르는 함수
    # 모든 지뢰의 위치를 공개함
    # IMAGE_* 에 붙어있는 설명을 읽기 바람
    def finishGame(self):
        for row in range(len(self.images)):
            for col in range(len(self.images[row])):
                if self.mines[row][col] and self.images[row][col] not in {IMAGE_BLOWN_UP_MINE, IMAGE_FLAG}:
                    self.images[row][col] = IMAGE_MISSED_MINE
                elif not self.mines[row][col] and self.images[row][col] == IMAGE_FLAG:
                    self.images[row][col] = IMAGE_WRONG_FLAG
        # for i, ii in self.images, self.mines:
        #     for j, jj in i, ii:
        #         if j == 0 and jj:

    # 남아있는 지뢰 개수를 셈 (잘못 표기한것도 포함)
    def countRemainingMine(self):
        mineCount = 0
        flagCount = 0
        for i in self.mines:
            mineCount += i.count(True)
        for i in self.images:
            flagCount += i.count(True)
        return mineCount - flagCount

    # 제대로 표기한 지뢰 개수를 셈
    def countFlaggedMine(self):
        count = 0
        for i in range(0, len(self.images)):
            for j in range(0, len(self.images[i])):
                if self.images[i][j] == IMAGE_FLAG and self.mines[i][j]:
                    count += 1
        return count

    # 게임에서 승리했는지 확인 (게임이 끝났으면 True)
    # 지뢰인 칸을 제외하고 모든 칸을 열었을 때가 승리 조건임
    def checkFinished(self):
        for i in range(0, len(self.opened)):
            for j in range(0, len(self.opened[i])):
                if not self.mines[i][j] and not self.opened[i][j]:
                    return False
        return True

    # 해당 칸에 써있는 숫자를 가져옴
    # 아직 열리지 않은 칸일 경우 None
    # 열렸지만 주변에 지뢰가 없을 경우 0
    def getCellText(self, x: int, y: int):
        if not self.opened[y][x]:
            return None
        else:
            return self.countAdjacentMines(x, y)

    # 해당 칸의 이미지 정보를 가져옴
    # (cycle_cell_image 함수와 IMAGE_* 변수 참고)
    def getCellImage(self, x: int, y: int):
        return self.images[y][x]

    # 게임을 시작하고 몇 초가 지났는지 리턴
    def getPlaytime(self):
        return time.time() - self.startTime

    # 게임판의 높이를 리턴함
    def height(self):
        return len(self.mines)

    # 게임판의 너비를 리턴함
    def width(self):
        return len(self.mines[0])

    # ===========================================
    # 여기부터 아래에 있는 함수들은 이 클래스 내부에서 사용하기 위해 만들어진 함수임
    # ===========================================

    # 해당 칸 주변(총 9칸)의 지뢰 개수를 세서 int형으로 리턴
    def countAdjacentMines(self, x: int, y: int):
        count = 0
        for i in range(y - 1, y + 2):
            if 0 <= i < len(self.mines):
                for j in range(x - 1, x + 2):
                    if 0 <= j < len(self.mines[i]):
                        if self.mines[i][j]:
                            count += 1
        return count

    # 주변에 지뢰가 없는 모든 인접한 칸을 찾는 함수
    # 조금 더 엄밀히는, 주변에 지뢰가 없는 모든 칸의 인접한 칸을 찾는 함수
    # for x, y in self.iter_empty_adjacent(...) 처럼 사용
    def iterEmptyAdjacent(self, x: int, y: int):
        visited = set()
        bfs = deque([(x, y)])

        while len(bfs) > 0:
            cx, cy = bfs.popleft()
            if cy < 0 or len(self.mines) <= cy or cx < 0 or len(self.mines[cy]) <= cx:
                continue
            if (cx, cy) in visited:
                continue

            visited.add((cx, cy))
            yield cx, cy

            if self.countAdjacentMines(cx, cy) == 0:
                for i in [-1, 0, 1]:
                    for j in [-1, 0, 1]:
                        if (cx + i, cy + j) not in visited:
                            bfs.append((cx + i, cy + j))
