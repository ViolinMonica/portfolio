"""View aplikasi main: halaman profil, experience, serta CRUD Project dan Skill.

Dua entitas dinamis (Project dan Skill) memakai pola yang sama: ada endpoint
`get_*_json` yang jadi satu-satunya sumber data, lalu halaman HTML-nya membaca
endpoint itu dan mendeserialisasinya, bukan query model secara langsung.
"""

from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import ProjectForm, SkillForm
from main.models import Experience, Project, Skill, SkillCategory


def show_main(request):
    """Render halaman utama berisi identitas dan bio.

    Semua isinya statis dan tidak menyentuh database. Nama pemilik situs tidak
    ditaruh di sini karena sudah disuplai ke seluruh template lewat context
    processor `site_identity`.
    """
    context = {
        "npm": "2506551794",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Computer Science student at Universitas Indonesia with a growing "
            "expertise in Cybersecurity and Data Science. I thrive at the "
            "intersection of rigorous logic and creative problem-solving. I am "
            "passionate about uncovering vulnerabilities and leveraging data to "
            "build secure, impactful solutions. Always open to discussing tech "
            "trends, security research, or potential collaborations. Reach me at: "
            "violin.monica@ui.ac.id or violin.monica@ristek.cs.ui.ac.id or "
            "violinmonica190207@gmail.com."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    """Tampilkan experience terurut dari yang terbaru, dipisah ongoing vs selesai.

    Pemisahan dikerjakan di Python lewat properti `Experience.is_ongoing` supaya
    definisi "masih berjalan" hidup di satu tempat saja (model), bukan
    diduplikasi jadi dua filter query di view ini.
    """
    experiences = Experience.objects.all().order_by("-started_at")
    context = {
        "ongoing_list": [e for e in experiences if e.is_ongoing],
        "past_list": [e for e in experiences if not e.is_ongoing],
    }
    return render(request, "experience.html", context)


def create_project(request):
    """Tangani penambahan proyek baru lewat ProjectForm.

    Satu view melayani dua method: pada GET, `request.POST or None` bernilai
    None sehingga form dirender kosong (unbound); pada POST form jadi bound dan
    divalidasi. Kalau valid, data disimpan lalu redirect ke daftar proyek —
    pola POST/redirect/GET, supaya refresh browser tidak menyimpan data dua
    kali. Kalau tidak valid, form dirender ulang lengkap dengan pesan error.
    """
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "form": form,
    }
    return render(request, "projects_form.html", context)


def get_projects_json(request):
    """Endpoint JSON seluruh proyek, opsional difilter lewat query string `?title=`.

    Formatnya mengikuti serializer bawaan Django: list objek berisi kunci
    "model", "pk", dan "fields". Dikonsumsi dua pihak — `show_projects` yang
    memanggilnya langsung di dalam proses, dan siapa pun yang membuka URL-nya
    (fetch dari JavaScript maupun pengecekan manual lewat browser). Pencarian
    judul memakai `icontains` supaya tidak peduli huruf besar-kecil.
    """
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")


def show_projects(request):
    """Tampilkan halaman proyek dari hasil deserialisasi endpoint JSON.

    Sengaja tidak query `Project.objects` langsung: data diambil dari
    `get_projects_json`, lalu `serializers.deserialize` mengubahnya kembali jadi
    instance Project (diakses lewat atribut `.object` tiap wrapper). Dengan
    begitu halaman HTML dan endpoint JSON dijamin menampilkan data serta hasil
    filter yang persis sama. `title_query` dibaca ulang semata-mata untuk
    mengisi kembali kotak pencarian di template.
    """
    json_response = get_projects_json(request)

    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    projects = [project.object for project in projects]
    title_query = request.GET.get("title", "").strip()

    context = {
        "project_list": projects,
        "title_query": title_query,
    }
    return render(request, "project.html", context)


