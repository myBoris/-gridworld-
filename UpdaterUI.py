import time
import random

from PyQt5.QtCore import QObject, pyqtSignal, QThread

from StateMachine import StateMachine

# 全局变量，表示网格大小
GRID_ROWS = 5
GRID_COLS = 5

#
forbidden_box = [ (1, 1), (1, 2), (2, 2), (3, 1), (3, 3), (4, 1)]
start_end_positions = [(2, 1), (3, 2)]
action = ['','↑','↓', '←', '→', '●']

class UpdateUI(QObject):
    update_signal = pyqtSignal(int, int, str, str, int)

    update_now = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.count = 0
        self.loopFlag = True

    def run(self):
        time.sleep(3)
        state_machine = StateMachine(GRID_COLS, GRID_ROWS)
        path = state_machine.iterate(start_end_positions[0][0], start_end_positions[0][1], callback=self.stateMachineCallBack)



        # while self.loopFlag:
        #
        #     x = random.randint(1, 3)
        #     y = random.randint(1, 3)
        #
        #     self.update_now.emit(x,y)
        #
        #     actionIndex = self.count % 6
        #     self.update_signal.emit(1, 1, f"{self.count}", f"{self.count}", actionIndex)
        #     self.count = self.count + 1
        #     time.sleep(2)  # 每秒更新一次
        #     if self.count > 20:
        #         self.loopFlag = False


    def stateMachineCallBack(self,pre_x, pre_y, x, y, action):
        print("direction :" + Const.action[action])
        print("direction update_now:" + str(x) + str(y))
        self.update_now.emit(x,y)
        self.update_signal.emit(pre_x, pre_y, f"", f"", action)