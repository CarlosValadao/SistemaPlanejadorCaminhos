from nxt.locator import find
from nxt.brick import Brick
from nxt.error import DirectProtocolError
from constants import MAILBOX1, MAILBOX3, MAILBOX10, NXT_BLUETOOTH_MAC_ADDRESS
import RPP
from threading import Thread, Lock
from nxt.locator import BrickNotFoundError
from nxt.error import DirectProtocolError
from time import sleep
from os import name, system
from Assets import datetime_formated

import math

# By default use MAILBOX1 to send messages
# and MAILBOX10 to receive reponse messages
#     MAILBOX3  to receive data messages

# Manages the communication between the supervisor and the robot over Bluetooth
class SupervisorClient:
    def __init__(self, nxt_bluetooth_mac):
        self._is_nxt_connected: bool = False
        self._nxt_brick: Brick = self.establish_nxt_connection(nxt_bluetooth_mac)
        # As soon as messages are read they're stored here
        self._recv_data_msg: list[tuple[int]] = []
        self._recv_response_msg: list[int] = []
        # mutexes
        self._msg_data_lock: Lock = Lock()
        self._there_is_running_program_on_nxt: bool = False
    
    # --- Connection Management ---
    
    def connect_to_nxt(self, nxt_bluetooth_mac: str) -> Brick|None:
        try:
            nxt_brick = find(host=nxt_bluetooth_mac)
            self._is_nxt_connected = True
            self.show_success_message('Connected on NXT :]')
            return nxt_brick
        except BrickNotFoundError:
            self.clear_console()
            self.show_warning_message("NXT is unreachable")
            self.show_warning_message("Trying to connect agin...")
            self._is_nxt_connected = False
            return None
    
    """force the connection with the NXT, ad infinitum every 500ms
    
    :param str nxt_bluetooth_mac: NXT MAC address
    
    :return: The nxt Brick object
    :rtype: nxt.Brick.Brick
    """
    def force_nxt_connection(self, nxt_bluetooth_mac: str) -> Brick:
        while not self._is_nxt_connected:
            nxt_brick = self.connect_to_nxt(nxt_bluetooth_mac)
            sleep(0.5)
        return nxt_brick

    def establish_nxt_connection(self, host: str) -> Brick:
        nxt_brick = self.connect_to_nxt(host)
        if not nxt_brick:
            nxt_brick = self.force_nxt_connection(host)
        return nxt_brick

    def close_nxt_connection(self) -> None:
        return self._nxt_brick.close()
    
    # --- Message Handling ---
    
    def send_message(self, request_code) -> None:
        try:
            formatted_msg = RPP.format_message(request_code=request_code)
            self._nxt_brick.message_write(MAILBOX1, formatted_msg)
        except DirectProtocolError:
            self.show_warning_message("It's impossible to send messages\
                                    - there's nothing running on NXT")
    
    def _read_message(self, mailbox: int) -> str:
        try:
            (inbox, received_message) = self._nxt_brick.message_read(mailbox, 0, True)
            return received_message.decode().replace('\x00', '')
        except DirectProtocolError:
            return ''
    
    def _read_all_messages(self, mailbox: int, is_data_msg: bool) -> None:
        has_active_program = self._is_running_program_on_nxt()
        while has_active_program:
            received_message = self._read_message(mailbox)
            #print(f'MENSAGEM RECEBIDA -> {received_message}')
            if received_message:
                data = RPP.parse_message(received_message)
                if is_data_msg:
                    with self._msg_data_lock:
                        #vetor_desc_tmp = [0,0] # Vetor deslocamento x,y
                        #desloc = data[0] # O quanto o robô se deslocou
                        #angulo = data[1] # A orientação do deslocamento do robô
                        #orientacao_rad = math.radians(angulo) # Conversão do angulo para radianos
                        #regiao = data[2]
                        # Para o deslocamento em X
                        #vetor_desc_tmp[0] = self._recv_data_msg[len(self._recv_data_msg)-1][0] + desloc*math.cos(orientacao_rad) 
                        # Para o deslocamento em Y
                        #vetor_desc_tmp[1] = self._recv_data_msg[len(self._recv_data_msg)-1][1] + desloc*math.sin(orientacao_rad)
                        #self._recv_data_msg.append((vetor_desc_tmp[0], vetor_desc_tmp[1], regiao))
                        self._recv_data_msg.append(data)
                else:
                    with self._msg_data_lock:
                        self._recv_response_msg.append(data)
                print(f'[RECEIVED] -> {datetime_formated()} - {data}')
            has_active_program = self._is_running_program_on_nxt()
        self.show_warning_message("It's impossible to read new messages - \
                                there's nothing running on NXT")
        self.show_warning_message('Ending NXT connection')
        self.close_nxt_connection()
    
    def get_data_msgs(self) -> list[tuple[int]]:
        with self._msg_data_lock:
            temp = self._recv_data_msg.copy()
            self._recv_data_msg = []
        return temp
    
    def get_response_msgs(self) -> list[int]:
        with self._msg_data_lock:
            temp = self._recv_response_msg.copy()
            self._recv_response_msg = []
        return temp
    
    # --- Utilities ---
    
    """Start two threads that catch all the messages from the NXT Brick
        from two differents mailboxes, using self._read_all_messages
    """
    def catch_all_messages(self) -> None:
        Thread(target=self._read_all_messages, kwargs={'mailbox': MAILBOX3, 'is_data_msg': True}).start()
        Thread(target=self._read_all_messages, kwargs={'mailbox': MAILBOX10, 'is_data_msg': False}).start()
    
    def _is_running_program_on_nxt(self) -> bool:
        try:
            current_program_name = self._nxt_brick.get_current_program_name()
            if current_program_name:
                self._current_program_name = current_program_name
                return True
        except DirectProtocolError:
            self._current_program_name = None
            return False
    
    def get_nxt_brick(self) -> Brick|None:
        return self._nxt_brick

    def clear_console(self) -> None:
        if name == 'nt':
            system('cls')
        else:
            system('clear')

    def show_warning_message(self, message) -> None:
        print(f'[WARNING] - {message}')
    
    def show_success_message(self, message) -> None:
        print(f'[SUCCESS] - {message}')
    
if __name__ == '__main__':
    supervisor_client = SupervisorClient(NXT_BLUETOOTH_MAC_ADDRESS)
    supervisor_client.send_message(request_code=RPP.GO)
    supervisor_client.catch_all_messages()
    # supervisor_client.close_nxt_connection()
