# Nama: Violin Monica  
# Kelas: PBP B  
# NPM: 2506551794 
# Portfolio Website

Portfolio pribadi yang menampilkan profil, skill, pengalaman, dan proyek yang pernah saya kerjakan. Dibangun untuk mata kuliah Pemrograman Berbasis Platform (PBP). Dimulai sebagai halaman statis (Tugas 1) dan dikembangkan menjadi aplikasi Django yang menyimpan data pengalaman dan proyek pada model serta menampilkannya lewat view dan template (Tugas 2).

## Tech Stack
- Python 3.x & Django
- HTML5 & CSS3 (custom, tanpa framework CSS)
- JavaScript vanilla (fitur filter skill)
- Django Template Language (DTL) dengan template inheritance
- Font: Space Grotesk (Google Fonts), ikon: Devicon & Simple Icons

### Setup & Menjalankan Proyek
Prasyarat
- Python 3.x
- pip
- Git

A. Pertama kali (setelah clone repository)

Karena aplikasi ini menggunakan model dan database, orang yang baru meng-clone repo harus menyiapkan skema database terlebih dahulu. Kalau langkah migrasi dilewati, server akan error karena tabel belum ada.

```bash
# 1. Clone repository
git clone https://github.com/ViolinMonica/portfolio.git
cd portfolio

# 2. Buat virtual environment (disarankan untuk menghindari konflik versi)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Terapkan skema database (WAJIB untuk Tugas 2 ke atas)
python manage.py migrate

# 5. (Opsional) buat superuser untuk mengisi data lewat halaman admin
python manage.py createsuperuser

# 6. Jalankan development server
python manage.py runserver
```

Buka http://127.0.0.1:8000 di browser.
A2. Menyiapkan peran Editor (WAJIB untuk Tugas 4)

Peran Editor disimpan sebagai Django Group di database, bukan di kode, jadi
tidak ikut ter-clone bersama repositori. Setelah `migrate`, buat perannya
lewat halaman admin:

1. `python manage.py createsuperuser`, lalu `python manage.py runserver`
2. Buka http://127.0.0.1:8000/admin/ dan login
3. Authentication and Authorization -> Groups -> Add group
4. Name: `Editor`
5. Pada *Available permissions*, pindahkan ke kanan:
   - `main | skill | Can add skill`
   - `main | skill | Can change skill`

   Jangan masukkan `Can delete skill` — hak hapus sengaja hanya untuk admin.
6. Save, lalu buka **Users**, pilih user yang mau dijadikan editor, dan
   pindahkan group `Editor` ke kanan pada bagian *Groups*.

B. Menjalankan proyek sehari-hari

Setelah setup pertama selesai, cukup:

```bash
source venv/bin/activate   # Windows: venv\Scripts\activate
python manage.py runserver
```

C. Jika mengubah models.py

Setiap kali ada perubahan pada model (menambah/menghapus field, menambah model baru, dsb.), jalankan dua perintah berikut secara berurutan:

```bash
python manage.py makemigrations   
python manage.py migrate           
```

D. Menjalankan test
```bash
python manage.py test
```

### Struktur Folder (ringkas)
```text
portfolio/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── portfolio/            
│   ├── settings.py
│   ├── urls.py              
│   ├── wsgi.py
│   ├── asgi.py
│   └── __init__.py
│
├── main/                   
│   ├── models.py           
│   ├── views.py            
│   ├── urls.py              
│   ├── context_processors.py
│   ├── tests.py            
│   └── migrations/          
│
├── templates/
│   ├── base.html            
│   ├── index.html          
│   ├── experience.html     
│   └── projects.html       
│
├── static/
│    ├── css/
│    │   └── style.css
│    ├── js/
│    │   └── script.js         
│    └── img/
│     ├── bobol.png            
│     ├── nusa-crop.png       
│     ├── portofolio.png   
│     └── profile.jpg  
```

## Deployment
Live di: https://violin-monica-portofolio.pws.cs.ui.ac.id

## Peran dan Hak Akses

| Peran | Lihat skills | Star | Create & Update | Delete |
|---|---|---|---|---|
| Pengunjung (belum login) | ✅ | ❌ redirect ke login | ❌ redirect ke login | ❌ redirect ke login |
| Pengguna terdaftar | ✅ | ✅ | ❌ 403 Forbidden | ❌ 403 Forbidden |
| Editor (Django Group) | ✅ | ✅ | ✅ | ❌ 403 Forbidden |
| Admin (superuser) | ✅ | ✅ | ✅ | ✅ |

Pembatasannya ditegakkan di sisi server.
Tiap view skill yang mengubah data memakai dua decorator bertumpuk:

```python
@login_required(login_url="/login/")
@permission_required("main.change_skill", raise_exception=True)
```

Urutannya menentukan perilaku. login_required dievaluasi lebih dulu sehingga
pengunjung anonim diarahkan ke halaman login, sedangkan pengguna yang sudah
login tapi tidak berizin diteruskan ke permission_required dan menerima
403 Forbidden berkat raise_exception=True. Kalau hanya permission_required
yang dipakai, pengunjung anonim ikut menerima 403; kalau raise_exception
dihilangkan, pengguna terdaftar malah dilempar ke halaman login padahal sudah
login. Permission add_skill, change_skill, dan delete_skill tidak
didefinisikan manual — Django membuatnya otomatis untuk tiap model.

Di template, tombol disembunyikan lewat {% if perms.main.add_skill %} dan
seterusnya. Ini murni soal kerapian tampilan; yang benar-benar menahan akses
tetap decorator di atas, karena URL-nya bisa diketik langsung.

Sejak Tugas 5, tambah skill dilakukan lewat modal AJAX ke `create_skill_ajax`.
View ini tidak memakai kedua decorator di atas karena keduanya membalas
redirect atau halaman HTML, sementara pemanggilnya `fetch()` yang mengharapkan
JSON. Sebagai gantinya izin dicek di dalam view dengan
`request.user.has_perm("main.add_skill")`, dan pengunjung anonim maupun
pengguna tanpa izin sama-sama menerima `403` berisi pesan JSON.

---

## Progres Mingguan & Setup Tambahan
- Minggu 0: Setup dasar & Hero Section
1. Inisialisasi project Django, konfigurasi static/ dan templates/.
2. Membangun hero section (identitas, foto, bio, meta data, social links) dengan CSS Grid, konten disesuaikan dengan data pribadi.

- Minggu 1: Skills, Filter, Projects & Dokumentasi
1. Membangun Skills section dengan kategori dan sistem pill, memakai icon dari Devicon dan Simple Icons.

