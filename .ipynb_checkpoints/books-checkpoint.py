from fastapi import Body, FastAPI
app = FastAPI()

BOOKS = [
    {"title":"Title one", "author": "Author one", "category":"Maths"},
    {"title":"Title two", "author": "Author two", "category":"Science"},
    {"title":"Title three", "author": "Author three", "category":"Physics"},
    {"title":"Title four", "author": "Author one", "category":"Science"}
]


@app.get("/books")
async def read_all_books():
    return BOOKS

@app.get("/books/{book_title}")                           # Path parameters
async def read_book(book_title: str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():      #casefold makes everything lowercase
            return book
        
@app.get("/books/")                             # Query  parameter
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return

@app.get("/books/{book_author}/")                                     # Read by path and query parameters
async def read_author_category_by_query(book_author: str, category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == book_author.casefold() and book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return

@app.post("/books/create_book")        # Post HTTP Request - Used to create a new data 
async def create_book(new_book=Body()):
    BOOKS.append(new_book)
    

@app.put("/books/update_book")        # Put HTTP Request - Used to update previous data 
async def update_book(updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == updated_book.get('title').casefold():
            BOOKS[i] = updated_book

@app.delete("/books/delete_book/{book_title}")        # Delete HTTP Request - Used to delete previous data 
async def delete_book(book_title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == book_title.casefold():
            BOOKS.pop(i)
            break
            
