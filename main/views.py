import datetime
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, permission_required 
from django.core.exceptions import PermissionDenied    
from django.db.models import Count
from django.views.decorators.http import require_POST

from main.forms import ProjectForm, SkillForm
from main.models import Experience, Project, Skill, SkillCategory


def show_main(request):
    """Tampilkan halaman profil beserta waktu login terakhir dari cookie.

    `last_login` sengaja dibaca dari cookie, bukan dari `request.user`, supaya
    nilainya tetap ada meski pengguna sudah logout — cookie-nya baru dihapus
    di `logout_user`. Nilai default dipakai kalau cookie belum pernah dipasang,
    agar template tidak perlu menangani kasus kosong sendiri.
    """
    last_login = request.COOKIES.get('last_login', 'No login session yet / Cookie not found')
    context = {
        "name": "Violin Monica",
        "npm": "2506551794",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Lolz"
        ),
        "last_login": last_login,
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

@login_required(login_url="/login/")    
def create_project(request):
    """Tangani penambahan proyek baru lewat ProjectForm.

    Satu view melayani dua method: pada GET, `request.POST or None` bernilai
    None sehingga form dirender kosong (unbound); pada POST form jadi bound dan
    divalidasi. Kalau valid, data disimpan lalu redirect ke daftar proyek —
    pola POST/redirect/GET, supaya refresh browser tidak menyimpan data dua
    kali. Kalau tidak valid, form dirender ulang lengkap dengan pesan error.
    """
    if not request.user.is_superuser:
        raise PermissionDenied
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
    judul memakai `icontains` supaya tidak peduli huruf besar-kecil. Daftar `fields` dibatasi eksplisit, bukan menyerialisasi seluruh model:
    relasi `starred_by` menyimpan pengguna yang memberi star, dan tanpa
    pembatasan ini endpoint publik ikut memuat id (atau username) mereka.
    Jumlah star dan status "sudah di-star" dihitung sekali lewat dua query
    agregat, sama seperti pada halaman skill, supaya template tidak memanggil
    `project.starred_by` sendiri-sendiri untuk tiap kartu.
    """
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.prefetch_related('starred_by').all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    # Konstruksi data JSON secara manual agar bisa menyisipkan logika Star
    data = []
    for project in projects:
        starred_users = project.starred_by.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(project.id),
            "fields": {
                "title": project.title,
                "description": project.description,
                "tech_stack": project.tech_stack,
                "project_url": project.project_url,
                "project_image_url": project.project_image_url,
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            }
        })

    return JsonResponse(data, safe=False)



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
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Violin Monica",
        "title_query": title_query,
        "form": ProjectForm(),
    }
    return render(request, "project.html", context)

@login_required(login_url="/login/")
@permission_required("main.delete_project", raise_exception=True)
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
    """Endpoint JSON skill yang dikelompokkan per kategori, plus info star.

    Disusun manual dengan JsonResponse supaya bisa menyisipkan `star_count` dan
    `is_starred`. Total query tetap tiga (kategori, skill+jumlah star, id skill
    yang di-star user), berapa pun jumlah skill-nya.
    """
    name_query = request.GET.get("name", "").strip()
    skills = Skill.objects.select_related("category").annotate(star_count=Count("starred_by"))
    if name_query:
        skills = skills.filter(name__icontains=name_query)
    starred_ids = (
            set(request.user.starred_skills.values_list("id", flat=True))
            if request.user.is_authenticated
            else set()
        )
    categories = {
        c.id: {"name": c.name, "slug": c.slug, "skills": []}
        for c in SkillCategory.objects.all()
    }
    for skill in skills:
        categories[skill.category_id]["skills"].append({
            "id": str(skill.id),
            "name": skill.name,
            "icon": skill.icon,
            "icon_kind": skill.icon_kind,
            "is_featured": skill.is_featured,
            "star_count": skill.star_count,
            "is_starred": skill.id in starred_ids,
        })
    
    # Saat mencari, kategori tanpa hasil tidak ikut dikirim
    data = [c for c in categories.values() if c["skills"] or not name_query]
    return JsonResponse(data, safe=False)


# def _categories_with_skills(request):
#     """Ambil skill lewat endpoint JSON, deserialisasi, lalu kelompokkan per kategori.
#     Helper privat — diawali underscore karena bukan view dan tidak dipetakan di
#     urls.py. Pengelompokan memakai satu dict `grouped` berkunci id kategori
#     supaya total query tetap dua saja; kalau tiap kategori memanggil
#     `category.skills.all()` sendiri-sendiri, jumlah query ikut bertambah
#     sebanyak kategori (masalah N+1). Hasilnya ditempelkan ke tiap kategori
#     sebagai atribut `skill_items` agar bisa langsung dilooping di template. 
#     Jumlah star dan status "sudah di-star" dihitung sekali di sini lewat dua
#     query agregat, lalu ditempelkan ke tiap objek. Kalau template memanggil
#     `skill.starred_by.count` sendiri-sendiri, jumlah query ikut bertambah
#     sebanyak skill yang dirender.
#     """
#     json_response = get_skills_json(request)
#     skills = [
#         wrapper.object
#         for wrapper in serializers.deserialize(
#             "json", json_response.content.decode("utf-8")
#         )
#     ]

