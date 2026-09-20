"""Model aplikasi main: Experience, Project, dan pasangan SkillCategory-Skill.

Semua model memakai UUID sebagai primary key, bukan auto-increment, supaya id
yang muncul di URL tidak membocorkan jumlah baris maupun urutan pembuatannya.
"""

import uuid

from django.db import models
from django.utils.text import slugify


class Experience(models.Model):
    """Satu pengalaman kerja, riset, atau kegiatan volunteer.

    Rentang waktunya disimpan sebagai pasangan `started_at` dan `ended_at`;
    `ended_at` yang kosong berarti kegiatannya masih berjalan, bukan datanya
    yang belum lengkap.
    """

    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        """True selama `ended_at` masih kosong.

        Dijadikan properti supaya definisi "masih berjalan" cuma ditulis sekali
        di sini; view tinggal memakainya dan tidak perlu mengulang pengecekan
        `ended_at is None` sendiri-sendiri.
        """
        return self.ended_at is None


class Project(models.Model):
    """Satu proyek di halaman portofolio.

    Gambar proyek disimpan sebagai URL eksternal, bukan file upload, supaya
    proyek ini tidak perlu menyediakan media storage saat di-deploy.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    tech_stack = models.CharField(max_length=255)
    project_url = models.URLField(blank=True)
    project_image_url = models.URLField(blank=True, max_length=500)

    def __str__(self):
        return self.title


class SkillCategory(models.Model):
    """Kelompok skill, misalnya "Fullstack" atau "Cybersecurity".

    Dipisah jadi model tersendiri (bukan `choices` di Skill) supaya kategori
    bisa ditambah lewat form tanpa mengubah kode dan membuat migrasi baru.

    `slug` dipakai dua kali di halaman skill: sebagai atribut `data-category`
    tiap kartu dan sebagai `value` tiap opsi dropdown filter. Karena keduanya
    dirender dari baris yang sama, nilainya mustahil jadi tidak sinkron.
    `order` memungkinkan urutan tampil diatur manual, tidak terpaku abjad.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'skill categories'

    def save(self, *args, **kwargs):
        """Isi `slug` otomatis dari `name` kalau masih kosong.

        Perulangannya wajib ada karena `slug` unique sementara `slugify` bisa
        menghasilkan nilai kembar dari nama yang berbeda — "Design" dan
        "Beside the Keyboard" (yang slug-nya memang disetel "design" saat
        seeding) akan bertabrakan. Tanpa penambahan sufiks angka, menambah
        kategori lewat form berujung IntegrityError, bukan pesan error yang
        bisa dibaca pengguna.

        `exclude(pk=self.pk)` menjaga agar objek yang sedang disimpan tidak
        dihitung bertabrakan dengan dirinya sendiri saat diperbarui.
        """
        if not self.slug:
            base = slugify(self.name)
            slug, n = base, 2
            while SkillCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Skill(models.Model):
    """Satu kemampuan yang ditampilkan sebagai pill di halaman skill.

    `on_delete=PROTECT`, bukan CASCADE: menghapus kategori yang masih berisi
    skill akan ditolak, bukan diam-diam ikut menghapus seluruh isinya.
    Urutan tampil memakai `created_at` supaya susunan pill mengikuti urutan
    penambahan dan tetap stabil, tidak berubah setiap field lain disunting.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        SkillCategory,
        on_delete=models.PROTECT,
        related_name="skills",
    )
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category__order', 'created_at']

    @property
    def icon_kind(self):
        """Tentukan cara icon harus dirender: "devicon", "image", "emoji", atau "".

        Satu field `icon` menampung tiga bentuk yang berbeda — class font
        devicon, URL gambar, dan karakter emoji — sehingga tidak perlu kolom
        tambahan hanya untuk menandai jenisnya. Penggolongannya dikerjakan di
        sini, bukan di template, supaya template cukup mencocokkan hasilnya dan
        tidak ikut menebak-nebak isi string.
        """
        if self.icon.startswith("devicon-"):
            return "devicon"
        if self.icon.startswith("http"):
            return "image"
        return "emoji" if self.icon else ""

    def __str__(self):
        return self.name
