from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q, Count
from .models import Receta, Categoria, Comentario, Valoracion, Ingrediente
from .forms import (
    RegistroForm,
    RecetaForm,
    IngredienteFormSet,
    ComentarioForm,
    EditarPerfilForm,
)
import base64
from django.core.files.base import ContentFile


def guardar_imagen_base64(receta, base64_str):
    if base64_str and base64_str.startswith("data:image"):
        formato, datos = base64_str.split(";base64,")
        ext = formato.split("/")[-1]
        nombre = f"receta_{receta.pk}.{ext}"
        receta.imagen.save(nombre, ContentFile(base64.b64decode(datos)), save=True)


def inicio(request):
    if request.user.is_authenticated:
        return redirect("explorar")
    return render(request, "recetas/inicio.html")


def explorar(request):
    query = request.GET.get("q", "")
    categoria_id = request.GET.get("categoria", "")
    ingrediente = request.GET.get("ingrediente", "")

    recetas = Receta.objects.all()

    if query:
        recetas = recetas.filter(Q(titulo__icontains=query))
    if categoria_id:
        recetas = recetas.filter(categoria_id=categoria_id)
    if ingrediente:
        recetas = recetas.filter(ingredientes__nombre__icontains=ingrediente)

    recetas = recetas.distinct().order_by("-fecha_creacion")

    mas_valoradas = (
        Receta.objects.annotate(media=Avg("valoraciones__puntuacion"))
        .filter(media__isnull=False)
        .order_by("-media")[:6]
    )

    mas_populares = Receta.objects.annotate(total_likes=Count("likes")).order_by(
        "-total_likes"
    )[:6]

    categorias = Categoria.objects.all()

    return render(
        request,
        "recetas/explorar.html",
        {
            "recetas": recetas,
            "categorias": categorias,
            "mas_valoradas": mas_valoradas,
            "mas_populares": mas_populares,
            "query": query,
            "categoria_id": categoria_id,
            "ingrediente": ingrediente,
        },
    )


def novedades(request):
    recetas = Receta.objects.order_by("-fecha_creacion")[:20]
    return render(request, "recetas/novedades.html", {"recetas": recetas})


def lista_recetas(request):
    query = request.GET.get("q", "")
    categoria_id = request.GET.get("categoria", "")
    recetas = Receta.objects.all().order_by("-fecha_creacion")
    if query:
        recetas = recetas.filter(
            Q(titulo__icontains=query) | Q(descripcion__icontains=query)
        )
    if categoria_id:
        recetas = recetas.filter(categoria_id=categoria_id)
    categorias = Categoria.objects.all()
    return render(
        request,
        "recetas/lista.html",
        {
            "recetas": recetas,
            "categorias": categorias,
            "query": query,
            "categoria_id": categoria_id,
        },
    )


def detalle_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk)
    comentarios = receta.comentarios.all().order_by("-fecha")
    valoracion_media = receta.valoraciones.aggregate(Avg("puntuacion"))[
        "puntuacion__avg"
    ]
    mi_valoracion = None
    comentario_form = ComentarioForm()
    ya_guardada = False

    if request.user.is_authenticated:
        ya_guardada = receta.guardadas.filter(pk=request.user.pk).exists()
        try:
            mi_valoracion = Valoracion.objects.get(
                receta=receta, usuario=request.user
            ).puntuacion
        except Valoracion.DoesNotExist:
            pass

        if request.method == "POST":
            if "comentario" in request.POST:
                comentario_form = ComentarioForm(request.POST)
                if comentario_form.is_valid():
                    c = comentario_form.save(commit=False)
                    c.receta = receta
                    c.autor = request.user
                    c.save()
                    return redirect("detalle_receta", pk=pk)

            elif "puntuacion" in request.POST:
                puntuacion = request.POST.get("puntuacion")
                Valoracion.objects.update_or_create(
                    receta=receta,
                    usuario=request.user,
                    defaults={"puntuacion": puntuacion},
                )
                return redirect("detalle_receta", pk=pk)

            elif "like" in request.POST:
                if request.user in receta.likes.all():
                    receta.likes.remove(request.user)
                else:
                    receta.likes.add(request.user)
                return redirect("detalle_receta", pk=pk)

            elif "guardar" in request.POST:
                if request.user in receta.guardadas.all():
                    receta.guardadas.remove(request.user)
                else:
                    receta.guardadas.add(request.user)
                return redirect("detalle_receta", pk=pk)

    return render(
        request,
        "recetas/detalle.html",
        {
            "receta": receta,
            "comentarios": comentarios,
            "comentario_form": comentario_form,
            "valoracion_media": valoracion_media,
            "mi_valoracion": mi_valoracion,
            "ya_guardada": ya_guardada,
        },
    )


@login_required
def crear_receta(request):
    if request.method == "POST":
        form = RecetaForm(request.POST, request.FILES)
        formset = IngredienteFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            receta = form.save(commit=False)
            receta.autor = request.user
            receta.save()
            formset.instance = receta
            formset.save()
            base64_str = request.POST.get("imagen_recortada", "")
            if base64_str:
                guardar_imagen_base64(receta, base64_str)
            return redirect("mis_recetas")
    else:
        form = RecetaForm()
        formset = IngredienteFormSet()
    return render(
        request, "recetas/crear_receta.html", {"form": form, "formset": formset}
    )


@login_required
def editar_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk, autor=request.user)
    if request.method == "POST":
        form = RecetaForm(request.POST, request.FILES, instance=receta)
        formset = IngredienteFormSet(request.POST, request.FILES, instance=receta)
        if form.is_valid() and formset.is_valid():
            receta = form.save()
            formset.save()
            base64_str = request.POST.get("imagen_recortada", "")
            if base64_str:
                guardar_imagen_base64(receta, base64_str)
            return redirect("mis_recetas")
    else:
        form = RecetaForm(instance=receta)
        formset = IngredienteFormSet(instance=receta)
    return render(
        request,
        "recetas/crear_receta.html",
        {"form": form, "formset": formset, "editando": True},
    )


@login_required
def eliminar_receta(request, pk):
    receta = get_object_or_404(Receta, pk=pk, autor=request.user)
    if request.method == "POST":
        receta.delete()
        return redirect("mis_recetas")


@login_required
def mis_recetas(request):
    creaciones = request.user.recetas.all().order_by("-fecha_creacion")
    favoritas = Receta.objects.filter(guardadas=request.user).order_by(
        "-fecha_creacion"
    )
    return render(
        request,
        "recetas/mis_recetas.html",
        {
            "creaciones": creaciones,
            "favoritas": favoritas,
        },
    )


@login_required
def perfil(request):
    recetas = request.user.recetas.all().order_by("-fecha_creacion")
    return render(request, "recetas/perfil.html", {"recetas": recetas})


@login_required
def editar_perfil(request):
    if request.method == "POST":
        form = EditarPerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("perfil")
    else:
        form = EditarPerfilForm(instance=request.user)
    return render(request, "recetas/editar_perfil.html", {"form": form})


@login_required
def cambiar_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("perfil")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "recetas/cambiar_password.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("explorar")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("explorar")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("inicio")


def registro(request):
    if request.user.is_authenticated:
        return redirect("explorar")
    if request.method == "POST":
        form = RegistroForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("explorar")
    else:
        form = RegistroForm()
    return render(request, "registration/registro.html", {"form": form})


def politica_privacidad(request):
    return render(request, "recetas/politica_privacidad.html")


def terminos_uso(request):
    return render(request, "recetas/terminos_uso.html")


def politica_cookies(request):
    return render(request, "recetas/politica_cookies.html")
