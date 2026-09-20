from django.forms import ModelForm, TextInput, Textarea, URLInput
from django.forms import (
    CharField, CheckboxInput, IntegerField, ModelForm,
    NumberInput, Select, TextInput,
)
from main.models import Project
from main.models import Skill, SkillCategory

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "tech_stack",
            "project_url",
            "project_image_url",
        ]

        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "tech_stack": "Teknologi yang Digunakan",
            "project_url": "URL Proyek",
            "project_image_url": "URL Gambar Proyek",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan Proyekmu",
                    "rows": 3,
                }
            ),
            "tech_stack": TextInput(
                attrs={
                    "placeholder": "Django, Python, HTML, CSS",
                }
            ),
            "project_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/kakBurhan/burhanquestv4",
                }
            ),
            "project_image_url": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
        }

class SkillForm(ModelForm):
    new_category = CharField(
        required=False,
        label="Atau kategori baru",
        widget=TextInput(attrs={"placeholder": "Machine Learning"}),
        help_text="Isi kalau kategori yang kamu mau belum ada di dropdown.",
    )
    proficiency = IntegerField(
        min_value=1,
        max_value=5,
        initial=3,
        label="Tingkat Penguasaan (1-5)",
        widget=NumberInput(attrs={"min": 1, "max": 5}),
    )

    class Meta:
        model = Skill
        fields = ["name", "category", "icon", "proficiency", "is_featured"]

        labels = {
            "name": "Nama Skill",
            "category": "Kategori",
            "icon": "Icon",
            "is_featured": "Tampilkan sebagai unggulan",
        }

        widgets = {
            "name": TextInput(attrs={"placeholder": "TensorFlow"}),
            "category": Select(),
            "icon": TextInput(attrs={"placeholder": "devicon-python-plain"}),
            "is_featured": CheckboxInput(),
        }

        help_texts = {
            "icon": (
                "Tiga format: class devicon (devicon-python-plain), "
                "URL gambar (https://...), atau emoji. Kosongkan kalau nggak ada."
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].required = False
        self.fields["category"].empty_label = "— pilih kategori —"

    def clean(self):
        cleaned = super().clean()
        new_name = (cleaned.get("new_category") or "").strip()

        if new_name:
            category = SkillCategory.objects.filter(name__iexact=new_name).first()
            if category is None:
                last = SkillCategory.objects.order_by("-order").first()
                category = SkillCategory.objects.create(
                    name=new_name,
                    order=(last.order + 1) if last else 1,
                )
            cleaned["category"] = category
        elif not cleaned.get("category"):
            self.add_error("category", "Pilih kategori yang ada atau isi kategori baru.")

        return cleaned
