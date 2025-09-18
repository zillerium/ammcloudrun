class Demo:
    def __init__(self, value):
        self.value = value
        self.result = self.compute_result()  # 👈 calls another method

    def compute_result(self):
        print("Inside compute_result, self =", self)
        return self.double_value()

    def double_value(self):
        print("Inside double_value, self =", self)
        return self.value * 2


# Create an object
d = Demo(10)
print("Final object:", d)