2. Menambahkan dropdown filter kategori skill menggunakan <select> + JavaScript.
3. Membangun Projects section dengan layout grid responsif.
4. Memisahkan JavaScript ke script.js, menambahkan komentar dokumentasi, dan menulis README.

- Minggu 2: Model, view, template, dan unit test
1. Menambahkan model Experience dan Project pada aplikasi main (lebih dari tiga field, UUID sebagai primary key, choices, dan @property untuk data turunan).
2. Membuat dan menerapkan migrasi (makemigrations + migrate), berkas migrasi ikut di-commit.
3. Membuat view show_main, show_experience, dan show_projects yang mengambil data dari model ke context, serta mendaftarkan named route pada main/urls.py.
4. Menampilkan objek dengan perulangan {% for %} dan {% empty %} untuk kondisi data kosong; navbar memakai {% url %}.
5. Mengekstrak layout bersama ke base.html (template inheritance) dan mengganti path /static/ hardcode dengan {% load static %} + {% static %}.
Menambahkan unit test yang mencakup akses URL + template, data muncul di HTML, dan pesan kondisi kosong.
6. Pengembangan di luar instruksi: mengelompokkan experience menjadi ongoing/past di view, dan membuat context processor untuk memusatkan data profil.

- Minggu 3: Form, ModelForm, dan Data Delivery
1. Menambahkan model `Skill` dan `SkillCategory` pada aplikasi main. Kategori dibuat sebagai model tersendiri, bukan `choices`, supaya pengguna bisa menambah kategori baru tanpa perlu migrasi lagi.
2. Memindahkan sekitar 30 skill yang tadinya hardcoded di `index.html` ke database lewat data migration. Tampilannya tetap sama persis, tapi sumber datanya sudah dinamis.
3. Membuat `SkillForm` (ModelForm) dengan empat field bertipe beda-beda (`CharField`, `ForeignKey`, `CharField`, `BooleanField`), plus field non-model `new_category` untuk membuat kategori langsung dari form.
4. Membuat view `create_skill`, `edit_skill`, `delete_skill`, dan `get_skills_json`, beserta halaman form create/update dan tombol delete.
5. Menampilkan data skill lewat deserialisasi JSON (`_categories_with_skills`), bukan query model langsung, supaya halaman HTML dan endpoint JSON pasti memakai sumber data yang sama.
6. Refactor `index.html`: sekitar 227 baris markup skill hardcoded diganti perulangan dari database, dan markup pill dipindah ke partial `components/skill_pill.html`.
7. Pengembangan di luar instruksi: auto-slug kategori dengan penanganan tabrakan nama, `on_delete=PROTECT`, filter kategori yang opsinya dirender dari database, flag `is_featured` dengan penanda visual, tombol aksi SVG dengan state `:hover` dan `:focus-visible`, serta perbaikan `django.contrib.messages` yang sebelumnya tidak pernah dirender di template mana pun.

- Minggu 4: Autentikasi, Otorisasi, dan Fitur Star
1. Menambahkan halaman register, login, dan logout memakai `UserCreationForm`
   dan `AuthenticationForm` bawaan Django, serta cookie `last_login` yang
   dipasang saat login dan dihapus saat logout.
2. Membuat peran Editor sebagai Django Group lewat halaman admin, memakai
   permission `add_skill` dan `change_skill` yang dibuat Django otomatis.
3. Menerapkan pembatasan akses di sisi server pada `create_skill`,
   `edit_skill`, dan `delete_skill` dengan `login_required` +
   `permission_required(raise_exception=True)`, sehingga pengunjung anonim
   diarahkan ke login sementara pengguna tanpa izin menerima 403.
4. Menyembunyikan tombol create, update, dan delete di `skill.html` memakai
   variabel `perms`.
5. Menambahkan `ManyToManyField` `starred_by` ke model `Skill` beserta
   migrasinya, dan view `toggle_skill_star` yang hanya menerima POST dengan
   `{% csrf_token %}`. Halaman menampilkan jumlah total star sekaligus status
   pengguna yang sedang login.
6. Menutup kebocoran data pada endpoint JSON: `get_skills_json` dan
   `get_projects_json` sekarang membatasi field yang diserialisasi, sehingga
   daftar pengguna pemberi star tidak ikut terekspos.
7. Pengembangan di luar instruksi: halaman 403 kustom, jumlah star dihitung
   sekali lewat query agregat supaya tidak menambah query per skill, dan
   tombol star memakai `aria-pressed` agar status toggle-nya terbaca screen
   reader.

- Minggu 5: AJAX, Fetch API, dan Keamanan Data di Sisi Klien
1. Mengubah `show_skills` agar hanya merender kerangka halaman. Daftar skill
   kini diambil lewat `fetch()` ke `/api/skills/` lalu dirender dengan
   JavaScript.
2. Menyusun ulang `get_skills_json` secara manual dengan `JsonResponse`. Data
   dikelompokkan per kategori dan tiap skill membawa `star_count` serta
   `is_starred` milik pengguna yang sedang login. Totalnya tetap tiga query
   berapa pun jumlah skill-nya.
3. Menampilkan tiga kondisi selama data dimuat: loading, data kosong, dan
   error saat request gagal.
4. Menambahkan pencarian skill berdasarkan nama lewat parameter `?name=`,
   dengan debouncing 300 ms sehingga request baru dikirim setelah pengguna
   berhenti mengetik.
5. Memindahkan form tambah skill ke dalam modal (`popover`) di halaman skill.
   View baru `create_skill_ajax` memvalidasi input dengan `SkillForm` dan
   membalas JSON berstatus `201`, `400`, atau `403`. Hak akses dicek di dalam
   view, dan token CSRF ikut terkirim lewat field `csrfmiddlewaretoken` di
   `FormData`.
6. Menampilkan toast saat skill berhasil ditambahkan maupun gagal, termasuk
   pesan validasi dari server lengkap dengan nama field yang salah.
7. Melakukan escaping pada setiap nilai teks yang disisipkan lewat
   `innerHTML` di `skill.html` dan `project.html`, serta membersihkan input
   dengan `strip_tags` di `clean_name`, `clean_icon`, dan
   `clean_new_category` pada `SkillForm`.
8. Menambahkan 9 unit test untuk `create_skill_ajax` (201, 400, 403, 405, dan
   penolakan request tanpa token CSRF) serta `get_skills_json` (info star per
   pengguna dan pencarian).
