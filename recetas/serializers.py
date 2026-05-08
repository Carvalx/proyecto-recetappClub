from rest_framework import serializers
from .models import Usuario, Receta, Ingrediente, Comentario, Categoria, Valoracion


class UsuarioSerializer(serializers.ModelSerializer):
    pais = serializers.CharField(source="pais.code", allow_blank=True, default="")

    class Meta:
        model = Usuario
        fields = ["id", "username", "email", "foto_perfil", "bio", "pais"]


class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = ["username", "email", "password", "password2"]

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError(
                {"password": "Las contraseñas no coinciden"}
            )
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        user = Usuario.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre"]


class IngredienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingrediente
        fields = ["id", "nombre", "cantidad"]


class ComentarioSerializer(serializers.ModelSerializer):
    autor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comentario
        fields = ["id", "autor", "texto", "fecha"]


class ValoracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Valoracion
        fields = ["id", "puntuacion"]


class RecetaSerializer(serializers.ModelSerializer):
    autor = serializers.StringRelatedField(read_only=True)
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        source="categoria",
        write_only=True,
        required=False,
    )
    ingredientes = IngredienteSerializer(many=True, read_only=True)
    comentarios = ComentarioSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    valoracion_media = serializers.SerializerMethodField()
    guardada = serializers.SerializerMethodField()

    class Meta:
        model = Receta
        fields = [
            "id",
            "titulo",
            "descripcion",
            "instrucciones",
            "imagen",
            "autor",
            "categoria",
            "categoria_id",
            "fecha_creacion",
            "ingredientes",
            "comentarios",
            "likes_count",
            "valoracion_media",
            "guardada",
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_valoracion_media(self, obj):
        from django.db.models import Avg

        result = obj.valoraciones.aggregate(Avg("puntuacion"))["puntuacion__avg"]
        return round(result, 1) if result else None

    def get_guardada(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.guardadas.filter(pk=request.user.pk).exists()
        return False


class RecetaListSerializer(serializers.ModelSerializer):
    autor = serializers.StringRelatedField(read_only=True)
    categoria = CategoriaSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    valoracion_media = serializers.SerializerMethodField()

    class Meta:
        model = Receta
        fields = [
            "id",
            "titulo",
            "descripcion",
            "imagen",
            "autor",
            "categoria",
            "fecha_creacion",
            "likes_count",
            "valoracion_media",
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_valoracion_media(self, obj):
        from django.db.models import Avg

        result = obj.valoraciones.aggregate(Avg("puntuacion"))["puntuacion__avg"]
        return round(result, 1) if result else None
