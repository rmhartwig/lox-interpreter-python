# Custom exception used to unwind the call stack when a return statement is executed.
# Allows returning values from functions.
class ReturnException(Exception):
    def __init__(self, value):
        super().__init__()
        self.value = value