9. Pengembangan di luar instruksi: `AbortController` untuk membatalkan request
   lama supaya hasil yang telat datang tidak menimpa hasil terbaru, filter
   kategori yang tetap berlaku saat mencari maupun setelah data ditambahkan,
   dan pembersihan partial `skill_pill.html` serta `skill_star.html` yang tidak
   terpakai lagi.

## Pertanyaan Reflektif
### Tugas 1

1. Ya, saya menggunakan elemen semantik HTML5 seperti `<header>`, `<nav>`, `<main>`, `<section>`, dan `<footer>` untuk membagi struktur halaman menjadi tiga bagian utama: Profile, Skills, dan Projects (masing-masing dibungkus `<section>` dengan `id` sendiri). Elemen-elemen ini membantu saya membuat struktur halaman yang lebih jelas secara hierarki. Contohnya, `<nav>` langsung menandakan bagian navigasi ke pembaca kode maupun screen reader dan `<section id="skills">` memudahkan saya melakukan scroll-anchor lewat link di navbar (`href="#skills"`). Saya belum menggunakan `<article>` karena konten seperti kartu proyek belum berdiri sendiri sebagai konten yang bisa didistribusikan secara independen, jadi `<div class="project-card">` dirasa cukup. Saya juga belum memakai `<aside>` karena portofolio ini tidak punya konten pelengkap/sidebar yang terpisah dari alur utama.

2. Tantangan responsive yang paling terasa ada di section Skills dan Projects. Untuk section Skills, saya menggunakan `grid-template-columns: repeat(auto-fit, minmax(240px, 1fr))` supaya jumlah kolom kartu kategori otomatis menyesuaikan lebar layar tanpa perlu menulis media query untuk tiap breakpoint, tapi saya tetap perlu media query tambahan di 600px untuk memaksa 1 kolom penuh di mobile, karena `auto-fit` saja kadang masih menyisakan kolom yang terlalu sempit untuk menampung skill-pill. Saya juga harus mengatur `.skill-list` dengan `flex-wrap: wrap` supaya pill-pill skill tidak overflow keluar kartu saat kontainer menyempit. Untuk section Projects, tantangannya ada pada menyamakan tinggi kartu meski panjang deskripsi tiap proyek berbeda-beda. Saya memakai `display: flex; flex-direction: column` pada `.card-body` lalu `margin-top: auto` pada `.card-link`, sehingga tombol "View Project" dan ikon GitHub selalu menempel di bagian bawah kartu, sejajar antar kartu, apa pun panjang teksnya. Saya mengevaluasi prioritas ukuran dengan memberi `flex: 1` pada tombol utama (`.project-link`) dan ukuran tetap 44px pada ikon GitHub (`.github-link`), karena tombol utama harus lebih dominan secara visual dibanding ikon sekunder.

3. Karena situs ini murni statis, saya tidak bisa menyimpan atau memproses input apa pun secara konkret, seperti filter skill yang hanya bisa menyembunyikan/menampilkan elemen yang sudah ada di HTML, bukan mengambil data dari sumber lain. Menambah proyek baru juga berarti saya harus mengedit langsung kode HTML, bukan lewat semacam panel admin. Fungsionalitas dinamis yang paling ingin saya siapkan di iterasi berikutnya adalah backend sederhana menggunakan Django untuk menyimpan data proyek di database sehingga bisa diubah tanpa mengedit HTML manual.

### Tugas 2

1. Alur request saat pengguna membuka halaman portofolio baru
Ketika pengguna mengakses sebuah halaman (misalnya `/experience/`), urutan yang terjadi di proyek saya adalah sebagai berikut:
(a) `urls.py` proyek (project-level) menerima request pertama kali. File ini berfungsi mencocokkan URL masuk dengan daftar `urlpatterns`, lalu meneruskan (`include()`) bagian path yang cocok ke `urls.py` milik aplikasi `main`. Saya juga menambahkan `static(settings.MEDIA_URL, ...)` saat `DEBUG` agar file media (mis. `thumbnail` proyek) bisa diakses selama development.

(b) `urls.py` aplikasi (app-level `main/urls.py`) menerima *path* yang diteruskan lalu mencocokkannya dengan named route yang saya daftarkan. Misalnya, `path("experience/", show_experience, name="show_experience")`. Karena saya memakai `app_name = "main"`, setiap route punya namespace (`main:show_experience`) yang saya panggil di template lewat `{% url %}`. Setelah cocok, request diarahkan ke fungsi view yang bersangkutan.

(c) View (`views.py`) berisi logika bisnis. View seperti `show_experience` memanggil model untuk mengambil data (`Experience.objects.all().order_by(...)`), lalu saya pisahkan menjadi `ongoing_list` dan `past_list` berdasarkan properti `is_ongoing`. Data tersebut dimasukkan ke dalam sebuah dictionary bernama `context`.

(d) Model (`models.py`) adalah lapisan yang berinteraksi dengan database. Ketika view memanggil `Experience.objects.all()`, Django ORM menerjemahkannya menjadi query SQL, mengambil baris dari tabel, dan mengubahnya kembali menjadi objek Python. Model juga punya `@property` seperti `is_ongoing` dan `skills_list` yang menyediakan data turunan tanpa menyimpannya di database.

(e) Template (`.html`) menerima `context` dari view lewat fungsi `render()`. Di sini Django Template Language (DTL) mengubah data menjadi HTML final: perulangan `{% for %}` menampilkan tiap objek, `{% empty %}` menangani kondisi saat data kosong, dan `{% extends "base.html" %}` memastikan navbar/footer konsisten. HTML jadi inilah yang akhirnya dikirim balik sebagai response dan dirender oleh browser.

2. Mengapa data disimpan di model dan tidak ditulis langsung di template
- Kemudahan mengubah/menambah data -> jika data proyek ada di database, datanya cukup diubah di satu tempat (lewat admin atau ORM) dan semua halaman yang menampilkannya otomatis ikut ter-update. Sedangkan, jika di*hard-code* di HTML, harus mencari dan mengedit setiap kemunculannya secara manual.

- Pemisahan tanggung jawab -> model mengurus data, view mengurus logika, template mengurus tampilan. Jika data ditulis di template, ketiga tanggung jawab ini tercampur, sehingga kode lebih sulit dibaca dan dipelihara.

- Skalabilitas & fitur lanjutan -> Data di model bisa difilter, diurutkan (`order_by`), dikelompokkan (ongoing vs past), dipaginasi, atau dicari lewat ORM. Sedangkan, data yang di-*hard-code* di template tidak bisa diperlakukan seperti itu tanpa menulis ulang HTML.

