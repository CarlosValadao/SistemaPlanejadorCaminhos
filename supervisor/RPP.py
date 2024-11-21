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

def parse_message(message: str) -> tuple[int]|int:
    #message = message.replace('\x00', '')
    message_head = message[0]
    message_tail = message[2:]
    print(f'MENSAGEM RECEBIDA -> {message}')
    if message_head == RESPONSE:
        response_type = int(message_tail)
        return response_type
    elif message_head == POSITION:
        (displacement, guidance, region) = map(lambda x: float(x), message_tail.split(sep=';'))
        #print(f'message -> {message}')
        #print(f'x -> {displacement} && y -> {guidance}')
        region = int(region)
        return (displacement, guidance, region)

def format_message(request_code: int) -> bytes:
    return f'1;{request_code}'.encode(encoding='utf-8')