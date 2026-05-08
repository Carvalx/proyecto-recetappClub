# RecetApp Club · Backend (Django + DRF)

![CI](https://github.com/Carvalx/proyecto-recetappClub/actions/workflows/ci.yml/badge.svg?branch=v2-dev)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.2_LTS-green)
![DRF](https://img.shields.io/badge/DRF-3.17-red)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)

Plataforma social de recetas con backend Django y cliente Android nativo. Los usuarios crean recetas, valoran las de otros, guardan favoritas, comentan e interactúan con likes.

**Aplicación en producción:** carvalx.pythonanywhere.com  
**Cliente Android:** github.com/Carvalx/recetappclub-android

---

## Vista previa

| Login | Registro |
|---|---|
| ![Login](docs/login.png) | ![Registro](docs/registro.png) |

| Explorar recetas | Perfil de usuario |
|---|---|
| ![Explorar](docs/explorar.png) | ![Perfil](docs/perfil.png) |

---

## Arquitectura

```
[ Web (Django Templates) ]──┐
                            ├──► [ Backend Django ]──► PostgreSQL
[ App Android (Kotlin) ]────┘     ├─ Vistas web (sesión)
                                  └─ API REST (DRF + Token Auth)
```

El backend expone simultáneamente dos interfaces sobre los mismos modelos:

- **Frontend web** servido con Django Templates, autenticación por sesión y formularios.
- **API REST** con Django REST Framework y autenticación por Token, consumida por el cliente Android.

---

## Stack técnico

**Backend**
- Python 3.12 · Django 5.2 LTS
- Django REST Framework 3.17
- PostgreSQL (psycopg2)
- Pillow para procesamiento de imágenes
- python-decouple para configuración por entorno
- django-countries

**Frontend web**
- Django Templates · HTML5 · CSS3 · JavaScript

**Cliente móvil (repo aparte)**
- Kotlin · Android SDK
- Retrofit + OkHttp para consumo de la API REST
- Corrutinas para llamadas asíncronas
- Glide para carga de imágenes

**DevOps**
- Docker + Docker Compose
- GitHub Actions (CI — tests automáticos en cada push)

**Despliegue**
- PythonAnywhere

---

## Modelo de datos

Seis modelos relacionados con relaciones uno-a-muchos y muchos-a-muchos:

| Modelo | Descripción | Relaciones |
|---|---|---|
| Usuario | Extiende AbstractUser con foto de perfil, país y bio | — |
| Categoria | Tipos de receta | — |
| Receta | Entidad principal con título, descripción, instrucciones e imagen | FK a Usuario y Categoria, M2M likes y guardadas |
| Ingrediente | Ingredientes de una receta | FK a Receta |
| Comentario | Comentarios de usuarios | FK a Receta y Usuario |
| Valoracion | Puntuación numérica única por usuario por receta | FK a Receta y Usuario, unique_together |

---

## Endpoints principales de la API

| Método | Endpoint | Descripción |
|---|---|---|
| POST | /api/registro/ | Registro de usuario, devuelve token |
| POST | /api/login/ | Login, devuelve token |
| GET | /api/perfil/ | Datos del usuario autenticado |
| PATCH | /api/perfil/foto/ | Subida de foto de perfil (multipart) |
| GET, POST | /api/recetas/ | Listar (con búsqueda y filtro) y crear |
| GET, PUT, DELETE | /api/recetas/<id>/ | Detalle, editar, eliminar (solo autor) |
| POST | /api/recetas/<id>/like/ | Toggle de like |
| POST | /api/recetas/<id>/valorar/ | Valorar receta (voto único por usuario) |
| POST | /api/recetas/<id>/guardar/ | Toggle de guardado en favoritos |
| POST | /api/recetas/<id>/comentar/ | Añadir comentario |
| POST | /api/recetas/<id>/ingredientes/ | Añadir ingrediente |
| GET | /api/categorias/ | Listar categorías |
| GET | /api/mis-recetas/ | Mis creaciones y mis favoritas |

Autenticación: los endpoints protegidos requieren la cabecera `Authorization: Token <token>`.

---

## Funcionalidades implementadas

- Autenticación por Token (DRF authtoken) y por sesión Django
- CRUD completo de recetas con permisos basados en autoría
- Búsqueda por texto en título y descripción, filtrado por categoría
- Sistema de likes con toggle atómico
- Sistema de guardado en favoritos (M2M)
- Comentarios sobre recetas
- Valoraciones con restricción de unicidad (unique_together)
- Subida de imágenes para recetas y perfiles (multipart)
- Vistas genéricas de DRF (ListCreateAPIView, RetrieveUpdateDestroyAPIView)
- Permisos diferenciados por método (IsAuthenticatedOrReadOnly)
- **38 tests** unitarios y de API con cobertura de modelos, endpoints y permisos
- **Pipeline CI/CD** con GitHub Actions — tests automáticos en cada push
- Entorno dockerizado con Docker Compose (Django + PostgreSQL)

---

## Tests y CI

El proyecto incluye 38 tests que cubren:

- Modelos: creación, validaciones, relaciones y cascadas
- API: autenticación, permisos, endpoints y casos límite
- Seguridad: acceso no autorizado, eliminación de recursos ajenos

```bash
# Ejecutar tests localmente con Docker
docker compose exec web python manage.py test recetas --verbosity=2
```

El pipeline de GitHub Actions ejecuta todos los tests automáticamente en cada push a `v2-dev` y `main`.

---

## Instalación local con Docker (recomendado)

```bash
# 1. Clonar el repo
git clone https://github.com/Carvalx/proyecto-recetappClub.git
cd proyecto-recetappClub

# 2. Variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 3. Levantar con Docker
docker compose up --build

# 4. Migraciones (en otra terminal)
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## Instalación local sin Docker

```bash
# 1. Clonar el repo
git clone https://github.com/Carvalx/proyecto-recetappClub.git
cd proyecto-recetappClub

# 2. Entorno virtual
python -m venv venv
source venv/bin/activate          # Linux/Mac
venv\Scripts\activate             # Windows

# 3. Dependencias
pip install -r requirements.txt

# 4. Variables de entorno
cp .env.example .env
# Editar .env con tus valores reales

# 5. Base de datos
python manage.py migrate
python manage.py createsuperuser

# 6. Servidor de desarrollo
python manage.py runserver
```

Ver `.env.example` para las variables de entorno necesarias.

---

## Estructura del proyecto

```
recetapp_club/
├── .github/
│   └── workflows/
│       └── ci.yml            # Pipeline CI/CD
├── recetapp_club/            # Configuración del proyecto Django
│   ├── settings.py
│   └── urls.py
├── recetas/                  # App principal
│   ├── models.py             # 6 modelos relacionales
│   ├── views.py              # Vistas web
│   ├── api_views.py          # Endpoints REST
│   ├── serializers.py        # Serializers de DRF
│   ├── forms.py              # Formularios web
│   ├── tests.py              # 38 tests unitarios y de API
│   └── urls.py               # Rutas (web + API)
├── templates/                # Plantillas HTML
├── static/                   # Recursos estáticos
├── docs/                     # Capturas de pantalla
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Sobre el proyecto

Proyecto desarrollado de forma autónoma como práctica integral de desarrollo backend con Django y consumo desde cliente móvil Android. Cubre el ciclo completo: modelado de datos relacional, autenticación por token, diseño de API REST, manejo de archivos multipart, lógica de negocio, tests automatizados, pipeline CI/CD, entorno dockerizado y despliegue en producción.

**Autor:** Carlos Macero · [LinkedIn](https://linkedin.com/in/tu-perfil) · [GitHub](https://github.com/Carvalx)