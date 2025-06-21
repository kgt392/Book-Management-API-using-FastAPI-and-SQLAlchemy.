# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from database import engine, SessionLocal
from pydantic import BaseModel

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schemas
class BookCreate(BaseModel):
    title: str
    author: str
    pages: int


# Routes
@app.post("/books/")
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    # db_book = models.Book(title=book.title,author=book.author,pages=book.pages)
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/books/")
def get_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()

@app.get("/books/{book_id}")
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return {"message": "Book deleted"}

@app.put("/books/{book_id}")
def update_book(updates_book: BookCreate,book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not updates_book:
        raise HTTPException(status_code=404, detail="Book not found")
    # book.update(updates_book.dict())
    book.title = updates_book.title
    book.author = updates_book.author
    book.pages = updates_book.pages 

    db.commit()
    db.refresh(book)
    return {"data":book}