- Menghindari duplikasi -> Dengan model tidak perlu menyalin-tempel *markup* yang sama berkali-kali pada banyak file.

3. Perbedaan `makemigrations` dan `migrate`
- `makemigrations` berfungsi membaca perubahan pada `models.py` kemudian membuat file migrasi yang merupakan *bluepint* yang mendeskripsikan *apa* yang berubah (menambah field, menghapus model, dll). 
- `migrate` berfungsi untuk mengeksekusi file migrasi tersebut ke database kemudian menerjemahkan instruksi di berkas migrasi menjadi perintah SQL yang sebenarnya (seperti `CREATE TABLE`, `ALTER TABLE`, dll) dan menerapkannya sehingga struktur tabel di database benar-benar berubah sesuai model.

Contoh perubahan model yang mengharuskan saya melakukan kedua perintah tersebut: 
Misalnya, pada model `Project` ingin ditambah field baru:

```python
thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
```
Setelah menyimpan perubahan itu, saya harus menjalankan kedua perintah:

1. `python manage.py makemigrations` -> dalam skenario ini, Django mendeteksi ada field `thumbnail` baru dan membuat berkas migrasi yang mendeskripsikan penambahan kolom tersebut.
2. `python manage.py migrate` -> dalam skenario ini, Django menjalankan berkas itu dan benar-benar menambahkan kolom `thumbnail` ke tabel database.

Tanpa `makemigrations`, perubahan model tidak tercatat sebagai migrasi. Tanpa `migrate`, database tetap memakai skema lama dan aplikasi bisa error karena model dan tabel tidak sinkron.

### Tugas 3

1. Mengapa memakai ModelForm dan mengapa `{% csrf_token %}` wajib ada
Alasan utamanya untuk menghindari duplikasi definisi field. Model `Skill` saya sudah mendeklarasikan `name` (maksimal 100 karakter), `category` (ForeignKey), `icon`, dan `is_featured`. Kalau form-nya saya tulis manual di HTML, definisi yang sama harus ditulis ulang minimal di tiga tempat: tag `<input>` di template, kode pembacaan `request.POST` di view, dan kode validasi panjang serta tipe datanya. Menambah satu field berarti mengedit tiga tempat, dan kalau ada yang kelewat, bug-nya baru ketahuan setelah data terlanjur masuk.

Dengan `ModelForm`, saya cukup menulis `model = Skill` dan `fields = ["name", "category", "icon", "is_featured"]`. Sisanya diturunkan Django sendiri:

- Widget otomatis -> `is_featured` yang bertipe `BooleanField` dirender jadi checkbox, dan `category` yang bertipe ForeignKey dirender jadi `<select>` berisi seluruh baris `SkillCategory`. Kalau manual, daftar opsi itu harus saya query dan susun sendiri.
- Validasi sisi server otomatis -> `max_length=100` pada `name` ditegakkan tanpa perlu saya tulis ulang. Untuk `category`, Django juga memastikan UUID yang dikirim memang ada di tabel kategori. Validasi ini penting karena atribut `maxlength` di HTML cuma menahan di browser dan gampang dilewati.
- Penyimpanan otomatis -> `form.save()` memetakan `cleaned_data` ke instance model. View saya jadi ringkas, dan yang lebih penting, `edit_skill` bisa memakai form yang sama persis cukup dengan menambahkan `instance=skill`. Satu kelas form melayani create sekaligus update.
- Field sensitif tetap terkendali -> saya menulis `fields` secara eksplisit, bukan `__all__`, jadi `id` dan `created_at` tidak ikut terekspos ke pengguna.

ModelForm juga tidak mengunci saya pada struktur model. Di `SkillForm` saya menambahkan `new_category`, field yang tidak ada di model Skill, lalu meng-override `clean()` supaya `SkillCategory` baru dibuat kalau field itu diisi. Jadi saya tetap dapat semua otomatisasi di atas sambil menambahkan perilaku khusus sendiri.

Mengapa `{% csrf_token %}` wajib

CSRF (Cross-Site Request Forgery) adalah serangan di mana situs lain membuat browser korban mengirim request ke aplikasi kita tanpa sepengetahuan korban. Masalahnya, browser otomatis melampirkan cookie sesi ke setiap request menuju domain tersebut, jadi dari sisi server request palsu itu kelihatan seperti datang dari pengguna yang sah.

Di proyek saya, view yang paling rawan adalah `delete_skill` dan `delete_project`. Keduanya menerima POST ke URL seperti `/skills/<uuid>/delete/`. Tanpa proteksi, halaman jahat bisa memasang form tersembunyi yang otomatis ter-submit ke URL itu dan menghapus data saya.

`{% csrf_token %}` merender `<input type="hidden" name="csrfmiddlewaretoken" value="...">`. `CsrfViewMiddleware` lalu membandingkan nilai itu dengan token pada cookie pengguna, dan menolak request kalau tidak cocok. Situs penyerang tidak bisa membaca nilai token tersebut karena terhalang same-origin policy browser, jadi dia tidak bisa menyusun request palsu yang lolos. Kalau tag ini lupa dipasang, Django membalas `403 Forbidden`, bukan diam-diam menerima.

Sebagai lapisan tambahan, view delete saya sengaja cuma mengeksekusi penghapusan kalau `request.method == "POST"`. Request GET hanya diarahkan balik tanpa efek apa pun. Alasannya, URL yang bisa dipicu lewat GET gampang tereksekusi tanpa sengaja oleh prefetch browser, crawler, atau sekadar link yang tertempel di suatu tempat.

2. Mengapa JSON lebih disukai dibanding XML
- Pemetaan langsung ke struktur data bawaan -> objek JSON jadi `dict` di Python dan object di JavaScript, array jadi `list`. XML menghasilkan pohon node yang harus ditelusuri manual, dan seluruh isinya berupa string sehingga angka maupun boolean perlu dikonversi sendiri. Pada respons `/api/skills/` saya, `"is_featured": false` langsung terbaca sebagai boolean. Di XML nilainya akan jadi teks `"False"` yang masih harus diterjemahkan.
- Parsing sudah tersedia tanpa tambahan apa pun -> di sisi klien cukup `response.json()`, di sisi Python cukup `json.loads()`. Untuk XML masih perlu `DOMParser` atau pustaka tersendiri plus kode penelusuran node.
- Ukuran lebih kecil -> XML mengulang nama setiap field dua kali, di tag pembuka dan penutup. Untuk data yang dikirim berulang kali lewat jaringan, selisihnya terasa.
- Cocok dengan cara kerja web modern -> API dan komunikasi antar-service umumnya berbicara dalam JSON, jadi memilih JSON berarti ikut ekosistem yang sudah jadi standar.

