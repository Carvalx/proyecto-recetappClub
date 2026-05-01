from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import Usuario, Receta, Ingrediente, Comentario


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        help_text="",
    )
    password2 = forms.CharField(
        label="Confirmar contraseña", widget=forms.PasswordInput, help_text=""
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].max_length = 30
        self.fields["username"].widget.attrs["maxlength"] = 30
        self.fields["username"].help_text = ""

    class Meta:
        model = Usuario
        fields = ["username", "email", "password1", "password2", "foto_perfil", "pais"]


class RecetaForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ["titulo", "descripcion", "instrucciones", "imagen", "categoria"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "instrucciones": forms.Textarea(attrs={"rows": 6}),
        }

    def clean_imagen(self):
        imagen = self.cleaned_data.get("imagen")
        if imagen:
            formatos_validos = [".jpg", ".jpeg", ".png", ".webp"]
            ext = "." + imagen.name.split(".")[-1].lower()
            if ext not in formatos_validos:
                raise forms.ValidationError(
                    "Formato no soportado. Usa JPG, PNG o WebP."
                )
        return imagen


class IngredienteForm(forms.ModelForm):
    class Meta:
        model = Ingrediente
        fields = ["nombre", "cantidad"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "placeholder": "Nombre del ingrediente",
                    "autocomplete": "off",
                }
            ),
            "cantidad": forms.TextInput(
                attrs={
                    "placeholder": "Ej: 200g, 2 tazas, 1/2 kg",
                }
            ),
        }


class IngredienteFormSetBase(BaseInlineFormSet):
    def clean(self):
        super().clean()
        validos = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get("DELETE", False):
                nombre = form.cleaned_data.get("nombre", "").strip()
                if nombre:
                    validos += 1
        if validos < 2:
            raise forms.ValidationError("La receta debe tener al menos 2 ingredientes.")


IngredienteFormSet = inlineformset_factory(
    Receta,
    Ingrediente,
    form=IngredienteForm,
    formset=IngredienteFormSetBase,
    extra=3,
    can_delete=True,
)


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ["texto"]
        widgets = {
            "texto": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Escribe tu comentario..."}
            ),
        }


class EditarPerfilForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].max_length = 30
        self.fields["username"].widget.attrs["maxlength"] = 30

    class Meta:
        model = Usuario
        fields = ["username", "email", "bio", "foto_perfil", "pais"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3}),
        }
