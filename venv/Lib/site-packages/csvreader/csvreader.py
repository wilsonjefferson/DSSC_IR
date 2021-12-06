from typing import Any, List
from _io import TextIOWrapper
class ParameterError(BaseException):
    pass

def ReadCSV(filename: str, return_type: str = 'str'):
    """

    :param filename: str
    :param return_type: str
    :return: Any[str, List[str], TextIOWrapper]

    This function reads a csv file.
    If return_type is str:
    it reads all the lines and returns them as a string.
    If return_type is list:
    it returns all the lines of the file as list.
    If return_type is obj:
    it returns the file object.
    """
    obj = open(filename, 'r')
    if return_type not in ['str','list','obj']:
        raise ParameterError('Please give return_type parameter as str, list or obj. Printing Docstring... please go through it.\n\n'+ReadCSV.__doc__)

    if return_type == 'obj':
        return obj
    elif return_type == 'str':
        x = obj.read()
        obj.close()
        return x
    elif return_type == 'list':
        x = obj.read().split('\n')
        for i in x:
            x[x.index(i)] = i.split(',')

        for i in x:
            for j in i:
                i[i.index(j)] = j.replace(' ','')
        obj.close()
        return x

def WriteCSV(filename: str, content, mode = 'w'):
    """

    :param filename: str
    :param content
    :param mode: str
    :return: int

    This function writes to a csv file.

    The content should be a string or a List with Lists inside it.
    If the content is a list,
    it writes the list to the file line by line.
    If the content is a str,
    it directly writes to a file.
    If the mode is w,
    it overwrites the text.
    If the mode is a,
    it appends the text.
    """
    if mode not in ['w', 'a']:
        raise ParameterError('Wrong Mode!')
    obj = open(filename, mode)
    try:
        if content.__class__.__name__ == 'str':
            obj.write(content)
        else:
            for i in content:
                for j in i:
                    if j == i[-1]:
                        obj.write(j)
                    else:
                        obj.write(j + ',')
                obj.write('\n')
    except Exception as e:
        obj.close()
        return 1
    obj.close()
    return 0

if __name__ == '__main__':
    print(ReadCSV('../alarms.csv', 'str'), ReadCSV('../alarms.csv', 'list'), ReadCSV('../alarms.csv', 'obj'))
    WriteCSV('../alarms.csv', '13, 30, SecondAlarm, pandas\n14, 30, ThirdAlarm, scipy\n', mode ='a')
    print(ReadCSV('../alarms.csv', 'str'), ReadCSV('../alarms.csv', 'list'), ReadCSV('../alarms.csv', 'obj'))

