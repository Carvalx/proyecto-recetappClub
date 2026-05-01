from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import Usuario, Receta, Ingrediente, Comentario, Categoria, Valoracion


class UsuarioChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].max_length = 25
        self.fields["username"].widget.attrs["maxlength"] = 25


class UsuarioCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].max_length = 25
        self.fields["username"].widget.attrs["maxlength"] = 25


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    form = UsuarioChangeForm
    add_form = UsuarioCreationForm
    list_display = ["username", "email", "pais", "date_joined"]
    fieldsets = UserAdmin.fieldsets + (
        ("Perfil", {"fields": ("foto_perfil", "pais", "bio")}),
    )


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ["titulo", "autor", "categoria", "fecha_creacion"]
    list_filter = ["categoria", "fecha_creacion"]
    search_fields = ["titulo", "autor__username"]


@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ["nombre", "cantidad", "receta"]


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ["autor", "receta", "fecha"]


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nombre"]


@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    list_display = ["usuario", "receta", "puntuacion"]
