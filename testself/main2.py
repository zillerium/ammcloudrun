class Book:
    def __init__(self, _title, _author):
        title = _title     # stored on the instance
        author = _author

    def describe():
        print(f"'{title}' by {author}")


# Create two books
book1 = Book("1984", "George Orwell")
book2 = Book("The Hobbit", "J.R.R. Tolkien")

book1.describe()
book2.describe()

