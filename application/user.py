class User:

    def __init__(self, first, last, code):
        self.first = first
        self.last = last
        self.code = code

        def __repr__(self):
            return "User('{}','{}','{}')".format(self.first, self.last, self.code)