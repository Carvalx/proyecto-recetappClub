from django.test import TestCase
from django.core.exceptions import ValidationError
from recetas.models import (
    Usuario,
    Categoria,
    Receta,
    Ingrediente,
    Comentario,
    Valoracion,
)

# ─────────────────────────────────────────
# HELPERS — datos reutilizables en todos los tests
# ─────────────────────────────────────────


def crear_usuario(username="testuser", password="pass1234"):
    return Usuario.objects.create_user(username=username, password=password)


def crear_categoria(nombre="Postres"):
    return Categoria.objects.create(nombre=nombre)


def crear_receta(autor, categoria, titulo="Tarta de queso"):
    return Receta.objects.create(
        titulo=titulo,
        descripcion="Una tarta deliciosa",
        instrucciones="Mezclar y hornear",
        autor=autor,
        categoria=categoria,
    )


# ─────────────────────────────────────────
# TESTS DE USUARIO
# ─────────────────────────────────────────


class UsuarioTests(TestCase):

    def test_crear_usuario_correctamente(self):
        """Un usuario se crea con username y contraseña correctamente"""
        usuario = crear_usuario()
        self.assertEqual(usuario.username, "testuser")
        self.assertTrue(usuario.check_password("pass1234"))

    def test_str_usuario_devuelve_username(self):
        """El __str__ del usuario devuelve su username"""
        usuario = crear_usuario()
        self.assertEqual(str(usuario), "testuser")

    def test_campos_opcionales_vacios(self):
        """bio, pais y foto_perfil pueden estar vacíos"""
        usuario = crear_usuario()
        self.assertEqual(usuario.bio, "")
        self.assertFalse(usuario.foto_perfil)


# ─────────────────────────────────────────
# TESTS DE CATEGORIA
# ─────────────────────────────────────────


class CategoriaTests(TestCase):

    def test_crear_categoria(self):
        """Una categoría se crea correctamente con nombre"""
        categoria = crear_categoria("Ensaladas")
        self.assertEqual(categoria.nombre, "Ensaladas")

    def test_str_categoria_devuelve_nombre(self):
        """El __str__ de la categoría devuelve su nombre"""
        categoria = crear_categoria("Sopas")
        self.assertEqual(str(categoria), "Sopas")


# ─────────────────────────────────────────
# TESTS DE RECETA
# ─────────────────────────────────────────


class RecetaTests(TestCase):

    def setUp(self):
        """setUp se ejecuta antes de cada test — prepara los datos base"""
        self.usuario = crear_usuario()
        self.categoria = crear_categoria()

    def test_crear_receta_correctamente(self):
        """Una receta se crea con todos sus campos correctamente"""
        receta = crear_receta(self.usuario, self.categoria)
        self.assertEqual(receta.titulo, "Tarta de queso")
        self.assertEqual(receta.autor, self.usuario)
        self.assertEqual(receta.categoria, self.categoria)

    def test_str_receta_devuelve_titulo(self):
        """El __str__ de la receta devuelve su título"""
        receta = crear_receta(self.usuario, self.categoria)
        self.assertEqual(str(receta), "Tarta de queso")

    def test_receta_sin_categoria(self):
        """Una receta puede existir sin categoría"""
        receta = Receta.objects.create(
            titulo="Sin categoria",
            descripcion="Desc",
            instrucciones="Instrucciones",
            autor=self.usuario,
            categoria=None,
        )
        self.assertIsNone(receta.categoria)

    def test_like_receta(self):
        """Un usuario puede dar like a una receta"""
        receta = crear_receta(self.usuario, self.categoria)
        receta.likes.add(self.usuario)
        self.assertIn(self.usuario, receta.likes.all())

    def test_guardar_receta(self):
        """Un usuario puede guardar una receta"""
        receta = crear_receta(self.usuario, self.categoria)
        receta.guardadas.add(self.usuario)
        self.assertIn(self.usuario, receta.guardadas.all())

    def test_borrar_autor_borra_receta(self):
        """Si se borra el autor, sus recetas se borran en cascada"""
        receta = crear_receta(self.usuario, self.categoria)
        receta_id = receta.id
        self.usuario.delete()
        self.assertFalse(Receta.objects.filter(id=receta_id).exists())


# ─────────────────────────────────────────
# TESTS DE INGREDIENTE
# ─────────────────────────────────────────


class IngredienteTests(TestCase):

    def setUp(self):
        self.usuario = crear_usuario()
        self.categoria = crear_categoria()
        self.receta = crear_receta(self.usuario, self.categoria)

    def test_crear_ingrediente(self):
        """Un ingrediente se asocia correctamente a una receta"""
        ingrediente = Ingrediente.objects.create(
            receta=self.receta, nombre="Harina", cantidad="200g"
        )
        self.assertEqual(ingrediente.nombre, "Harina")
        self.assertEqual(ingrediente.receta, self.receta)

    def test_str_ingrediente(self):
        """El __str__ del ingrediente devuelve cantidad y nombre"""
        ingrediente = Ingrediente.objects.create(
            receta=self.receta, nombre="Azúcar", cantidad="100g"
        )
        self.assertEqual(str(ingrediente), "100g de Azúcar")

    def test_borrar_receta_borra_ingredientes(self):
        """Si se borra la receta, sus ingredientes se borran en cascada"""
        ingrediente = Ingrediente.objects.create(
            receta=self.receta, nombre="Sal", cantidad="1 pizca"
        )
        ingrediente_id = ingrediente.id
        self.receta.delete()
        self.assertFalse(Ingrediente.objects.filter(id=ingrediente_id).exists())


# ─────────────────────────────────────────
# TESTS DE COMENTARIO
# ─────────────────────────────────────────


class ComentarioTests(TestCase):

    def setUp(self):
        self.usuario = crear_usuario()
        self.categoria = crear_categoria()
        self.receta = crear_receta(self.usuario, self.categoria)

    def test_crear_comentario(self):
        """Un comentario se crea correctamente asociado a receta y autor"""
        comentario = Comentario.objects.create(
            receta=self.receta, autor=self.usuario, texto="Muy buena receta"
        )
        self.assertEqual(comentario.texto, "Muy buena receta")
        self.assertEqual(comentario.autor, self.usuario)

    def test_str_comentario(self):
        """El __str__ del comentario devuelve autor y receta"""
        comentario = Comentario.objects.create(
            receta=self.receta, autor=self.usuario, texto="Texto"
        )
        self.assertEqual(str(comentario), f"{self.usuario} - {self.receta}")


# ─────────────────────────────────────────
# TESTS DE VALORACION
# ─────────────────────────────────────────


class ValoracionTests(TestCase):

    def setUp(self):
        self.usuario = crear_usuario()
        self.categoria = crear_categoria()
        self.receta = crear_receta(self.usuario, self.categoria)

    def test_crear_valoracion(self):
        """Una valoración se crea correctamente con puntuación"""
        valoracion = Valoracion.objects.create(
            receta=self.receta, usuario=self.usuario, puntuacion=4.5
        )
        self.assertEqual(float(valoracion.puntuacion), 4.5)

    def test_un_voto_por_usuario(self):
        """Un usuario no puede valorar la misma receta dos veces"""
        Valoracion.objects.create(
            receta=self.receta, usuario=self.usuario, puntuacion=4.0
        )
        with self.assertRaises(Exception):
            Valoracion.objects.create(
                receta=self.receta, usuario=self.usuario, puntuacion=3.0
            )
