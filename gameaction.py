# 클라이언트가 게임에서 행한 동작을 dict 형식으로 바꿈
class GameAction:
    def openCell(self, x, y):
        dic = {'action': 'openCell', 'x': x, 'y': y}
        return dic

    def openCellAdjacent(self, x, y):
        dic = {'action': 'openCellAdjacent', 'x': x, 'y': y}
        return dic

    def cycleCellImage(self, x, y):
        dic = {'action': 'cycleCellImage', 'x': x, 'y': y}
        return dic
