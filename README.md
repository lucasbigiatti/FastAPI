# 📌 FastAPI Todo App

Este es un proyecto de una API RESTful desarrollada con **FastAPI**, que permite gestionar una lista de tareas (TODOs). La aplicación utiliza SQLite como base de datos local y está organizada en módulos.

---

## 🚀 Tecnologías utilizadas

- Python 3.11.9
- FastAPI
- SQLite
- SQLAlchemy
- Uvicorn

---

## 📂 Estructura del proyecto

FastAPI/
│
├── TodoApp/ # Módulo principal de la aplicación
│ ├── main.py # Archivo de inicio con la instancia de FastAPI
│ ├── models.py # Modelos de la base de datos
│ ├── routers.py # Rutas/endpoints de la API
│ └── database.py # Conexión y gestión de la base de datos
│
├── todosapp.db # Base de datos SQLite
├── requirements.txt # Dependencias del proyecto
└── README.md