Meski begitu, XML tidak lantas usang. XML unggul kalau dokumen butuh validasi skema ketat (XSD), namespace, atribut di samping isi elemen, atau dokumen dengan teks campuran seperti format `.docx`. Untuk kebutuhan proyek ini, yaitu mengirim daftar objek sederhana dari server ke halaman web, JSON jelas lebih tepat. Django sendiri menyediakan keduanya lewat `serializers.serialize("json", ...)` maupun `("xml", ...)`, dan saya memilih JSON karena alasan-alasan di atas.

3. Alur view mengembalikan data JSON dan mengapa perlu serialization
Alur yang terjadi saat `/api/skills/` diakses

(a) `portfolio_config/urls.py` menerima request, mencocokkan prefix, lalu meneruskannya ke `main/urls.py` lewat `include()`.

(b) `main/urls.py` mencocokkan path dengan `path("api/skills/", get_skills_json, name="get_skills_json")` dan memanggil view tersebut.

(c) `get_skills_json` menjalankan `Skill.objects.all()`. Django ORM menerjemahkannya jadi query SQL, mengambil baris dari tabel, lalu membungkus tiap baris jadi objek `Skill` di memori Python. Urutannya mengikuti `Skill.Meta.ordering`.

(d) `serializers.serialize("json", ...)` mengubah objek-objek Python tadi jadi satu string JSON berformat `"model"`, `"pk"`, dan `"fields"`.

(e) String itu dibungkus `HttpResponse(..., content_type="application/json")`. Header `content_type` inilah yang memberi tahu penerima bahwa isi respons harus diperlakukan sebagai JSON, bukan HTML.

Untuk halaman HTML-nya, alurnya berlanjut satu tahap lagi. `_categories_with_skills` memanggil `get_skills_json` di dalam proses yang sama, lalu `serializers.deserialize` mengubah string JSON itu balik jadi instance `Skill` (diakses lewat atribut `.object` tiap wrapper), baru dikelompokkan per kategori dan dikirim ke template. Karena itu halaman dan endpoint dijamin menampilkan data yang sama.

Mengapa perlu serialization

Objek `Skill` adalah objek Python yang hidup di memori: punya method, punya atribut internal seperti `_state`, dan punya descriptor untuk relasi. HTTP cuma bisa mengangkut teks atau byte, jadi objek semacam itu mustahil dikirim apa adanya. Serialization adalah proses menerjemahkannya jadi representasi tekstual yang bisa melintasi jaringan.

Memanggil `json.dumps()` langsung pada objek model pun akan gagal, karena objek model bukan tipe yang dikenali JSON. Selain itu ada beberapa tipe field yang memang tidak punya padanan di JSON, dan serializer Django yang menanganinya. Ini kelihatan jelas pada respons saya:

- `pk` berupa UUID diubah jadi string `"c8a2a9a0-ffd5-4fd0-a387-f5a38bde13fb"`, karena JSON tidak mengenal tipe UUID.
- `created_at` berupa `datetime` diubah jadi string ISO 8601 `"2026-09-20T09:05:12.898Z"`.
- `category` yang merupakan ForeignKey diubah jadi UUID kategori terkait, bukan objek kategori yang tersarang. Karena itulah `_categories_with_skills` mengelompokkan datanya memakai `skill.category_id`, bukan `skill.category`.

Alasan terakhir soal kontrak antar sistem. Hasil serialization tidak terikat pada Python, jadi penerimanya bisa JavaScript di browser, aplikasi mobile, atau layanan lain dalam bahasa apa pun. Format objek Python cuma bisa dimengerti Python, sedangkan JSON bisa dimengerti semuanya.

### Tugas 5

1. Apa itu debouncing dan mengapa penting untuk pencarian AJAX
Debouncing adalah teknik menunda eksekusi sebuah fungsi sampai event pemicunya berhenti terjadi selama jeda waktu tertentu. Setiap kali event baru muncul sebelum jeda itu habis, hitungan waktunya diulang dari nol. Fungsinya baru benar-benar jalan sekali, yaitu setelah pengguna diam.

Di halaman skill saya, penerapannya ada pada event `input` di kotak pencarian:

```js
let searchTimer;
document.getElementById('skill-search').addEventListener('input', function (e) {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => fetchSkills(e.target.value.trim()), 300);
});
```

Setiap ketikan membatalkan timer sebelumnya lewat `clearTimeout`, lalu memasang timer baru 300 ms. Request ke `/api/skills/?name=...` baru dikirim kalau dalam 300 ms tidak ada ketikan lagi.

Alasan teknik ini penting:
- Mengurangi jumlah request -> tanpa debouncing, mengetik "python" memicu enam request (`p`, `py`, `pyt`, dan seterusnya), padahal yang dibutuhkan pengguna hanya hasil untuk kata lengkapnya. Dengan debouncing, kalau diketik lancar, yang terkirim cukup satu request.
- Mengurangi beban server dan database -> tiap request menjalankan query `name__icontains` ke database. Request yang hasilnya langsung dibuang tetap memakan kerja server, dan bebannya berlipat kalau penggunanya banyak.
- Tampilan lebih stabil -> tiap request memicu kondisi loading lalu merender ulang daftar. Tanpa debouncing, halaman berkedip di setiap ketikan.
- Memperkecil peluang race condition -> request tidak dijamin selesai sesuai urutan kirimnya. Kalau request untuk `py` ternyata selesai setelah request untuk `python`, hasil yang lebih lama akan menimpa hasil yang lebih baru. Debouncing memperkecil peluang ini karena request yang terkirim lebih sedikit, tapi tidak menghilangkannya sepenuhnya. Karena itu saya juga memakai `AbortController` untuk membatalkan request lama setiap kali request baru dikirim.

Angka 300 ms saya pilih sebagai kompromi. Jeda yang terlalu pendek membuat debouncing hampir tidak berpengaruh, sedangkan jeda yang terlalu panjang membuat pencarian terasa lambat merespons.

2. Fungsi `await` saat memakai `fetch()` dan apa yang terjadi tanpanya
`fetch()` bersifat asinkron. Fungsi ini tidak langsung mengembalikan respons dari server, melainkan sebuah `Promise`, yaitu janji bahwa respons akan tersedia nanti setelah request selesai. `await` membuat fungsi `async` berhenti di baris itu sampai `Promise` tersebut selesai, lalu mengembalikan isinya, yaitu objek `Response`. Hal yang sama berlaku untuk `response.json()`, yang juga mengembalikan `Promise` karena isi respons dibaca secara bertahap dari jaringan.

