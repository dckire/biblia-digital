#!/usr/bin/env python3
"""
Script para importar archivos HTML de la Biblia a MongoDB
"""
import os
import re
import asyncio
from pathlib import Path
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Estructura de libros de la Biblia
BOOKS_STRUCTURE = {
    # Antiguo Testamento
    "genesis": {"name": "Génesis", "testament": "Antiguo", "order": 1, "chapters": 50},
    "exodo": {"name": "Éxodo", "testament": "Antiguo", "order": 2, "chapters": 40},
    "levitico": {"name": "Levítico", "testament": "Antiguo", "order": 3, "chapters": 27},
    "numeros": {"name": "Números", "testament": "Antiguo", "order": 4, "chapters": 36},
    "deuteronomio": {"name": "Deuteronomio", "testament": "Antiguo", "order": 5, "chapters": 34},
    "josue": {"name": "Josué", "testament": "Antiguo", "order": 6, "chapters": 24},
    "jueces": {"name": "Jueces", "testament": "Antiguo", "order": 7, "chapters": 21},
    "rut": {"name": "Rut", "testament": "Antiguo", "order": 8, "chapters": 4},
    "1samuel": {"name": "1 Samuel", "testament": "Antiguo", "order": 9, "chapters": 31},
    "2samuel": {"name": "2 Samuel", "testament": "Antiguo", "order": 10, "chapters": 24},
    "1reyes": {"name": "1 Reyes", "testament": "Antiguo", "order": 11, "chapters": 22},
    "2reyes": {"name": "2 Reyes", "testament": "Antiguo", "order": 12, "chapters": 25},
    "1cronicas": {"name": "1 Crónicas", "testament": "Antiguo", "order": 13, "chapters": 29},
    "2cronicas": {"name": "2 Crónicas", "testament": "Antiguo", "order": 14, "chapters": 29},
    "esdras": {"name": "Esdras", "testament": "Antiguo", "order": 15, "chapters": 10},
    "nehemias": {"name": "Nehemías", "testament": "Antiguo", "order": 16, "chapters": 13},
    "ester": {"name": "Ester", "testament": "Antiguo", "order": 17, "chapters": 10},
    "job": {"name": "Job", "testament": "Antiguo", "order": 18, "chapters": 42},
    "salmos": {"name": "Salmos", "testament": "Antiguo", "order": 19, "chapters": 150},
    "proverbios": {"name": "Proverbios", "testament": "Antiguo", "order": 20, "chapters": 31},
    "eclesiastes": {"name": "Eclesiastés", "testament": "Antiguo", "order": 21, "chapters": 12},
    "cantares": {"name": "Cantares", "testament": "Antiguo", "order": 22, "chapters": 8},
    "isaias": {"name": "Isaías", "testament": "Antiguo", "order": 23, "chapters": 66},
    "jeremias": {"name": "Jeremías", "testament": "Antiguo", "order": 24, "chapters": 52},
    "lamentaciones": {"name": "Lamentaciones", "testament": "Antiguo", "order": 25, "chapters": 5},
    "ezequiel": {"name": "Ezequiel", "testament": "Antiguo", "order": 26, "chapters": 48},
    "daniel": {"name": "Daniel", "testament": "Antiguo", "order": 27, "chapters": 12},
    "oseas": {"name": "Oseas", "testament": "Antiguo", "order": 28, "chapters": 14},
    "joel": {"name": "Joel", "testament": "Antiguo", "order": 29, "chapters": 3},
    "amos": {"name": "Amós", "testament": "Antiguo", "order": 30, "chapters": 9},
    "abdias": {"name": "Abdías", "testament": "Antiguo", "order": 31, "chapters": 1},
    "jonas": {"name": "Jonás", "testament": "Antiguo", "order": 32, "chapters": 4},
    "miqueas": {"name": "Miqueas", "testament": "Antiguo", "order": 33, "chapters": 7},
    "nahum": {"name": "Nahúm", "testament": "Antiguo", "order": 34, "chapters": 3},
    "habacuc": {"name": "Habacuc", "testament": "Antiguo", "order": 35, "chapters": 3},
    "sofonias": {"name": "Sofonías", "testament": "Antiguo", "order": 36, "chapters": 3},
    "hageo": {"name": "Hageo", "testament": "Antiguo", "order": 37, "chapters": 2},
    "zacarias": {"name": "Zacarías", "testament": "Antiguo", "order": 38, "chapters": 14},
    "malaquias": {"name": "Malaquías", "testament": "Antiguo", "order": 39, "chapters": 4},
    
    # Nuevo Testamento
    "mateo": {"name": "Mateo", "testament": "Nuevo", "order": 40, "chapters": 28},
    "marcos": {"name": "Marcos", "testament": "Nuevo", "order": 41, "chapters": 16},
    "lucas": {"name": "Lucas", "testament": "Nuevo", "order": 42, "chapters": 24},
    "juan": {"name": "Juan", "testament": "Nuevo", "order": 43, "chapters": 21},
    "hechos": {"name": "Hechos", "testament": "Nuevo", "order": 44, "chapters": 28},
    "romanos": {"name": "Romanos", "testament": "Nuevo", "order": 45, "chapters": 16},
    "1corintios": {"name": "1 Corintios", "testament": "Nuevo", "order": 46, "chapters": 16},
    "2corintios": {"name": "2 Corintios", "testament": "Nuevo", "order": 47, "chapters": 13},
    "galatas": {"name": "Gálatas", "testament": "Nuevo", "order": 48, "chapters": 6},
    "efesios": {"name": "Efesios", "testament": "Nuevo", "order": 49, "chapters": 6},
    "filipenses": {"name": "Filipenses", "testament": "Nuevo", "order": 50, "chapters": 4},
    "colosenses": {"name": "Colosenses", "testament": "Nuevo", "order": 51, "chapters": 4},
    "1tesalonicenses": {"name": "1 Tesalonicenses", "testament": "Nuevo", "order": 52, "chapters": 5},
    "2tesalonicenses": {"name": "2 Tesalonicenses", "testament": "Nuevo", "order": 53, "chapters": 3},
    "1timoteo": {"name": "1 Timoteo", "testament": "Nuevo", "order": 54, "chapters": 6},
    "2timoteo": {"name": "2 Timoteo", "testament": "Nuevo", "order": 55, "chapters": 4},
    "tito": {"name": "Tito", "testament": "Nuevo", "order": 56, "chapters": 3},
    "filemon": {"name": "Filemón", "testament": "Nuevo", "order": 57, "chapters": 1},
    "hebreos": {"name": "Hebreos", "testament": "Nuevo", "order": 58, "chapters": 13},
    "santiago": {"name": "Santiago", "testament": "Nuevo", "order": 59, "chapters": 5},
    "1pedro": {"name": "1 Pedro", "testament": "Nuevo", "order": 60, "chapters": 5},
    "2pedro": {"name": "2 Pedro", "testament": "Nuevo", "order": 61, "chapters": 3},
    "1juan": {"name": "1 Juan", "testament": "Nuevo", "order": 62, "chapters": 5},
    "2juan": {"name": "2 Juan", "testament": "Nuevo", "order": 63, "chapters": 1},
    "3juan": {"name": "3 Juan", "testament": "Nuevo", "order": 64, "chapters": 1},
    "judas": {"name": "Judas", "testament": "Nuevo", "order": 65, "chapters": 1},
    "apocalipsis": {"name": "Apocalipsis", "testament": "Nuevo", "order": 66, "chapters": 22},
}

def parse_html_file(file_path):
    """Parsea un archivo HTML y extrae los versículos"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        verses = []
        
        # Buscar todos los párrafos en texto-columna o contenido similar
        content_div = soup.find('div', class_='texto-columna')
        if not content_div:
            # Buscar en el main o container
            content_div = soup.find('main') or soup.find('div', class_='container')
        
        if content_div:
            paragraphs = content_div.find_all('p')
            
            for p in paragraphs:
                text = p.get_text().strip()
                if not text:
                    continue
                
                # Intentar extraer número de versículo al inicio
                match = re.match(r'^(\d+)\s+(.+)$', text)
                if match:
                    verse_number = int(match.group(1))
                    verse_text = match.group(2).strip()
                    verses.append({
                        'number': verse_number,
                        'text': verse_text
                    })
                else:
                    # Si no tiene número, podría ser el versículo 1 o continuación
                    if not verses:
                        verses.append({
                            'number': 1,
                            'text': text
                        })
        
        return verses
    except Exception as e:
        logger.error(f"Error parseando {file_path}: {e}")
        return []

async def import_bible_data(source_dir, mongo_url, db_name):
    """Importa todos los datos de la Biblia a MongoDB"""
    
    # Conectar a MongoDB
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        # Limpiar colecciones existentes
        logger.info("Limpiando colecciones existentes...")
        await db.books.delete_many({})
        await db.chapters.delete_many({})
        await db.verses.delete_many({})
        
        # Crear índices
        await db.books.create_index("slug")
        await db.chapters.create_index([("book_id", 1), ("number", 1)])
        await db.verses.create_index([("chapter_id", 1), ("number", 1)])
        await db.verses.create_index([("text", "text")])  # Índice de texto para búsqueda
        
        total_books = 0
        total_chapters = 0
        total_verses = 0
        
        # Procesar cada libro
        for book_slug, book_info in BOOKS_STRUCTURE.items():
            logger.info(f"Procesando {book_info['name']}...")
            
            # Insertar libro
            book_doc = {
                "id": book_slug,
                "slug": book_slug,
                "name": book_info['name'],
                "testament": book_info['testament'],
                "order": book_info['order'],
                "total_chapters": book_info['chapters']
            }
            await db.books.insert_one(book_doc)
            total_books += 1
            
            # Procesar capítulos del libro
            for chapter_num in range(1, book_info['chapters'] + 1):
                chapter_file = Path(source_dir) / f"{book_slug}{chapter_num}.html"
                
                if not chapter_file.exists():
                    logger.warning(f"Archivo no encontrado: {chapter_file}")
                    continue
                
                # Parsear versículos
                verses = parse_html_file(chapter_file)
                
                if not verses:
                    logger.warning(f"No se encontraron versículos en {chapter_file}")
                    continue
                
                # Insertar capítulo
                chapter_id = f"{book_slug}_{chapter_num}"
                chapter_doc = {
                    "id": chapter_id,
                    "book_id": book_slug,
                    "number": chapter_num,
                    "title": f"{book_info['name']} {chapter_num}",
                    "total_verses": len(verses)
                }
                await db.chapters.insert_one(chapter_doc)
                total_chapters += 1
                
                # Insertar versículos
                verse_docs = []
                for verse in verses:
                    verse_doc = {
                        "id": f"{chapter_id}_{verse['number']}",
                        "chapter_id": chapter_id,
                        "book_id": book_slug,
                        "book_name": book_info['name'],
                        "chapter_number": chapter_num,
                        "number": verse['number'],
                        "text": verse['text'],
                        "reference": f"{book_info['name']} {chapter_num}:{verse['number']}"
                    }
                    verse_docs.append(verse_doc)
                
                if verse_docs:
                    await db.verses.insert_many(verse_docs)
                    total_verses += len(verse_docs)
                
                logger.info(f"  Capítulo {chapter_num}: {len(verses)} versículos")
        
        logger.info("=" * 60)
        logger.info(f"IMPORTACIÓN COMPLETADA:")
        logger.info(f"  📚 Libros: {total_books}")
        logger.info(f"  📖 Capítulos: {total_chapters}")
        logger.info(f"  📝 Versículos: {total_verses}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error durante la importación: {e}")
        raise
    finally:
        client.close()

async def main():
    """Función principal"""
    source_dir = "bible-source"
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME', 'bible_db')
    
    if not mongo_url:
        logger.error("MONGO_URL no está configurado en .env")
        return
    
    logger.info("Iniciando importación de la Biblia...")
    logger.info(f"Directorio fuente: {source_dir}")
    logger.info(f"Base de datos: {db_name}")
    
    await import_bible_data(source_dir, mongo_url, db_name)

if __name__ == "__main__":
    asyncio.run(main())