#     categories = list(SkillCategory.objects.all())
#     grouped = {category.id: [] for category in categories}
#     star_counts = dict(
#         Skill.objects.annotate(total=Count("starred_by")).values_list("id", "total")
#     )
#     starred_ids = (
#         set(request.user.starred_skills.values_list("id", flat=True))
#         if request.user.is_authenticated
#         else set()
#     )
#     for skill in skills:
#         skill.star_count = star_counts.get(skill.id, 0)
#         skill.is_starred = skill.id in starred_ids
#         grouped[skill.category_id].append(skill)

#     for category in categories:
#         category.skill_items = grouped[category.id]

#     return categories


def show_skills(request):
    """Render kerangka halaman skill; isinya diambil lewat fetch() ke get_skills_json."""
    return render(request, "skill.html", {"form": SkillForm()})

@login_required(login_url="/login/")
@permission_required("main.add_skill", raise_exception=True)
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

@require_POST
def create_skill_ajax(request):
    """Tambah skill lewat AJAX dari modal di halaman skill.

    Hak akses dicek di sini, bukan cuma lewat tombol yang disembunyikan di
    template — request POST bisa dikirim langsung tanpa membuka halamannya.
    Tidak memakai @login_required/@permission_required karena keduanya membalas
    redirect/HTML, sedangkan pemanggilnya fetch() yang mengharapkan JSON.
    """
    if not request.user.has_perm("main.add_skill"):
        return JsonResponse(
            {"message": "Kamu tidak punya izin untuk menambahkan skill."},
            status=403,
        )

    form = SkillForm(request.POST)
    if form.is_valid():
        skill = form.save()
        return JsonResponse(
            {"message": "Skill berhasil ditambahkan.", "id": str(skill.id)},
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@login_required(login_url="/login/")
@permission_required("main.change_skill", raise_exception=True)
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

@login_required(login_url="/login/")
@permission_required("main.delete_skill", raise_exception=True)
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

def register(request):
    """Buat akun baru lewat `UserCreationForm` bawaan Django.

    Memakai form bawaan, bukan menulis sendiri, karena form itu sudah membawa
    validasi password Django (panjang minimum, tidak terlalu umum, tidak mirip
    username) dan hashing lewat `set_password`. Setelah sukses pengguna
    diarahkan ke halaman login, bukan langsung di-login, supaya akun yang baru
    dibuat benar-benar diuji kredensialnya sekali.
    """
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account is succesfully created. Please login.")
        return redirect("main:login")

    context = {
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    """Akhiri sesi pengguna dan bersihkan cookie `last_login`.

    `logout()` menghapus data sesi di sisi server, tapi cookie `last_login`
    dipasang terpisah oleh view ini sendiri sehingga tidak ikut terhapus. Kalau
    tidak dihapus manual, halaman profil masih memajang waktu login milik akun
    sebelumnya setelah pengguna keluar.
    """
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

@login_required(login_url="/login/")
def toggle_skill_star(request, skill_id):
    """Beri atau batalkan star pada satu skill untuk pengguna yang sedang login.

    Hanya POST yang mengubah data; GET diarahkan balik tanpa efek supaya star
    tidak bisa terpicu lewat URL yang sekadar dibuka atau di-prefetch browser.
    Pengecekan memakai `.exists()` alih-alih `request.user in
    skill.starred_by.all()` agar cukup satu query COUNT, bukan memuat seluruh
    daftar pengguna ke memori hanya untuk satu pemeriksaan keanggotaan.
    """
    skill = get_object_or_404(Skill, pk=skill_id)

    if request.method == "POST":
        if skill.starred_by.filter(pk=request.user.pk).exists():
            skill.starred_by.remove(request.user)
        else:
            skill.starred_by.add(request.user)

    return redirect("main:show_skills")

@login_required(login_url="/login/")
def toggle_project_star(request, project_id):
    """Beri atau batalkan star pada satu proyek untuk pengguna yang sedang login.

    Hanya POST yang mengubah data; GET diarahkan balik tanpa efek supaya star
    tidak bisa terpicu lewat URL yang sekadar dibuka atau di-prefetch browser.
    Pengecekan memakai `.exists()` alih-alih `request.user in
    project.starred_by.all()` agar cukup satu query COUNT, bukan memuat seluruh
    daftar pengguna ke memori hanya untuk satu pemeriksaan keanggotaan.
    """
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        if project.starred_by.filter(pk=request.user.pk).exists():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    return redirect("main:show_projects")

@require_POST
def create_project_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )

    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {"message": "Proyek berhasil ditambahkan.", "pk": str(project.id)},
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

