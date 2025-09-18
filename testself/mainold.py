class Student:
    def __init__ (self, name, person):
        if not name:
            raise ValueError ("no name")
        if person not in ["Joe", "Jo"]:
            raise ValueError ("no valid person")
        self.name=name
        self.person=person
    
    @property
    def person(self):
        return self._person

    @person.setter
    def person(self, person):
        self._person = person + " setter method"

    def __str__(self):
        return f"{self.name} from {self.person}"

def main():
    student = get_student()
    print(student)
    print(f" {student.name} from {student.person} ")

def get_student():
    name = input("name = ")
    person= input("person = ")
    return Student(name, person)


if __name__ == "__main__":
    main()