```js
const response = await fetch(url, { signal: skillsAbortController.signal });
if (!response.ok) throw new Error('Failed to fetch skills');
const categories = await response.json();
```

`await` hanya menghentikan fungsi `fetchSkills` itu sendiri, bukan seluruh browser. Selama menunggu respons, halaman tetap bisa di-scroll dan diklik. Inilah yang membedakannya dari request sinkron yang membekukan halaman.

Kalau `await` dihilangkan, beberapa hal akan rusak:
- `response` berisi objek `Promise`, bukan `Response`. Properti `response.ok` bernilai `undefined`, sehingga `!response.ok` bernilai `true` dan kode langsung melempar error padahal request-nya mungkin berhasil. Pengguna akan melihat pesan "Gagal memuat data" setiap kali halaman dibuka.
- Kalau pengecekan `ok` dilewati, `response.json` juga tidak ada di objek `Promise`, sehingga muncul `TypeError: response.json is not a function`.
- Kalau hanya `await` pada `response.json()` yang dihilangkan, `categories` berisi `Promise`. Pemanggilan `categories.every(...)` dan `categories.map(...)` akan gagal karena `Promise` bukan array.
- Error dari request yang gagal tidak lagi tertangkap `try...catch`, karena `catch` hanya menangkap penolakan `Promise` yang di-`await`. Akibatnya muncul *unhandled promise rejection* di console, dan kondisi error di halaman tidak pernah tampil.
- Kode setelah `fetch()` berjalan sebelum data tiba. Misalnya `show('grid')` dijalankan duluan sehingga yang tampil adalah daftar kosong.

Alternatif dari `await` adalah rantai `.then()`. Hasilnya sama, tapi `async`/`await` membuat alur asinkron bisa ditulis dan dibaca dari atas ke bawah seperti kode biasa, dan error-nya cukup ditangani dengan `try...catch`.

3. Apa itu XSS dan mengapa data lewat AJAX/JavaScript lebih rentan dibanding template Django
XSS (Cross-Site Scripting) adalah serangan di mana penyerang menyisipkan kode, biasanya JavaScript, ke dalam halaman yang nantinya dibuka oleh pengguna lain. Karena kode itu berjalan di dalam domain situs kita, browser memperlakukannya seperti kode milik situs sendiri. Kode tersebut bisa membaca isi halaman termasuk token CSRF, mengirim request atas nama korban memakai sesi login-nya, mengubah tampilan untuk menipu pengguna, atau mengarahkan korban ke situs lain.

Yang relevan dengan proyek saya adalah *stored XSS*. Contohnya, seseorang yang punya akses tambah skill mengisi nama skill dengan `<img src=x onerror="alert(document.cookie)">`. Nilai itu tersimpan di database, lalu dikirim ke setiap pengunjung halaman skill lewat `/api/skills/`. Kalau ditampilkan apa adanya, browser semua pengunjung akan menjalankan skrip tersebut.

Mengapa data lewat JavaScript lebih rentan:
- Template Django melakukan auto-escaping secara default. Setiap `{{ skill.name }}` otomatis diubah dulu, misalnya `<` menjadi `&lt;`, sebelum masuk ke HTML. Developer harus sengaja mematikannya (`|safe` atau `{% autoescape off %}`) supaya data bisa berubah jadi tag. Jadi kondisi bawaannya aman.
- Data dari AJAX tidak pernah melewati template engine. JSON dari `/api/skills/` langsung diterima JavaScript, lalu disusun jadi HTML memakai template literal dan dimasukkan lewat `innerHTML`. Baik template literal maupun `innerHTML` tidak melakukan escaping apa pun. Kondisi bawaannya justru tidak aman, sehingga developer harus ingat melakukan escaping di setiap nilai yang disisipkan. Satu nilai yang terlewat sudah cukup untuk membuka celah.
- Ini benar terjadi di proyek saya. Waktu mengaudit kode, ternyata `project.html` memasukkan `project.title`, `project.description`, dan `project.project_url` ke `innerHTML` tanpa escaping sama sekali. Halaman skill sudah aman, tapi halaman project masih bolong. Yang terakhir ketemu adalah `project_url` di atribut `href`, satu baris yang terlewat dari perbaikan sebelumnya.

Cara saya menanganinya:
- Di sisi klien, saya memakai helper `esc()` yang mengubah lima karakter berbahaya (`& < > " '`) menjadi entitas HTML, lalu membungkus setiap nilai teks dari server dengannya. Untuk teks yang tidak butuh markup, seperti pesan toast dan pesan "Tidak ada skill dengan nama ...", saya memakai `textContent`, yang selalu memperlakukan isinya sebagai teks biasa.
- Di sisi server, `SkillForm` membersihkan input dengan `strip_tags` di `clean_name`, `clean_icon`, dan `clean_new_category`, sehingga tag HTML tidak sempat tersimpan ke database.

Kedua lapisan ini tetap saya pakai bersamaan. `strip_tags` hanya membersihkan data yang masuk lewat form, sementara data lama atau data yang masuk lewat jalur lain seperti halaman admin tidak ikut dibersihkan. Karena itu escaping di sisi klien tetap dibutuhkan sebagai pertahanan terakhir tepat sebelum data ditampilkan.

## AI Disclosure
### Tugas 1
Saya menggunakan Claude (Anthropic) sebagai asisten belajar selama mengerjakan Tugas 1, dengan strategi utama yaitu meminta penjelasan konsep dan hint/referensi terlebih dahulu untuk kemudian dicoba dikulik dan diketik kodenya sendiri.  

Bagian yang dibantu AI:
- Penjelasan konsep struktur HTML semantik (kenapa memilih `<div>` dibanding `<article>` untuk kartu proyek)
- Penjelasan CSS Grid (`grid-template-areas`, `grid-template-columns`, `clamp()`) yang saya terapkan ke `.hero-grid` dan `.project-grid`
- Penjelasan pola `repeat(auto-fit, minmax(...))` untuk membuat grid skill & project otomatis responsive
- Saat membangun fitur filter skill dengan JavaScript, saya secara eksplisit meminta AI memberi hint dan referensi per bagian struktur alih-alih kode utuh langsung pakai
- Merapikan `script.js` menjadi file terpisah dari HTML dan menambahkan komentar dokumentasi
- Membuat draf awal deskripsi proyek, cara setup proyek, dan deskripsi progres mingguan
- Debugging

