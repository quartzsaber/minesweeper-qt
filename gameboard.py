
FLAG_TYPE_NO_FLAG = 0  # 아무런 표시도 되어있지 않음
FLAG_TYPE_MINE = 1  # 지뢰임을 나타내는 깃발
FLAG_TYPE_QUESTION = 2  # 물음표 표시
FLAG_TYPE_BLOWN_UP_MINE = 3  # 폭발해버린 지뢰. cycle_cell_flag는 이 깃발을 사용하지 않음
FLAG_TYPE_DISPLAYED_MINE = 4  # 싱글플레이 게임이 끝나서 나타난 지뢰. cycle_cell_flag는 이 깃발을 사용하지 않음

# 모든 2차원 리스트는 arr[y][x] 처럼 접근함

# 지뢰찾기 게임판
class GameBoard:
    def __init__(self):
        # 이 변수들은 여기서는 선언만 하고 new_game() 에서 초기화합니다
        self.mines = [[]]  # 2차원 리스트, 지뢰인 칸은 True, 아니면 False
        self.opened = [[]]  # 2차원 리스트, 열린 칸은 True, 아니면 False
        self.flags = [[]]]  # 2차원 리스트, FLAG_TYPE_* 으로 각 칸을 표시함
        self.start_time = 0  # 시작했을때의 시간. 파이썬에 내장된 time.time() 함수 참고

    # w x h 크기의 게임판을 만들고, mines개수의 지뢰를 랜덤하게 배치
    def new_game(self, w: int, h: int, mines: int):
    
    # pickle을 이용해 이 게임판을 문자열로 저장해 리턴
    def serialize_game(self):
    
    # pickle을 이용해 이 게임판을 불러옴
    def deserialize_game(self):
    
    # 해당 칸의 플래그 정보를 바꿈
    def cycle_cell_flag(self, x: int, y: int):
    
    # 해당 칸이 좌클릭이나 우클릭 할 수 있다면 True
    def check_cell_clickable(self, x: int, y: int)
    
    # 해당 칸을 엶 (좌클릭 함)
    # 해당 칸에 지뢰가 있었을 경우 True를 리턴
    # 지뢰로 표시해놓은 칸은 무시
    def mark_cell(self, x: int, y: int):
    
    # 주변 3x3 칸을 엶
    # 지뢰로 표시해놓은 칸은 무시
    def mark_cell_adjecent(self, x: int, y: int)
    
    # 남아있는 지뢰 개수를 셈 (잘못 표기한것도 포함)
    def count_remaining_mine(self):
    
    # 제대로 표기한 지뢰 개수를 셈
    def count_flagged_mine(self)
    
    # 게임에서 승리했는지 확인 (게임이 끝났으면 True)
    def check_finished(self):
        return count_flagged_mine() == 0
    
    # 해당 칸에 써있는 숫자를 가져옴
    # 아직 열리지 않은 칸일 경우 False
    # 열렸지만 빈 칸일경우 0
    def get_cell_text(self, x: int, y: int):
    
    # 해당 칸의 깃발 정보를 가져옴
    # (cycle_cell_flag 함수와 FLAG_TYPE_* 변수 참고)
    def get_cell_flag(self, x: int, y: int):
    
    # 게임을 시작하고 몇 초가 지났는지 리턴
    def get_playtime(self):

