from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Biblia API",
    description="API completa para la Biblia con interfaz web",
    version="1.0.0"
)

# Conectar a MongoDB
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'bible_db')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

@app.get("/books")
async def get_books():
    books = await db.books.find().sort("order", 1).to_list(length=100)
    for book in books:
        book["_id"] = str(book["_id"])
    return books

@app.get("/books/{book_id}")
async def get_book(book_id: str):
    book = await db.books.find_one({"id": book_id})
    if not book:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    book["_id"] = str(book["_id"])
    return book

@app.get("/books/{book_id}/chapters")
async def get_book_chapters(book_id: str):
    chapters = await db.chapters.find(
        {"book_id": book_id}
    ).sort("number", 1).to_list(length=200)
    
    for chapter in chapters:
        chapter["_id"] = str(chapter["_id"])
    return chapters

@app.get("/books/{book_id}/chapters/{chapter_number}/verses")
async def get_chapter_verses(book_id: str, chapter_number: int):
    verses = await db.verses.find({
        "book_id": book_id,
        "chapter_number": chapter_number
    }).sort("number", 1).to_list(length=200)
    
    for verse in verses:
        verse["_id"] = str(verse["_id"])
    return verses

@app.get("/search")
async def search_verses(q: str):
    # Búsqueda de texto completo en MongoDB
    verses = await db.verses.find({
        "$text": {"$search": q}
    }).to_list(length=50)
    
    for verse in verses:
        verse["_id"] = str(verse["_id"])
    return verses

@app.get("/books/{book_id}/chapters/{chapter_number}/verses/{verse_number}")
async def get_specific_verse(book_id: str, chapter_number: int, verse_number: int):
    verse = await db.verses.find_one({
        "book_id": book_id,
        "chapter_number": chapter_number,
        "number": verse_number
    })
    
    if not verse:
        raise HTTPException(status_code=404, detail="Versículo no encontrado")
    
    verse["_id"] = str(verse["_id"])
    return verse

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
