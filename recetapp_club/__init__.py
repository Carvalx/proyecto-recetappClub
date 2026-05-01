def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields["username"].max_length = 30
    self.fields["username"].widget.attrs["maxlength"] = 30
    self.fields["username"].help_text = ""  # 👈 esto elimina el texto
