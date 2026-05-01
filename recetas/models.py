from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
from django.conf import settings


class Usuario(AbstractUser):
    foto_perfil = models.ImageField(upload_to="perfiles/", blank=True, null=True)
    pais = CountryField(blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.username


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Receta(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    instrucciones = models.TextField()
    imagen = models.ImageField(upload_to="recetas/", blank=True, null=True)
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="recetas")
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(Usuario, related_name="recetas_liked", blank=True)
    guardadas = models.ManyToManyField(
        Usuario, related_name="recetas_guardadas", blank=True
    )

    def __str__(self):
        return self.titulo


class Ingrediente(models.Model):
    receta = models.ForeignKey(
        Receta, on_delete=models.CASCADE, related_name="ingredientes"
    )
    nombre = models.CharField(max_length=200)
    cantidad = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.cantidad} de {self.nombre}"


class Comentario(models.Model):
    receta = models.ForeignKey(
        Receta, on_delete=models.CASCADE, related_name="comentarios"
    )
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.autor} - {self.receta}"


class Valoracion(models.Model):
    receta = models.ForeignKey(
        Receta, on_delete=models.CASCADE, related_name="valoraciones"
    )
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    puntuacion = models.DecimalField(max_digits=2, decimal_places=1)

    class Meta:
        unique_together = ["receta", "usuario"]  # un voto por usuario

    def __str__(self):
        return f"{self.usuario} - {self.receta} - {self.puntuacion}"
