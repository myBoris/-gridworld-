import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel, QHBoxLayout, \
    QStackedLayout, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsSimpleTextItem
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QTimer

from UpdaterUI import UpdateUI, GRID_ROWS, GRID_COLS, forbidden_box, start_end_positions, action


class GridWorldGame(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.grid_layout = QGridLayout()

        # 创建中心小部件和布局
        central_widget = QWidget(self)
        self.grid_layout = QGridLayout(central_widget)

        for row in range(0, GRID_ROWS):
            for col in range(0, GRID_COLS):

                # 根据下标是否在yellow_boxes列表中来设置按钮的背景颜色
                if (row, col) in forbidden_box:
                    color = "background-color: #F4B860;"
                else:
                    color = "background-color: white;"

                # 创建一个新的QWidget，用于放置垂直布局
                layout_widget = QWidget()
                layout_widget.setStyleSheet(color)  # 设置背景颜色

                # 为这个QWidget创建一个垂直布局
                v_layout = QVBoxLayout(layout_widget)

                # 第一层：水平布局，包含两个标签
                h_layout1_widget = QWidget()
                h_layout1_widget.setStyleSheet("background-color: white;")
                h_layout1 = QHBoxLayout()

                # id
                idLabel = QLabel(f"state= {row}{col}")
                h_layout1.addWidget(idLabel)

                # 起始终点标签
                start_end_label = QLabel()
                if (row, col) == start_end_positions[0]:
                    start_end_label_str = "start"
                    #start_end_label.setStyleSheet("QLabel { border: 1px solid black;color: red; }")
                    start_end_label.setStyleSheet("QLabel { color: red; }")
                elif (row, col) == start_end_positions[1]:
                    start_end_label_str = "end"
                    start_end_label.setStyleSheet("QLabel { color: red; }")
                else:
                    start_end_label_str = ""
                start_end_label.setText(start_end_label_str)

                h_layout1.addWidget(start_end_label)

                indexNow = QLabel(f"")
                indexNow.setStyleSheet("QLabel { color: red; }")
                indexNow.setObjectName(f"{row}{col}indexNow")
                h_layout1.addWidget(indexNow)
                v_layout.addLayout(h_layout1)

                # 第二层：垂直布局，包含两个标签
                h_layout2_widget = QWidget()
                h_layout2_widget.setStyleSheet("background-color: white;")
                h_layout2 = QVBoxLayout()

                actionValueLabel = QLabel(f"actionVal =")
                actionValueLabel.setObjectName(f"{row}{col}actionValue")
                h_layout2.addWidget(actionValueLabel)

                stateValueLabel = QLabel(f"stateVal = ")
                stateValueLabel.setObjectName(f"{row}{col}stateValue")
                h_layout2.addWidget(stateValueLabel)

                v_layout.addLayout(h_layout2)
                # 第三层：水平布局，一个标签
                h_layout3 = QHBoxLayout()

                actionLabel = QLabel(f"action = {action[0]}")
                actionLabel.setObjectName(f"{row}{col}action")
                h_layout3.addWidget(actionLabel)

                v_layout.addLayout(h_layout3)
                # 将包含垂直布局的QWidget添加到网格布局的相应格子中
                self.grid_layout.addWidget(layout_widget, row, col)


        self.setLayout(self.grid_layout)
        self.setWindowTitle('Grid World Game')
        self.setGeometry(100, 100, 600, 600)

        # 创建工作线程
        self.worker = UpdateUI()
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.update_signal.connect(self.update_label)  # 连接信号
        self.worker.update_now.connect(self.startBlinking)  # 连接信号
        self.thread.start()

        # 创建定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.toggleLabelVisibility)

        # 当前闪烁的标签，初始时没有标签闪烁
        self.current_blinking_label = None

    # 通过对象名获取标签的函数
    def get_label_by_name(self, name):
        return self.findChild(QLabel, name)
    @pyqtSlot(int, int, str, str, int)
    def update_label(self, row, col, actionValue, stateValue, actionIndex):
        actionValueLabel = self.get_label_by_name(f"{row}{col}actionValue")
        actionValueLabel.setText(f"actionVal = {actionValue}")

        stateValueLabel = self.get_label_by_name(f"{row}{col}stateValue")
        stateValueLabel.setText(f"stateVal = {stateValue}")

        actionLabel = self.get_label_by_name(f"{row}{col}action")
        actionLabel.setText(f"action = {action[actionIndex]}")

    def toggleLabelVisibility(self):
        # 切换当前闪烁标签的可见性
        if self.current_blinking_label:
            if not self.current_blinking_label.text():
                self.current_blinking_label.setText(f"★")
            else:
                self.current_blinking_label.setText(f"")

    @pyqtSlot(int, int)
    def startBlinking(self, row, col):
        nowBlinking = self.get_label_by_name(f"{row}{col}indexNow")
        nowBlinking.setText(f"★")
        # 开始让指定的标签闪烁
        if self.current_blinking_label is not nowBlinking:
            if self.current_blinking_label:
                self.current_blinking_label.setText(f"")  #
            self.current_blinking_label = nowBlinking


    def stopBlinking(self):
        # 停止闪烁
        self.timer.stop()
        if self.current_blinking_label:
            self.current_blinking_label.setText(f"")
            self.current_blinking_label = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = GridWorldGame()
    game.show()

    # 让label2开始闪烁
    game.startBlinking(start_end_positions[0][0],start_end_positions[0][1])

    if not game.timer.isActive():
        game.timer.start(500)  # 间隔时间（毫秒）

    sys.exit(app.exec_())