def delete_project(request, project_id):
    """Hapus satu proyek, lalu selalu kembali ke daftar proyek.

    Penghapusan hanya dijalankan kalau method-nya POST. GET sengaja dibiarkan
    tidak berefek karena URL yang bisa dibuka lewat GET gampang terpicu tanpa
    sengaja — prefetch browser, crawler, atau sekadar link yang tertempel. Jadi
    cabang non-POST cuma redirect balik tanpa mengubah data apa pun.
    """
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")

    return redirect("main:show_projects")


def get_skills_json(request):
    """Endpoint JSON seluruh skill, terurut sesuai `Skill.Meta.ordering`.

    Sama seperti `get_projects_json`, isinya format serializer Django
    ("model"/"pk"/"fields") dan jadi satu-satunya sumber data skill: dipakai
    `_categories_with_skills` untuk mengisi halaman, sekaligus bisa dibuka
    langsung sebagai URL. Tidak ada parameter filter karena jumlah skill kecil
    dan pengelompokannya dikerjakan di sisi Python.
    """
    return HttpResponse(
        serializers.serialize("json", Skill.objects.all()),
        content_type="application/json",
    )


def _categories_with_skills(request):
    """Ambil skill lewat endpoint JSON, deserialisasi, lalu kelompokkan per kategori.

    Helper privat — diawali underscore karena bukan view dan tidak dipetakan di
    urls.py. Pengelompokan memakai satu dict `grouped` berkunci id kategori
    supaya total query tetap dua saja; kalau tiap kategori memanggil
    `category.skills.all()` sendiri-sendiri, jumlah query ikut bertambah
    sebanyak kategori (masalah N+1). Hasilnya ditempelkan ke tiap kategori
    sebagai atribut `skill_items` agar bisa langsung dilooping di template.
    """
    json_response = get_skills_json(request)
    skills = [
        wrapper.object
        for wrapper in serializers.deserialize(
            "json", json_response.content.decode("utf-8")
        )
    ]

    categories = list(SkillCategory.objects.all())
    grouped = {category.id: [] for category in categories}
    for skill in skills:
        grouped[skill.category_id].append(skill)

    for category in categories:
        category.skill_items = grouped[category.id]

    return categories


def show_skills(request):
    """Render halaman skill berisi daftar kategori beserta skill di dalamnya."""
    return render(
        request, "skill.html", {"category_list": _categories_with_skills(request)}
    )


def create_skill(request):
    """Tangani penambahan skill baru lewat SkillForm.

    Alurnya sama persis dengan `create_project`. Bedanya SkillForm punya field
    tambahan `new_category`, sehingga pengguna bisa membuat kategori baru dari
    form yang sama; pembuatan kategori itu sendiri ditangani di
    `SkillForm.clean()`, bukan di view ini.
    """
    form = SkillForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Skill baru berhasil ditambahkan!")
        return redirect("main:show_skills")

    return render(request, "skills_form.html", {"form": form})


def edit_skill(request, skill_id):
    """Tangani penyuntingan skill yang sudah ada.

    Memakai template form yang sama dengan `create_skill`; pembedanya argumen
    `instance=skill`, yang membuat form terisi nilai lama saat GET dan
    memperbarui baris yang sama (bukan membuat baris baru) saat POST. Objek
    `skill` ikut dikirim ke template supaya judul halaman dan action form-nya
    bisa menyesuaikan mode edit.
    """
    skill = get_object_or_404(Skill, pk=skill_id)
    form = SkillForm(request.POST or None, instance=skill)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Skill berhasil diperbarui!")
        return redirect("main:show_skills")

    return render(request, "skills_form.html", {"form": form, "skill": skill})


def delete_skill(request, skill_id):
    """Hapus satu skill, lalu selalu kembali ke halaman skill.

    Sengaja dibuat sebentuk dengan `delete_project`: hanya POST yang
    benar-benar menghapus, request lain cuma diarahkan balik tanpa efek samping.
    """
    skill = get_object_or_404(Skill, pk=skill_id)

    if request.method == "POST":
        skill.delete()
        messages.success(request, "Skill berhasil dihapus!")

    return redirect("main:show_skills")
