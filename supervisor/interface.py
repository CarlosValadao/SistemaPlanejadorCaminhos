import sys
from time import sleep
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QLabel
from PyQt5.QtGui import QPainter, QColor, QFont
import SupervisorClient
from threading import Thread
from constants import NXT_BLUETOOTH_MAC_ADDRESS
from os import environ
from math import ceil

class RobotPositionThread(QThread):
    position_updated = pyqtSignal(int, int, int)

    def run(self):
        while True:
            received_messages = supervisor_client.get_data_msgs()
            if(received_messages):
                for data_msg in received_messages:
                    (new_x, new_y, region) = data_msg
                    new_x = ceil(new_x) 
                    new_y = ceil(new_y)
                    self.position_updated.emit(new_x, new_y, region)

class RobotCommThread(QThread):
    control_signal = pyqtSignal(int)
    def run(self):
        while True:
            received_comms = supervisor_client.get_response_msgs()
            if received_comms:
                for comm in received_comms:
                    self.control_signal.emit(comm)

class RobotArea(QFrame):
    def __init__(self):
        super().__init__()
        self.robot_position = [20, 340]
        self.rastro = []
        self.setFixedSize(540, 360)

    def update_robot_position(self, new_position):
        self.robot_position = new_position
        self.rastro.append(new_position)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRect(0, 0, self.width(), self.height())
        painter.setPen(Qt.black)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(1, 1, 80, 358)
        painter.drawRect(self.width() - 81, 1, 80, 358)

        square_width = 60
        square_height = 60
        offset_x = 165
        offset_y = 1
        spacing = 89
        
        for row in range(3):
            for col in range(2):
                x = offset_x + col * (square_width + spacing)
                y = offset_y + row * (square_height + spacing)
                painter.setPen(Qt.black)
                painter.drawRect(x, y, square_width, square_height)

        painter.setBrush(QColor(200, 0, 0, 150))
        for pos in self.rastro:
            painter.drawEllipse(pos[0], pos[1], 5, 5)

        painter.setBrush(QColor(255, 0, 0))
        painter.drawEllipse(self.robot_position[0], self.robot_position[1], 20, 20)

class RobotInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Controle do Robô')
        self.setFixedSize(800, 400)
        self.main_layout = QHBoxLayout()
        font = QFont()
        font.setPointSize(11)
        label_width = 190
        label_height = 50

        self.control_panel = QFrame(self)
        self.control_panel.setFixedWidth(200)
        self.control_layout = QVBoxLayout()

        self.button = QPushButton('Ativar Robô', self)
        self.button.clicked.connect(self.toggle_robot)
        self.control_layout.addWidget(self.button)
        
        self.quit_button = QPushButton('Sair', self)
        self.quit_button.clicked.connect(self.close_application)
        self.control_layout.addWidget(self.quit_button)

        self.region_label = QLabel('Região: Base', self)
        self.region_label.setFont(font)
        self.region_label.setFixedSize(label_width, label_height)
        self.region_label.setStyleSheet("""
            QLabel {
                border: 2px solid #333;
                border-radius: 8px;
                background-color: #f0f0f0;
                padding: 8px;
                color: #005500;
                font-weight: bold;
            }
        """)
        self.control_layout.addWidget(self.region_label)

        self.coordinates_label = QLabel('Coordenadas: (0, 0)', self)
        self.coordinates_label.setFont(font)
        self.coordinates_label.setFixedSize(label_width, label_height)
        self.coordinates_label.setStyleSheet("""
            QLabel {
                border: 2px solid #333;
                border-radius: 8px;
                background-color: #f0f0f0;
                padding: 8px;
                color: #550000;
                font-weight: bold;
            }
        """)
        self.control_layout.addWidget(self.coordinates_label)

        self.control_panel.setLayout(self.control_layout)
        self.main_layout.addWidget(self.control_panel)

        self.robot_area = RobotArea()
        self.robot_area.setStyleSheet("background-color: white;")
        self.main_layout.addWidget(self.robot_area)

        self.setLayout(self.main_layout)

        self.robot_active = False
        self.position_thread = RobotPositionThread()
        self.position_thread.position_updated.connect(self.update_robot_position)
        
        self.comm_thread = RobotCommThread()
        self.comm_thread.control_signal.connect(self.control_interface)

    def toggle_robot(self):
        self.comm_thread.start()
        if not self.robot_active:
            supervisor_client.send_message(request_code=0)

    def control_interface(self, control):
        if control == 3:
            self.robot_active = True
            self.button.setText('Iniciando')
            self.button.setEnabled(False)
            self.button.setStyleSheet("background-color: yellow; color: black;")

            timer = QTimer(self)
            timer.setSingleShot(True)

            def finish_activation():
                self.button.setText('Robô Ativado')
                self.button.setStyleSheet("")

            timer.timeout.connect(finish_activation)
            timer.start(3000)
            self.robot_area.rastro.clear()
            self.position_thread.start()
        elif control == 2:
            self.button.setText('Ativar Robô')
            self.button.setEnabled(True)
            self.position_thread.terminate()
            self.robot_active = False

    def update_robot_position(self, new_x, new_y, regiao):
        robot_area_width = self.robot_area.width()
        robot_area_height = self.robot_area.height()
        new_x = max(0, min(new_x + 20, robot_area_width - 20))
        new_y = max(0, min(150 - new_y, robot_area_height - 20))
        new_x = new_x * 2
        new_y = new_y * 2
        self.robot_area.update_robot_position([new_x, new_y])

        self.coordinates_label.setText(f'Coordenadas: ({new_x}, {new_y})')
        if regiao == 0:
            self.region_label.setText('Região: Base')
        elif regiao == 1:
            self.region_label.setText('Região: Pátio')
        elif regiao == 2:
            self.region_label.setText('Região: Estoque')
        else:
            self.region_label.setText('Região: Desconhecida')

    def close_application(self):
        print("Aplicação fechando...")
        self.close()

if __name__ == '__main__':
    environ['QT_QPA_PLATFORM'] = 'xcb'
    supervisor_client = SupervisorClient.SupervisorClient(NXT_BLUETOOTH_MAC_ADDRESS)
    supervisor_client.catch_all_messages()
    app = QApplication(sys.argv)
    window = RobotInterface()
    window.show()
    sys.exit(app.exec_())
