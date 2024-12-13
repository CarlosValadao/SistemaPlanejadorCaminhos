import sys
from time import sleep
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QPoint
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QLabel
from PyQt5.QtGui import QPainter, QColor, QFont
import SupervisorClient
from trajetoria import calcular_campo_potencial, planejar_trajetoria
from threading import Thread
from constants import NXT_BLUETOOTH_MAC_ADDRESS
from os import environ
from math import ceil

'''
trajetoria: lista de tuplas contendo posição e a orientação no formato (x, y, grau)
'''

def dividir_por_10(lista):
    return [
        ((x1 // 10, y1 // 10), (x2 // 10, y2 // 10))
        for ((x1, y1), (x2, y2)) in lista
]

def multiplicar_por_10(lista):
    return [
        (x * 10, y * 10)  # Multiplica apenas os dois primeiros valores (x, y)
        for (x, y) in lista
    ]

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
        self.robot_position = [260, 170]
        self.rastro = []
        self.obstacles = []
        self.objective = []
        self.robot_obstacles = [((75.5, 179.5), (85.5, 169.5)), ((75.0, 169.5), (85.0, 159.5)), ((75.0, 160.0), (85.0, 150.0)), ((115.0, 179.5), (125.0, 169.5)), ((115.5, 169.5), (125.5, 159.5)), ((115.0, 159.5), (125.0, 149.5)), ((142.5, 179.5), (152.5, 169.5)), ((142.0, 169.5), (152.0, 159.5)), ((142.0, 160.0), (152.0, 150.0)), ((181.5, 179.0), (191.5, 169.0)), ((181.5, 170.0), (191.5, 160.0)), ((182.0, 160.0), (192.0, 150.0)), ((115.0, 30.5), (125.0, 20.5)), ((114.5, 20.5), (124.5, 10.5)), ((115.5, 10.5), (125.5, 0.5)), ((182.0, 29.0), (192.0, 19.0)), ((181.5, 19.0), (191.5, 9.0)), ((181.5, 9.5), (191.5, -0.5)), ((142.0, 31.0), (152.0, 21.0)), ((142.0, 21.5), (152.0, 11.5)), ((142.0, 12.0), (152.0, 2.0)), ((75.0, 30.5), (85.0, 20.5)), ((75.0, 21.5), (85.0, 11.5)), ((75.0, 12.0), (85.0, 2.0))]
        #self.robot_obstacles = [((80, 180), (90, 170)), ((80, 16), (90, 150)), ((150, 180), (160.0, 170.0)), ((150.0, 160), (160, 170)), ((180, 180), (190, 170)), ((180, 160), (190, 150)), ((80, 30), (90, 20)), ((80, 10), (90, 40)), ((110, 30), (120, 20)), ((110, 10), (120, 0)), ((150, 30), (160, 20)), ((150, 10), (160, 0)), ((180, 30), (190, 20)), ((180, 10), (190, 0))]
        #self.robot_obstacles = [((76.0, 179.0), (86.0, 169.0)), ((75.5, 169.0), (85.5, 159.0)), ((75.5, 159.5), (85.5, 149.5)), ((115.5, 180.0), (125.5, 170.0)), ((115.0, 170.0), (125.0, 160.0)), ((115.5, 159.5), (125.5, 149.5)), ((142.0, 179.0), (152.0, 169.0)), ((141.5, 170.0), (151.5, 160.0)), ((142.0, 159.5), (152.0, 149.5)), ((181.5, 179.5), (191.5, 169.5)), ((181.5, 170.5), (191.5, 160.5)), ((181.5, 160.0), (191.5, 150.0)), ((75.0, 30.5), (85.0, 20.5)), ((75.5, 20.0), (85.5, 10.0)), ((75.0, 10.5), (85.0, 0.5)), ((115.5, 30.0), (125.5, 20.0)), ((115.0, 21.0), (125.0, 11.0)), ((115.5, 11.0), (125.5, 1.0)), ((142.0, 31.5), (152.0, 2)), ((180, 10), (190, 0)), ((76.0, 179.0), (86.0, 169.0)), ((75.5, 169.0), (85.5, 159.0)), ((75.5, 159.5), (85.5, 149.5)), ((115.5, 180.0), (125.5, 170.0)), ((115.0, 170.0), (125.0, 160.0)), ((115.5, 159.5), (125.5, 149.5)), ((142.0, 179.0), (152.0, 169.0)), ((141.5, 170.0), (151.5, 160.0)), ((142.0, 159.5), (152.0, 149.5)), ((181.5, 179.5), (191.5, 169.5)), ((181.5, 170.5), (191.5, 160.5)), ((181.5, 160.0), (191.5, 150.0)), ((75.0, 30.5), (85.0, 20.5)), ((75.5, 20.0), (85.5, 10.0)), ((75.0, 10.5), (85.0, 0.5)), ((115.5, 30.0), (125.5, 20.0)), ((115.0, 21.0), (125.0, 11.0)), ((115.5, 11.0), (125.5, 1.0)), ((142.0, 31.5), (152.0, 29.5)), ((181.5, 179.5), (191.5, 169.5)), ((181.5, 170.5), (191.5, 160.5)), ((181.5, 160.0), (191.5, 150.0)), ((75.0, 30.5), (85.0, 20.5)), ((75.5, 20.0), (85.5, 10.0)), ((75.0, 10.5), (85.0, 0.5)), ((115.5, 30.0), (125.5, 20.0)), ((115.0, 21.0), (125.0, 11.0)), ((115.5, 11.0), (125.5, 1.0)), ((142.0, 31.5), (152.0, 2, 10.0)), ((75.0, 10.5), (85.0, 0.5)), ((115.5, 30.0), (125.5, 20.0)), ((115.0, 21.0), (125.0, 11.0)), ((115.5, 11.0), (125.5, 1.0)), ((142.0, 31.5), (152.0, 21.5)), ((141.5, 21.5), (151.5, 11.5)), ((141.0, 12.5), (151.0, 2.5)), ((181.0, 30.5), (191.0, 20.5)), ((181.0, 21.0), (191.0, 11.0)), ((181.0, 10.5), (191.0, 0.5))]
        self.robot_objective = []
        self.trajetoria = []
        self.campo = []
        self.drawing = False
        self.start_point = None
        self.rect_width = 20
        self.rect_height = 20
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

        square_width = 60
        square_height = 60
        offset_x = 170 
        offset_y = 1
        spacing_x = 73 # distancia entre um block e outro no eixo (medida real 36.5)
        spacing_y = 238 # altura y (360) - primeiro bloco (60) - segundo bloco (60) - offset em cima e em baixo (1+1)

        for row in range(2):
            for col in range(2):
                x = offset_x + col * (square_width + spacing_x)
                y = offset_y + row * (square_height + spacing_y)
                painter.setPen(Qt.black)
                painter.drawRect(x, y, square_width, square_height)

        painter.setBrush(QColor(200, 0, 0, 150))
        for i in range(len(self.rastro) - 1):
            painter.drawLine(self.rastro[i][0], self.rastro[i][1], self.rastro[i + 1][0], self.rastro[i + 1][1])

        painter.setBrush(QColor(255, 0, 0))
        painter.drawEllipse(self.robot_position[0], self.robot_position[1], 20, 20)

        #obstaculo
        painter.setPen(QColor(100, 100, 100))
        painter.setBrush(QColor(200, 200, 200, 100))
        for obstacle in self.obstacles:
            start, end = obstacle
            if start is not None and end is not None:
                painter.drawRect(start.x(), start.y(), self.rect_width, self.rect_height)

        #objetivo
        painter.setBrush(QColor(0, 200, 0))
        for obj in self.objective:
            painter.drawEllipse(obj.x(), obj.y(), 10, 10)

        #trajetoria
        painter.setBrush(QColor(0, 0, 255))
        for pos in self.trajetoria:
            painter.drawEllipse(pos[0]*2, 360 - pos[1]*2, 5, 5)

        # desenha o retangulo
        if self.drawing and self.start_point:
            painter.drawRect(self.start_point.x(), self.start_point.y(), self.rect_width, self.rect_height)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.parent().drawing_mode:
            self.drawing = True
            self.start_point = event.pos()

        if event.button() == Qt.LeftButton and self.parent().adding_objective_mode:
            self.add_objective(event.pos())


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            if self.start_point is not None:  # Check for valid start point
                # Define the end point based on the starting point and the rect dimensions
                end_point = QPoint(self.start_point.x() + self.rect_width, self.start_point.y() + self.rect_height)
                self.obstacles.append((self.start_point, end_point))
                print(f"Rectangle added: Start {self.start_point}, End {end_point}")
                self.robot_obstacles.append(((self.start_point.x()/2, 180 - (self.start_point.y())/2), (end_point.x()/2, 180 - (end_point.y()/2))))
                print(self.robot_obstacles)
            self.start_point = None
            self.update()

    def add_objective(self, position):
        if(len(self.objective) > 0):
            self.objective.pop()
            self.robot_objective.pop()
        self.objective.append(position)
        self.robot_objective.append((position.x()/2, 180-(position.y()/2)))
        print(self.robot_objective)
        print(f"Objective added at: {position}")
        self.update()

    def set_rect_size(self, width, height):
        """Ajusta o tamanho dos retângulos desenhados."""
        self.rect_width = width
        self.rect_height = height

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

        self.drawing_mode = False
        self.adding_objective_mode = False  # Variável para controlar o modo de adicionar objetivo
        self.draw_button = QPushButton('Desenhar Obstaculo', self)
        self.draw_button.clicked.connect(self.toggle_drawing_mode)
        self.control_layout.addWidget(self.draw_button)

        self.add_objective_button = QPushButton('Adicionar Objetivo', self)  # Novo botão
        self.add_objective_button.clicked.connect(self.toggle_adding_objective_mode)
        self.control_layout.addWidget(self.add_objective_button)

        self.trajetoria_button = QPushButton('Gerar Trajetoria', self)
        self.trajetoria_button.clicked.connect(self.path_planning)
        self.control_layout.addWidget(self.trajetoria_button)

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

    def toggle_drawing_mode(self):
        self.drawing_mode = not self.drawing_mode
        if self.drawing_mode:
            self.draw_button.setStyleSheet("background-color: green; color: white;")
        else:
            self.draw_button.setStyleSheet("")

    def toggle_adding_objective_mode(self):
        self.adding_objective_mode = not self.adding_objective_mode
        if self.adding_objective_mode:
            self.add_objective_button.setStyleSheet("background-color: green; color: white;")
        else:
            self.add_objective_button.setStyleSheet("")

    def path_planning(self):
        grid_size = (27, 18)
        obstaculos = dividir_por_10(self.robot_area.robot_obstacles)
        objetivo = [tuple(valor // 10 for valor in tupla) for tupla in self.robot_area.robot_objective]
        inicio = (13, 9)

        campo = calcular_campo_potencial(grid_size, objetivo[0], obstaculos, 1)
        trajetoria = planejar_trajetoria(campo, inicio, objetivo)
        #print(trajetoria)

        self.robot_area.trajetoria = multiplicar_por_10(trajetoria)
        print(self.robot_area.trajetoria)
        #self.robot_area.rastro.extend(self.robot_area.trajetoria)
        self.robot_area.update()
        print("Trajetória gerada:", self.robot_area.trajetoria)

    def close_application(self):
        print("Aplicação fechando...")
        self.close()

if __name__ == '__main__':
    #environ['QT_QPA_PLATFORM'] = 'xcb'
    #supervisor_client = SupervisorClient.SupervisorClient(NXT_BLUETOOTH_MAC_ADDRESS)
    #supervisor_client.catch_all_messages()
    app = QApplication(sys.argv)
    window = RobotInterface()
    window.show()
    sys.exit(app.exec_())
