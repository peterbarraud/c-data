import inspect

class Logger:
    def __init__(self, logger_name : str = None):
        if not logger_name:
            logger_name = f'{inspect.stack()[1][3]}.log'
        self.__log = open(f'testing.data/{logger_name}', 'w')
        # pass

    def Writeln(self, ln):
        self.__log.write(f'{ln}\n')

    def close(self):
        self.__log.close()