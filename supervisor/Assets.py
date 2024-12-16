# this module contains all the functions
# that help to improve the supervisor functionalities

from datetime import datetime
import RPP


def datetime_formated() -> str:
    return datetime.now().strftime('%d-%m-%Y %H:%M:%S')

def slice_str(data: str, slice_size: int) -> list[bytes]:
    slices = []
    i = 1
    slice = data[0: slice_size]
    while slice != '':
        slices.append(slice.encode())
        start = slice_size * i
        end = slice_size * (i + 1)
        slice = data[start: end]
        i += 1
    return slices

'''
put all elements of an list, recursively
separated by white spaces
'''
def list_content_to_str(data: list) -> str:
    str_data = ''
    for element in data:
        for item in element:
            str_data += f'{item} '
    return str_data[:-1]


def num_to_str(num: int) -> str:
    return str(num)


if __name__ == '__main__':
    data1 = [ (510, 610), (710, 810), (910, 1010) ]
    data2 = [(130, 90), (130, 80), (130, 70), (130, 60), (130, 50), (130, 40), (140, 40), (150, 40), (160, 40), (160, 30), (160, 20)]
    print(RPP.pack_coordinates(data2, 57))