class MyClass:
    def __init__(self):
        self._my_variable = 0

    @property
    def my_variable(self):
        print(111)
        return self._my_variable

    @my_variable.setter
    def my_variable(self, value):
        print(222)
        self._my_variable = value

a = MyClass()
a.my_variable = 5