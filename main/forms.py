"""ModelForm aplikasi main untuk entitas Project dan Skill.

Tiap form menetapkan `fields` secara eksplisit, bukan `__all__`, supaya kolom
seperti `id` dan `created_at` yang tidak boleh diisi pengguna tidak ikut
terekspos hanya karena suatu saat ditambahkan ke model.
"""

from django.forms import (
    CharField,
    CheckboxInput,
    ModelForm,
    Select,
    Textarea,
    TextInput,
    URLInput,
)
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from main.models import Project, Skill, SkillCategory


class ProjectForm(ModelForm):
    """Form tambah/sunting proyek.

    Seluruh field boleh diisi pengguna; `id` tidak disertakan karena UUID-nya
    dibuat otomatis oleh model dan bersifat `editable=False`.
    """

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

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Nama proyek tidak boleh hanya berisi tag HTML.")
        return title

    def clean_tech_stack(self):
        return strip_tags(self.cleaned_data["tech_stack"]).strip()

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()

class SkillForm(ModelForm):
    """Form tambah/sunting skill, sekaligus jalan pintas membuat kategori baru.

    `new_category` bukan field milik model Skill, melainkan field tambahan milik
    form ini saja. Adanya field itu membuat pengguna bisa memakai kategori yang
    belum ada tanpa perlu halaman CRUD kategori tersendiri.

    `created_at` sengaja tidak masuk `fields` karena diisi otomatis lewat
    `auto_now_add`; memasukkannya cuma akan menampilkan kolom yang nilainya
    selalu ditimpa.
    """

    new_category = CharField(
        required=False,
        label="Atau kategori baru",
        widget=TextInput(attrs={"placeholder": "Machine Learning"}),
        help_text="Isi kalau kategori yang kamu mau belum ada di dropdown.",
    )

    class Meta:
        model = Skill
        fields = ["name", "category", "icon", "is_featured"]

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
        """Longgarkan field `category` supaya `new_category` bisa jadi gantinya.

        Secara bawaan ForeignKey yang tidak nullable membuat `category` wajib
        diisi, sehingga form langsung ditolak sebelum `clean()` sempat membaca
        `new_category`. Di sini `required` dimatikan dan pengecekan "salah satu
        harus terisi" dipindahkan ke `clean()`.
        """
        super().__init__(*args, **kwargs)
        self.fields["category"].required = False
        self.fields["category"].empty_label = "— pilih kategori —"

    def clean_name(self):
        name = strip_tags(self.cleaned_data["name"]).strip()
        if not name:
            raise ValidationError("Nama skill tidak boleh hanya berisi tag HTML.")
        return name

    def clean_icon(self):
        return strip_tags(self.cleaned_data["icon"]).strip()

    def clean_new_category(self):
        return strip_tags(self.cleaned_data["new_category"]).strip()

    def clean(self):
        """Pastikan skill punya kategori, dari dropdown maupun ketikan baru.

        Kategori baru dibuat di sini, bukan di `save()`, karena ModelForm
        menyusun instance dari `cleaned_data` tepat setelah `clean()` selesai —
        kalau menunggu `save()`, `category` masih kosong saat validasi model
        berjalan dan form gagal dengan alasan yang membingungkan.

        Pencocokan memakai `name__iexact` agar "machine learning" tidak
        membuat kategori kedua saat "Machine Learning" sudah ada. Kategori baru
        ditaruh di urutan paling belakang supaya susunan kategori lama tidak
        bergeser.

        Konsekuensi yang disadari: kalau field lain gagal validasi setelah blok
        ini, kategori sudah terlanjur dibuat dan perlu dihapus lewat admin.
        """
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
