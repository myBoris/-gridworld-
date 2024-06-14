import random
import sys
import numpy as np
import torch
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QBrush, QPen

from agent.net import QNetwork


class GridGameEnv:
    def __init__(self, grid_array):
        self.grid = grid_array
        self.start_pos = tuple(np.argwhere(self.grid == 8)[0])
        self.goal_pos = tuple(np.argwhere(self.grid == 9)[0])
        self.current_pos = self.start_pos

        self.state_size = grid_array.size
        self.action_size = 5  # 上, 下, 左, 右, 停

    def reset(self):
        self.current_pos = self.start_pos
        return self._get_obs()

    def step(self, action):
        x, y = self.current_pos
        if action == 0:  # 上
            x = max(0, x - 1)
        elif action == 1:  # 下
            x = min(self.grid.shape[0] - 1, x + 1)
        elif action == 2:  # 左
            y = max(0, y - 1)
        elif action == 3:  # 右
            y = min(self.grid.shape[1] - 1, y + 1)
        elif action == 4:  # 停
            pass

        if self.grid[x, y] in [0, 1, 8, 9]:
            self.current_pos = (x, y)

        done = self.current_pos == self.goal_pos
        reward = 1 if done else -0.1
        return self._get_obs(), reward, done, {}

    def _get_obs(self):
        obs = np.zeros_like(self.grid)
        obs[self.current_pos] = 1
        return obs

    def render(self):
        print(self.grid)
        print(f'当前坐标: {self.current_pos}')


class GridGameWidget(QWidget):
    def __init__(self, env):
        super().__init__()
        self.env = env
        self.start_end_positions = [self.env.start_pos, self.env.goal_pos]
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 800)
        self.setWindowTitle('网格游戏环境')
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(100)

    def paintEvent(self, event):
        painter = QPainter(self)
        self.drawGrid(painter)

    def drawGrid(self, painter):
        cell_size = 200
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))

        for row in range(self.env.grid.shape[0]):
            for col in range(self.env.grid.shape[1]):
                rect = (col * cell_size, row * cell_size, cell_size, cell_size)

                # 设置背景颜色
                if self.env.grid[row, col] == 0:
                    painter.setBrush(QBrush(Qt.yellow, Qt.SolidPattern))
                elif self.env.grid[row, col] == 1:
                    painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))
                elif self.env.grid[row, col] == 8:
                    painter.setBrush(QBrush(Qt.green, Qt.SolidPattern))
                elif self.env.grid[row, col] == 9:
                    painter.setBrush(QBrush(Qt.gray, Qt.SolidPattern))

                # 绘制当前坐标
                x, y = self.env.current_pos
                if row == x and col == y:
                    painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))

                painter.drawRect(*rect)

                # 绘制状态ID标签
                idLabel = f"状态= {row}{col}"
                painter.drawText(col * cell_size + 5, row * cell_size + 20, idLabel)

                # 绘制起始终点标签
                if (row, col) == self.start_end_positions[0]:
                    start_end_label_str = "开始"
                    painter.setPen(QPen(Qt.red))
                    painter.drawText(col * cell_size + 5, row * cell_size + 40, start_end_label_str)
                    painter.setPen(QPen(Qt.black))
                elif (row, col) == self.start_end_positions[1]:
                    start_end_label_str = "结束"
                    painter.setPen(QPen(Qt.red))
                    painter.drawText(col * cell_size + 5, row * cell_size + 40, start_end_label_str)
                    painter.setPen(QPen(Qt.black))

                # 绘制动作值标签
                actionValueLabel = "动作值 ="
                painter.drawText(col * cell_size + 5, row * cell_size + 60, actionValueLabel)

                # 绘制状态值标签
                stateValueLabel = "状态值 ="
                painter.drawText(col * cell_size + 5, row * cell_size + 80, stateValueLabel)

        # # 绘制当前坐标
        # x, y = self.env.current_pos
        # painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
        # painter.drawRect(y * cell_size, x * cell_size, cell_size, cell_size)


class MainWindow(QMainWindow):
    def __init__(self, env, isTest=False):
        super().__init__()
        self.env = env
        self.isTest = isTest

        self.initUI()

        if isTest:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.agent = QNetwork(env.state_size, env.action_size).to(self.device)
            self.agent.load_state_dict(torch.load("dqn_model.pth"))
            self.agent.eval()
            self.current_state = env.reset().flatten()
            self.current_state = torch.tensor(self.current_state, dtype=torch.float32).unsqueeze(0).to(self.device)
            self.random_move_timer = QTimer(self)
            self.random_move_timer.timeout.connect(self.test)
            self.random_move_timer.start(500)  # 每500毫秒执行一次

    def initUI(self):
        self.setWindowTitle('网格游戏环境')
        self.setGeometry(100, 100, 1010, 1010)
        self.grid_widget = GridGameWidget(self.env)
        self.setCentralWidget(self.grid_widget)
        self.show()

    def keyPressEvent(self, event):
        action = None
        if event.key() == Qt.Key_Up:
            action = 0
        elif event.key() == Qt.Key_Down:
            action = 1
        elif event.key() == Qt.Key_Left:
            action = 2
        elif event.key() == Qt.Key_Right:
            action = 3
        elif event.key() == Qt.Key_Space:
            action = 4

        if action is not None:
            obs, reward, done, info = self.env.step(action)
            self.grid_widget.update()
            if done:
                print("目标达成!")
                # self.env.reset()

    def random_move(self):
        action = random.choice([0, 1, 2, 3, 4])
        obs, reward, done, info = self.env.step(action)
        self.grid_widget.update()
        if done:
            print("目标达成!")
            self.env.reset()

    def test(self):
        if self.isTest:
            action = self.agent(self.current_state).max(1)[1].view(1, 1)
            obs, reward, done, info = self.env.step(action)
            self.current_state = torch.tensor(obs.flatten(), dtype=torch.float32).unsqueeze(0).to(self.device)
            self.grid_widget.update()
            if done:
                print("目标达成!")
                self.env.reset()


def main():
    grid_array = np.array([
        [1, 1, 1, 1, 1],
        [1, 0, 0, 1, 1],
        [1, 8, 0, 1, 1],
        [1, 0, 9, 0, 1],
        [1, 0, 1, 1, 1]
    ])

    env = GridGameEnv(grid_array)
    app = QApplication(sys.argv)
    main_window = MainWindow(env)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
