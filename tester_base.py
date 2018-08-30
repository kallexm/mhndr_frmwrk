class TesterBase(object):
    def __init__(self):
        pass

    def prepare(self):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError
