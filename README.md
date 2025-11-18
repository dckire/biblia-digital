# 📖 Biblia Digital

Una aplicación web moderna para leer y buscar en la Biblia, construida con FastAPI y MongoDB.

![Biblia Digital](https://img.shields.io/badge/FastAPI-0.104.1-009688?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python)
![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-47A248?logo=mongodb)

## 🚀 Características

- 📚 **66 libros** de la Biblia completos
- 🔍 **Búsqueda en tiempo real** en todos los versículos
- 📱 **Interfaz responsive** para móviles y desktop
- ⚡ **API REST** completa con FastAPI
- 🗄️ **Base de datos** MongoDB optimizada

## 🛠️ Stack Tecnológico

- **Backend:** FastAPI, Python 3.8+
- **Base de datos:** MongoDB con Motor
- **Frontend:** HTML5, CSS3, JavaScript vanilla
- **Scraping:** BeautifulSoup4

## 🎯 Demo

![Interfaz de la Biblia Digital](https://via.placeholder.com/800x400/667eea/ffffff?text=Biblia+Digital+Interface)

## 📦 Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/biblia-digital.git
cd biblia-digital/backend

# Instalar dependencias
pip install -r requirements.txt

# Configurar entorno
cp .env.example .env

# Importar datos
python import_bible.py

# Ejecutar
uvicorn main:app --reload
