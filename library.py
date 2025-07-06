from flask import Flask, request

app = Flask(__name__)

books = [
    {
        "title": "Harry Potter 1",
        "author": "J.K.Rowling",
        "year": 2001,
        "main_characters": [
            "Harry",
            "Ron",
            "Hermiona"
        ]
     }
]

@app.get("/library")
def get_all_books():
    return {"books": books}

@app.post("/library")
def new_book_to_library():
    new_book_json = request.get_json()
    for book in books:
        if new_book_json["title"] == book["title"]:
            return "Book title already exists", 403
    new_book = {
        "title": new_book_json["title"],
        "author": new_book_json["author"],
        "year": new_book_json["year"],
        "main_characters": new_book_json["main_characters"]
    }
    books.append(new_book)
    return new_book, 201

@app.get("/library/<string:title>")
def get_book_details(title):
    for book in books:
        if book["title"] == title:
            return book, 200
    return {'message': f"No book with {title}"}, 404