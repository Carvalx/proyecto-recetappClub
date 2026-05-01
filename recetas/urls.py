from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # WEB
    path("", views.inicio, name="inicio"),
    path("explorar/", views.explorar, name="explorar"),
    path("novedades/", views.novedades, name="novedades"),
    path("recetas/", views.lista_recetas, name="lista_recetas"),
    path("recetas/nueva/", views.crear_receta, name="crear_receta"),
    path("recetas/<int:pk>/", views.detalle_receta, name="detalle_receta"),
    path("recetas/<int:pk>/editar/", views.editar_receta, name="editar_receta"),
    path("recetas/<int:pk>/eliminar/", views.eliminar_receta, name="eliminar_receta"),
    path("mis-recetas/", views.mis_recetas, name="mis_recetas"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("registro/", views.registro, name="registro"),
    path("perfil/", views.perfil, name="perfil"),
    path("perfil/editar/", views.editar_perfil, name="editar_perfil"),
    path("perfil/cambiar-password/", views.cambiar_password, name="cambiar_password"),
    path("politica-privacidad/", views.politica_privacidad, name="politica_privacidad"),
    path("terminos-uso/", views.terminos_uso, name="terminos_uso"),
    path("politica-cookies/", views.politica_cookies, name="politica_cookies"),
    # API
    path("api/registro/", api_views.api_registro, name="api_registro"),
    path("api/login/", api_views.api_login, name="api_login"),
    path("api/perfil/", api_views.api_perfil, name="api_perfil"),
    path(
        "api/perfil/foto/", api_views.api_actualizar_foto_perfil, name="api_foto_perfil"
    ),
    path("api/recetas/", api_views.RecetaListCreate.as_view(), name="api_recetas"),
    path(
        "api/recetas/<int:pk>/",
        api_views.RecetaDetail.as_view(),
        name="api_receta_detail",
    ),
    path(
        "api/recetas/<int:pk>/ingredientes/",
        api_views.api_añadir_ingrediente,
        name="api_ingrediente",
    ),
    path("api/recetas/<int:pk>/comentar/", api_views.api_comentar, name="api_comentar"),
    path("api/recetas/<int:pk>/like/", api_views.api_like, name="api_like"),
    path("api/recetas/<int:pk>/valorar/", api_views.api_valorar, name="api_valorar"),
    path("api/recetas/<int:pk>/guardar/", api_views.api_guardar, name="api_guardar"),
    path("api/categorias/", api_views.CategoriaList.as_view(), name="api_categorias"),
    path("api/mis-recetas/", api_views.api_mis_recetas, name="api_mis_recetas"),
]