Keterbatasan AI: AI tidak tahu bagian mana dari kode saya yang asli buatan sendiri vs hasil contoh tutorial kecuali saya beri tahu, jadi saya perlu mengoreksi draf refleksi secara manual agar jujur mencerminkan proses belajar saya.

Log chat AI: https://claude.ai/share/705f637e-bd3a-49ee-9412-0a979b428e72

### Tugas 2
Saya memakai Claude (Anthropic) lewat claude.ai sebagai asisten belajar selama Tugas 2. Strategi prompting yang saya pakai: menempelkan instruksi dan checklist tugas ke prompt supaya sarannya tidak melenceng, meminta penjelasan alur request dari `urls.py` sampai template dulu sebelum minta kode, lalu menyusun kodenya sendiri dan minta AI me-review hasilnya. Untuk `tests.py` saya tidak langsung pakai draf AI, melainkan saya cocokkan dulu dengan checklist dan minta revisi untuk kasus yang belum tercover.

Bagian yang dibantu AI:

- Pembuatan draf jawaban ketiga pertanyaan reflektif berdasarkan rubrik dan instruksi Tugas 2
- Review kecocokan antara model, view, urls.py, dan template terhadap checklist tugas
- Refactor layout bersama ke base.html dengan template inheritance dan mengganti path /static/ hardcode menjadi {% load static %} + {% static %}
- Menambahkan null-guard pada script.js agar tidak error di halaman tanpa elemen #skill-filter
- Menambahkan guard {% if %} dan rel="noopener" pada tautan proyek
- Perbaikan CSS sticky header dan warna badge status
- Pengelompokan data experience menjadi ongoing dan past di view (ongoing_list / past_list)
- Pembuatan context processor untuk memusatkan data profil (name) agar tidak diulang di tiap view
- Penyusunan tests.py yang mencakup akses URL + template, data muncul di HTML, dan pesan kondisi kosong
- Penyusunan commit message dan struktur README ini
- Membuat draf awal deskripsi proyek, cara setup proyek, dan deskripsi progres mingguan
- Debugging

Keterbatasan AI: draf test dari AI awalnya tidak sesuai instruksi, sehingga saya cocokkan manual dengan checklist tugas, cari kasus yang belum tercover, lalu minta untuk kembali direvisi dan diverifikasi.

Log chat AI: https://claude.ai/share/2ab69e56-a51f-4707-b00c-f920fd841191, hhttps://claude.ai/share/9d5bfe8b-266d-4db3-b64c-e9e756f1ddf7

### Tugas 3
Saya memakai Claude (Anthropic) lewat Claude Code di terminal sebagai asisten selama Tugas 3. Strategi prompting yang saya pakai: menyuruh AI membaca kode yang sudah ada dulu sebelum menyarankan apa pun, meminta satu perubahan kecil per prompt supaya gampang saya review, dan menanyakan alasan di balik tiap saran desain model (misalnya kenapa `on_delete=PROTECT` dan bukan `CASCADE`) sebelum kodenya saya pakai. Tiap keluaran AI tetap saya baca ulang dan cocokkan dengan checklist tugas, dan yang tidak cocok saya revert atau perbaiki manual seperti tercatat di bagian keterbatasan di bawah.

Bagian yang dibantu AI:

- Review kecocokan kode terhadap checklist tugas, termasuk memeriksa ulang bahwa seluruh berkas HTML sudah extend dari `base.html`
- Perancangan model `Skill` dan `SkillCategory`, termasuk saran `on_delete=PROTECT` dan auto-slug dengan penanganan tabrakan nama
- Penyusunan data migration untuk memindahkan sekitar 30 skill hardcoded dari `index.html` ke database
- Penyusunan `SkillForm`, termasuk pola field non-model `new_category` untuk membuat kategori langsung dari form
- Penyusunan view `create_skill`, `edit_skill`, `delete_skill`, `get_skills_json`, dan helper `_categories_with_skills`
- Styling CSS untuk `<select>`, checkbox, pesan `messages`, serta tombol aksi SVG
- Penyusunan docstring pada `models.py` dan `forms.py`
- Pembuatan draf jawaban ketiga pertanyaan reflektif
- Penyusunan commit message dan struktur README ini
- Debugging

Keterbatasan AI dan perbaikan manual yang saya lakukan:

- AI mengerjakan yang tidak diminta. Waktu saya cuma minta pemeriksaan checklist, AI malah langsung menambahkan view update beserta URL dan template-nya. Saya minta perubahan itu di-revert dan mengambil kembali kontrol soal kapan kode ditulis.
- AI tidak membedakan kode tutorial dan kode buatan sendiri. AI awalnya menyimpulkan checklist sudah terpenuhi karena mencocokkannya dengan `ProjectForm`, padahal `Project` berasal dari tutorial. Saya yang mengoreksi bahwa "bagian yang dipilih" seharusnya bagian buatan saya sendiri, dan dari situ arah pengerjaan berpindah ke Skills.
- Perancangan awal AI belum memeriksa data asli. AI memperkirakan icon cuma ada dua bentuk (devicon dan emoji), padahal setelah markup asli dibaca ternyata ada empat (tambahan `<img>` dari CDN eksternal dan skill tanpa icon). `Meta.ordering` yang disarankan AI juga memakai `-proficiency`, yang membuat urutan pill berubah dari susunan asli, jadi saya ganti ke `created_at`.
- AI menambahkan field yang tidak terpakai. Field `proficiency` dan `is_featured` ditambahkan cuma demi memenuhi syarat "tipe data bervariasi", tapi tidak pernah dirender di view mana pun. Saya menemukannya waktu review, lalu minta `proficiency` dihapus dan `is_featured` diberi penanda visual supaya benar-benar berfungsi.
- Import ganda tertinggal, dua kali. Waktu menambahkan view dan form baru, AI menulis baris import baru tanpa memeriksa yang sudah ada, sehingga `views.py` sempat gagal dijalankan dan `forms.py` punya import kembar. Saya menemukannya waktu audit kualitas kode.
- Instruksi AI beberapa kali ambigu sampai merusak template. Potongan kode yang diberikan tidak menyebut batas baris yang harus diganti, sehingga `skill.html` sempat punya tag `{% for %}` ganda dan `skills_form.html` sempat menaruh `<h1>` serta tombol submit di dalam `{% block meta %}`. Akibatnya tombol tampil menempel di pojok kiri atas halaman.
- Docstring buatan AI memuat klaim yang tidak benar. Docstring `SkillForm.clean()` menyebut kategori yatim bisa dihapus lewat admin, padahal `Skill` dan `SkillCategory` belum didaftarkan di `admin.py`. Saya mendaftarkannya supaya klaim itu jadi benar.
- Masalah environment yang saya diagnosa sendiri. Folder proyek berada di dalam OneDrive, dan itu dua kali merusak isi repositori: object git hilang sehingga `git commit` gagal dengan `invalid object`, dan dua berkas gambar di `static/img/` terhapus sendiri. Saya memulihkannya lewat `git hash-object -w`, `git fetch --refetch`, dan `git restore`.

