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
