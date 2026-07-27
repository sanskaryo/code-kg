class Helper:
    def __init__(self):
        self.value = 1

    def do_work(self, x):
        if x > 0:
            return x + self.value
        return self.value
