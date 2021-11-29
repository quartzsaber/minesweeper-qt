# 여러 모듈에서 사용되는 상수들을 모아두는 모듈
# 특정 모듈에서만 사용되는 상수는 여기에 넣지 말 것

from enum import IntEnum


class ImageType(IntEnum):
    NONE = 0  # 특별한 표시가 없음. 닫혔으면 닫힌 모습이, 열렸으면 숫자 혹은 빈칸이 나타남
    FLAG = 1  # 지뢰임을 나타내는 깃발
    QUESTION = 2  # 물음표 표시. cycle_cell_flag는 여기까지 3개의 이미지만 사용함
    BLOWN_UP_MINE = 3  # 폭발해버린 지뢰. 빨간 배경의 지뢰 모습
    MISSED_MINE = 4  # 싱글플레이 게임이 끝날때 나타나는, 미처 지뢰라고 표기하지 못했던 지뢰. 회색 배경의 지뢰 모습
    WRONG_FLAG = 5  # 싱글플레이 게임이 끝날때 나타나는, 지뢰가 아닌데 지뢰라고 표기한 곳. 빨간 배경의 깃발 모습


DEFAULT_PORT = 5995
MAGIC_STRING = b'minesweeper-qt/1.0\n'
