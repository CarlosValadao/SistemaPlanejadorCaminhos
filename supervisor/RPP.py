import Assets

# Robotics PBL Protocol

from typing import Final

# Header message type
REQUEST: Final = '1'
RESPONSE: Final = '2'
POSITION: Final = '3'

REQUEST_I: Final = 1
RESPONSE_I: Final = 2
POSITION_I: Final = 3

# Request codes
ACTIVATE: Final = 0
STATUS: Final = 1

# Response codes
SUCCESS: Final = 0
ERROR: Final = 1
COMPLETED: Final = 2
ONGOING: Final = 3

GO: Final = 0

BASE: Final = 0
STOCK: Final = 1
MIDDLE: Final = 2

START_SENDING_COORDS: Final = 0
STOP_SENDING_COORDS : Final = 2

MAX_BYTE_TRANSFER: Final = 57

def parse_message(message: str) -> tuple[int]|int:
    #message = message.replace('\x00', '')
    message_head = message[0]
    message_tail = message[2:]
    print(f'MENSAGEM RECEBIDA -> {message}')
    if message_head == RESPONSE:
        response_type = int(message_tail)
        return response_type
    elif message_head == POSITION:
        (displacement, guidance) = map(lambda x: float(x), message_tail.split(sep=';'))
        #print(f'message -> {message}')
        #print(f'x -> {displacement} && y -> {guidance}')
        return (displacement, guidance)


def format_message(request_code: int) -> bytes:
    return f'1;{request_code}'.encode(encoding='utf-8')

'''
packet_size em funcao do tamanho da string e nao da quantidade de numeros
'''
def pack_coordinates(data: list[tuple], packet_size: int = MAX_BYTE_TRANSFER) -> list[bytes]:
    packets = []
    chunk = ''
    str_point = ''
    data_content = [coordinate for point in data for coordinate in point]
    data_size = len(data_content)
    i = 0
    while(i < data_size):
        str_point = Assets.num_to_str(data_content[i])
        chunk_len = len(chunk)
        str_point_len = len(str_point)
        if (chunk_len + str_point_len == packet_size) or (chunk_len + str_point_len + 1) == packet_size:
            chunk = chunk + str_point
            packets.append(chunk.encode())
            chunk = ''
        elif chunk_len + str_point_len + 1 < packet_size:
            chunk = chunk + f'{str_point} '
        else:
            packets.append(chunk[:-1].encode())
            chunk = f'{str_point} '
        i = i + 1
    if chunk:
        packets.append(chunk[:-1].encode())
    return packets