Log chat AI: https://drive.google.com/file/d/1m4IWbC-5gKajS-YXYvwKnYW784G-qY-j/view?usp=sharing 

### Tugas 4
Saya memakai Claude (Anthropic) lewat Claude Code di terminal. Strategi
prompting yang saya pakai: menempelkan instruksi tugas beserta rubrik
penilaiannya ke prompt, lalu meminta walkthrough bertahap alih-alih kode jadi,
supaya seluruh kodenya tetap saya ketik sendiri dan saya paham tiap
perubahannya. Saya juga meminta pesan commit per perubahan kecil, bukan satu
commit besar di akhir.

Bagian yang dibantu AI:

- Audit riwayat git untuk menemukan perubahan yang tidak disengaja
- Rancangan urutan pengerjaan dan pemecahan tiap fase menjadi commit terpisah
- Pola `login_required` + `permission_required(raise_exception=True)` beserta
  alasan urutannya
- Penemuan kebocoran `starred_by` pada endpoint JSON dan cara menutupnya
- Optimasi perhitungan jumlah star agar tidak menimbulkan query per skill
- Penyusunan docstring, pesan commit, dan struktur README ini

Keterbatasan AI dan perbaikan manual yang saya lakukan:

- AI menemukan bahwa link navigasi `Skills` hilang dari `base.html`, tapi
  penyebabnya juga dari sesi AI sebelumnya: perubahan fungsional (menambah
  menu login/register) dicampur dengan reindentasi seluruh berkas dalam satu
  commit, sehingga satu baris yang terhapus tidak kelihatan di diff. Saya
  memulihkannya dan memisahkannya jadi commit tersendiri.
- AI memberi potongan CSS yang duplikat dengan isi `style.css` yang sudah ada.
  Aturan `.star-count` jadi tertulis dua kali dan `.skill-star-form` ternyata
  sama persis dengan `.skill-action-form` yang sudah dipakai. Saya menemukannya
  waktu membuka file CSS-nya, lalu minta diganti dengan aturan yang hanya
  menambal selisihnya.
- Rencana awal AI menyasar model `Project` karena saya belum menyebutkan bahwa
  fitur minggu ini harus diterapkan ke bagian Skills. Setelah saya perjelas,
  rencananya harus disusun ulang.
- Saya salah mengetik nama permission menjadi `main.edit_skill`, padahal Django
  membuat `main.change_skill`. Bug ini tidak memunculkan error apa pun —
  superuser tetap bisa mengedit karena punya seluruh izin secara otomatis, dan
  yang rusak hanya peran Editor. AI menemukannya waktu saya minta pengecekan
  status pengerjaan.

Log chat AI: https://drive.google.com/file/d/1bAEosbTQq-A5bJtaMFcPdzXDDB1KhoyJ/view?usp=sharing

### Tugas 5
Saya memakai Claude (Anthropic) lewat Claude Code di terminal. Strategi
prompting yang saya pakai: menempelkan poin instruksi tugas satu per satu,
meminta penjelasan cara mengerjakannya beserta contoh kode yang disesuaikan
dengan kode saya yang sudah ada, lalu menerapkannya sendiri. Setelah tiap
poin selesai saya meminta pesan commit tersendiri, dan di akhir saya
menempelkan rubrik penilaian untuk mengaudit apakah semua kriteria sudah
terpenuhi.

Bagian yang dibantu AI:

- Rancangan `get_skills_json` yang disusun manual dengan `JsonResponse`,
  termasuk cara menghitung star tanpa query per skill
- Kerangka halaman skill beserta fungsi render, kondisi loading/kosong/error,
  dan helper `esc()`
- Pola debouncing dan `AbortController` untuk pencarian
- View `create_skill_ajax`, modal tambah skill, dan pengiriman token CSRF
  lewat `FormData`
- Debugging layout dan filter kategori yang rusak setelah data dirender lewat
  JavaScript
- Penyusunan unit test untuk view AJAX dan endpoint JSON
- Audit kode terhadap rubrik penilaian
- Pembuatan draf jawaban ketiga pertanyaan reflektif
- Penyusunan pesan commit dan struktur README ini

Keterbatasan AI dan perbaikan manual yang saya lakukan:

- Kode awal dari AI membungkus seluruh kategori skill dalam satu
  `<div id="skill-container">` tanpa memperhitungkan bahwa grid tiga kolom
  dipasang di elemen induknya. Akibatnya semua kategori menumpuk jadi satu
  kolom sempit. Saya melaporkannya, lalu masalahnya diperbaiki dengan
  `display: contents`.
- AI awalnya juga tidak memperhitungkan bahwa `script.js` mencari elemen
  `.skill-category` sekali saja saat halaman dimuat. Karena data baru muncul
  setelah `fetch()` selesai, filter kategori jadi tidak berfungsi sampai
  pencariannya dipindah ke dalam handler `change`.
- Instruksi AI untuk menaruh kotak pencarian "di bawah `<select>`" ambigu,
  sehingga input sempat masuk ke dalam elemen `<select>`. Browser lalu
  menutup `<select>` lebih awal dan dropdown filter jadi kosong. Bug ini
  ketemu waktu saya minta pengecekan.
- Kode JavaScript dari AI memakai tag Django `{{ ... }}` langsung sebagai
  nilai boolean, yang ditandai error oleh VS Code. Saya menggantinya dengan
  pola perbandingan string yang sudah saya pakai di `project.html`.
- Nama berkas modal yang saya buat (`skills_form_modal.html`) berbeda dengan
  nama yang di-include di template (`skill_form_modal.html`). AI menemukannya
  waktu saya meminta pesan commit, sebelum sempat menyebabkan error di
  halaman.
- Waktu memeriksa tampilan lewat browser, AI sempat tertipu oleh berkas CSS
  versi lama yang masih tersimpan di cache, sehingga perbaikan yang
  sebenarnya sudah berhasil terlihat seperti belum berpengaruh.

Log chat AI: https://drive.google.com/file/d/1mdrtWDa34Tm1raVyu_LBwfNKOoSMmBEF/view?usp=sharing

