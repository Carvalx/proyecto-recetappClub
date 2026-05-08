from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate
from django.db.models import Q
from .models import Receta, Categoria, Comentario, Valoracion, Ingrediente
from .serializers import (
    RecetaSerializer,
    RecetaListSerializer,
    CategoriaSerializer,
    ComentarioSerializer,
    ValoracionSerializer,
    RegistroSerializer,
    UsuarioSerializer,
)


# AUTH
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def api_registro(request):
    serializer = RegistroSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "username": user.username})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def api_login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "username": user.username, "user_id": user.id}
        )
    return Response(
        {"error": "Credenciales incorrectas"}, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def api_perfil(request):
    serializer = UsuarioSerializer(request.user)
    return Response(serializer.data)


# RECETAS
class RecetaListCreate(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "POST":
            return RecetaSerializer
        return RecetaListSerializer

    def get_queryset(self):
        queryset = Receta.objects.all().order_by("-fecha_creacion")
        query = self.request.query_params.get("q")
        categoria = self.request.query_params.get("categoria")
        if query:
            queryset = queryset.filter(
                Q(titulo__icontains=query) | Q(descripcion__icontains=query)
            )
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)
        return queryset

    def perform_create(self, serializer):
        serializer.save(autor=self.request.user)


from rest_framework.exceptions import PermissionDenied


class RecetaDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Receta.objects.all()
    serializer_class = RecetaSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def perform_destroy(self, instance):
        if instance.autor != self.request.user:
            raise PermissionDenied("No puedes eliminar una receta que no es tuya")
        instance.delete()

    def perform_update(self, serializer):
        if serializer.instance.autor != self.request.user:
            raise PermissionDenied("No puedes editar una receta que no es tuya")
        serializer.save()


# INGREDIENTES
@api_view(["POST"])
def api_añadir_ingrediente(request, pk):
    receta = Receta.objects.get(pk=pk)
    if receta.autor != request.user:
        return Response({"error": "No autorizado"}, status=403)
    from .serializers import IngredienteSerializer

    serializer = IngredienteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(receta=receta)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


# COMENTARIOS
@api_view(["POST"])
def api_comentar(request, pk):
    receta = Receta.objects.get(pk=pk)
    serializer = ComentarioSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(receta=receta, autor=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


# LIKES
@api_view(["POST"])
def api_like(request, pk):
    receta = Receta.objects.get(pk=pk)
    if request.user in receta.likes.all():
        receta.likes.remove(request.user)
        return Response({"liked": False, "likes_count": receta.likes.count()})
    else:
        receta.likes.add(request.user)
        return Response({"liked": True, "likes_count": receta.likes.count()})


# VALORACIÓN
@api_view(["POST"])
def api_valorar(request, pk):
    receta = Receta.objects.get(pk=pk)
    puntuacion = request.data.get("puntuacion")
    Valoracion.objects.update_or_create(
        receta=receta, usuario=request.user, defaults={"puntuacion": puntuacion}
    )
    return Response({"ok": True})


# CATEGORÍAS
class CategoriaList(generics.ListAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.AllowAny]


@api_view(["POST"])
def api_guardar(request, pk):
    receta = Receta.objects.get(pk=pk)
    if request.user in receta.guardadas.all():
        receta.guardadas.remove(request.user)
        return Response({"guardada": False})
    else:
        receta.guardadas.add(request.user)
        return Response({"guardada": True})


@api_view(["GET"])
def api_mis_recetas(request):
    creaciones = Receta.objects.filter(autor=request.user).order_by("-fecha_creacion")
    favoritas = Receta.objects.filter(guardadas=request.user).order_by(
        "-fecha_creacion"
    )
    return Response(
        {
            "creaciones": RecetaListSerializer(
                creaciones, many=True, context={"request": request}
            ).data,
            "favoritas": RecetaListSerializer(
                favoritas, many=True, context={"request": request}
            ).data,
        }
    )


# PERFIL - FOTO
@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def api_actualizar_foto_perfil(request):
    if "foto_perfil" in request.FILES:
        request.user.foto_perfil = request.FILES["foto_perfil"]
        request.user.save()
        serializer = UsuarioSerializer(request.user, context={"request": request})
        return Response(serializer.data)
    return Response(
        {"error": "No se recibió imagen"}, status=status.HTTP_400_BAD_REQUEST
    )
