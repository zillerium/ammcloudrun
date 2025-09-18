class Wizard:
    def __init__(self, name):
        self.name = name


class Student(Wizard):
    def __init__ (self, name, person):
        super().__init__(name)
        self.person=person
    
    @property
    def person(self):
        return self._person

    @person.setter
    def person(self, person):
        self._person = person + " setter method"

    def __str__(self):
        return f"{self.name} from {self.person}"

class Professor(Wizard):
    def __init__(self, name, subject):
        super().__init__(name)
        self.subject = subject

def main():
    student = get_student()
    print(student)
    print(f" {student.name} from {student.person} ")

def get_student():
    name = input("name = ")
    person= input("person = ")
    return Student(name, person)

wizard = Wizard("Akbus")
student=Student("Harry", "jo")
professor= Professor("johnson", "professor johnson")

