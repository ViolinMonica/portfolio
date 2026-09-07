# Nama: Violin Monica  
# Kelas: PBP B  
# NPM: 2506551794 
# Portfolio Website

Portfolio pribadi yang menampilkan profil, skill, dan proyek yang pernah saya kerjakan. Dibangun sebagai tugas mata kuliah Pemrograman Berbasis Platform (PBP) dengan struktur halaman statis (HTML/CSS/JS) yang di-serve lewat Django.

## Tech Stack
- HTML5 & CSS3 (custom, tanpa framework CSS)
- JavaScript vanilla (fitur filter skill)
- Django (serving static files)
- Font: Space Grotesk (Google Fonts), ikon: Devicon & Simple Icons

## Setup & Menjalankan Proyek
### Prasyarat
- Python 3.x
- pip
- Git

### Langkah instalasi
```bash
# 1. Clone repository
git clone https://github.com/ViolinMonica/portfolio.git
cd portfolio

# 2. Buat virtual environment (opsional tapi disarankan untuk menghindari konflik versi)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Jalankan development server
python manage.py runserver
```

Buka `http://127.0.0.1:8000` di browser.

## Struktur Folder (ringkas) 
portfolio/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── portfolio/          # konfigurasi utama Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── views.py
│   ├── asgi.py
│   └── __init__.py
│                    
├── templates/         
│ └── index.html       # markup halaman portofolio
│
└── static/
    ├── css/
    │   └── style.css             # seluruh styling halaman
    ├── js/
    │   └── script.js             # logic dropdown filter skill
    └── img/
        ├── profile.jpg
        ├── nusa-crop.png
        ├── portofolio.png
        └── bobol.png

## Deployment
Live di: https://violin-monica-portofolio.pws.cs.ui.ac.id

---

## Progres Mingguan & Setup Tambahan
### Minggu 0 — Setup dasar & Hero Section *(adaptasi tutorial)*
- Inisialisasi project Django, konfigurasi `static/` dan `templates/`
- Membangun struktur `hero` section (identitas, foto, bio, meta data, social links) menggunakan CSS Grid dengan `grid-template-areas`, mengikuti pola dari tutorial yang dijadikan referensi
- Konten (foto profil, bio, data NPM/Program, link sosial) disesuaikan dengan data pribadi

### Minggu 1 — Skills, Filter, Projects & Dokumentasi *(dikerjakan mandiri)*

#### Perbaikan icon di Social Links (Hero)
- **Kendala:** icon GitHub, LinkedIn, dan Gmail pada `social-links` tidak terlihat karena berwarna gelap/biru di atas background gelap (`--ink`). Penyebabnya class `colored` pada devicon memaksa icon memakai warna resmi brand (hitam untuk GitHub, biru untuk LinkedIn), alih-alih mengikuti warna teks di sekitarnya.
- **Solusi:** menghapus class `colored` dari icon GitHub dan LinkedIn — tanpa class itu, icon devicon (yang sebenarnya adalah font icon, bukan gambar) otomatis mengikuti `color` yang berlaku di elemen induknya (`var(--paper)`, putih). Untuk icon Gmail (berbentuk `<img>`, bukan font icon, sehingga tidak bisa mengikuti `currentColor`), warna diatur manual lewat parameter URL CDN Simple Icons (`/faf6ee`).

#### Skills Section — kategori & perbaikan icon
- Menambahkan kategori skill (`skill-category`) dengan sistem pill (`skill-pill`) menggunakan Flexbox, serta integrasi icon dari Devicon (font icon) dan Simple Icons (image-based)
- **Kendala 1:** icon Figma dan dua pill setelahnya (Graphic Design, Painting) tiba-tiba tampil dengan font serif/italic yang tidak konsisten dengan pill lain.
- **Solusi 1:** akar masalahnya adalah tag `<i class="devicon-figma-plain-colored">` yang tidak ditutup dengan `</i>`. Browser otomatis "membawa" efek formatting tag yang tidak ditutup ke elemen-elemen sibling setelahnya sampai parser menemukan penutupnya secara paksa — sehingga pill setelah Figma ikut terkena efek tersebut. Selain itu, nama class-nya salah (`devicon-figma-plain-colored` seharusnya dua class terpisah: `devicon-figma-plain colored`).
- **Kendala 2:** beberapa icon devicon tidak muncul sama sekali: Visual Studio Code (`devicon-vsCode`) dan Robot Operating System (`devicon-ros-plain`).
- **Solusi 2:** untuk VS Code, nama class yang benar adalah `devicon-vscode-plain` (huruf kecil semua + akhiran versi) — devicon bersifat *case-sensitive* dan tidak mengenali `devicon-vsCode`. Untuk ROS, ternyata devicon hanya menyediakan varian `-original`, bukan `-plain`, sehingga class yang benar adalah `devicon-ros-original`.
- **Kendala 3:** beberapa icon tools keamanan siber (Nmap, Ghidra) memakai `<img>` yang di-*hotlink* langsung dari domain eksternal (`nmap.org`, `media.defense.gov`), yang berisiko diblokir oleh proteksi hotlink pada server tersebut.
- **Solusi 3:** untuk icon yang tersedia di Simple Icons (Burp Suite, Wireshark), tetap memakai CDN tersebut karena memang didesain untuk dipakai publik. Untuk sumber lain yang rawan, direkomendasikan meng-host file logo sendiri di folder `static/img/` alih-alih hotlink langsung.

#### Filter Interaktif Skill
- Menambahkan dropdown filter kategori skill menggunakan `<select>` + JavaScript (`querySelector`, `querySelectorAll`, `addEventListener`, `dataset`)
- **Kendala 1:** dropdown filter tidak berfungsi sama sekali — memilih kategori apapun tidak menyembunyikan/menampilkan card manapun.
- **Solusi 1:** tag `<script>` awalnya diletakkan tepat setelah `<body>` dibuka, sebelum elemen `<select id="skill-filter">` dan `.skill-category` dibaca browser. Karena HTML dieksekusi berurutan dari atas ke bawah, `document.querySelector("#skill-filter")` mengembalikan `null` saat script dijalankan, sehingga `addEventListener` gagal dan seluruh script berhenti tanpa pernah terpasang. Diperbaiki dengan membungkus seluruh logic dalam `document.addEventListener("DOMContentLoaded", ...)`, memastikan script berjalan setelah seluruh HTML selesai dimuat.
- **Kendala 2:** grid layout skill section berantakan — `.section-header` (judul + dropdown) ikut menyempit seperti satu kotak `.skill-category`, bukan melebar penuh di atasnya.
- **Solusi 2:** karena `display: grid` diterapkan ke `.container`, semua elemen anak langsung di dalamnya (termasuk `.section-header`) otomatis diperlakukan sebagai satu item grid. Ditambahkan `grid-column: 1 / -1` pada `.section-header` agar selalu melebar penuh menutupi seluruh kolom grid, berapa pun jumlah kolom yang dihasilkan `auto-fit`.

#### Projects Section
- Membangun `project-card` dengan layout grid responsive (`repeat(auto-fit, minmax(...))`)
- **Kendala:** gambar mockup tidak tampil, dan tombol "View Project" beserta icon GitHub tidak proporsional.
- **Solusi:** ditemukan tiga bug terpisah — (a) `src` gambar sempat mengarah ke URL halaman Wikipedia, bukan file gambar asli; (b) class pembungkus gambar sempat ditulis sebagai tiga class terpisah `class="card image wrap"`, tidak cocok dengan selector CSS `.card-image-wrap`; (c) belum ada styling untuk `.card-link` sehingga tombol dan icon (elemen `<a>`, defaultnya *inline*) tidak bisa diatur ukuran/jaraknya dengan baik. Ketiganya diperbaiki dengan mengoreksi path gambar, menyatukan nama class, dan menambahkan `display: flex` beserta ukuran tetap pada `.github-link`.

#### Refactoring & Dokumentasi
- Memisahkan kode JavaScript dari inline `<script>` di HTML ke file `script.js` terpisah, tetap dibungkus `DOMContentLoaded` agar konsisten berjalan di posisi manapun script diletakkan
- Menambahkan komentar informatif pada HTML, CSS, dan JS untuk menjelaskan bagian yang tidak *self-explanatory* (mis. teknik `clamp()`, `grid-template-areas`, perbedaan cara mengatur ukuran font icon vs image icon)
- Penulisan dokumentasi README ini

---

## Pertanyaan Reflektif
### Tugas 1

1. Ya, saya menggunakan elemen semantik HTML5 seperti `<header>`, `<nav>`, `<main>`, `<section>`, dan `<footer>` untuk membagi struktur halaman menjadi tiga bagian utama: Profile, Skills, dan Projects (masing-masing dibungkus `<section>` dengan `id` sendiri). Elemen-elemen ini membantu saya membuat struktur halaman yang lebih jelas secara hierarki. Contohnya, `<nav>` langsung menandakan bagian navigasi ke pembaca kode maupun screen reader dan `<section id="skills">` memudahkan saya melakukan scroll-anchor lewat link di navbar (`href="#skills"`). Saya belum menggunakan `<article>` karena konten seperti kartu proyek belum berdiri sendiri sebagai konten yang bisa didistribusikan secara independen, jadi `<div class="project-card">` dirasa cukup. Saya juga belum memakai `<aside>` karena portofolio ini tidak punya konten pelengkap/sidebar yang terpisah dari alur utama.

2. Tantangan responsive yang paling terasa ada di section Skills dan Projects. Untuk section Skills, saya menggunakan `grid-template-columns: repeat(auto-fit, minmax(240px, 1fr))` supaya jumlah kolom kartu kategori otomatis menyesuaikan lebar layar tanpa perlu menulis media query untuk tiap breakpoint, tapi saya tetap perlu media query tambahan di 600px untuk memaksa 1 kolom penuh di mobile, karena `auto-fit` saja kadang masih menyisakan kolom yang terlalu sempit untuk menampung skill-pill. Saya juga harus mengatur `.skill-list` dengan `flex-wrap: wrap` supaya pill-pill skill tidak overflow keluar kartu saat kontainer menyempit. Untuk section Projects, tantangannya ada pada menyamakan tinggi kartu meski panjang deskripsi tiap proyek berbeda-beda. Saya memakai `display: flex; flex-direction: column` pada `.card-body` lalu `margin-top: auto` pada `.card-link`, sehingga tombol "View Project" dan ikon GitHub selalu menempel di bagian bawah kartu, sejajar antar kartu, apa pun panjang teksnya. Saya mengevaluasi prioritas ukuran dengan memberi `flex: 1` pada tombol utama (`.project-link`) dan ukuran tetap 44px pada ikon GitHub (`.github-link`), karena tombol utama harus lebih dominan secara visual dibanding ikon sekunder.

3. Karena situs ini murni statis, saya tidak bisa menyimpan atau memproses input apa pun secara konkret, seperti filter skill yang hanya bisa menyembunyikan/menampilkan elemen yang sudah ada di HTML, bukan mengambil data dari sumber lain. Menambah proyek baru juga berarti saya harus mengedit langsung kode HTML, bukan lewat semacam panel admin. Fungsionalitas dinamis yang paling ingin saya siapkan di iterasi berikutnya adalah backend sederhana menggunakan Django untuk menyimpan data proyek di database sehingga bisa diubah tanpa mengedit HTML manual.

## AI Disclosure
Saya menggunakan Claude (Anthropic) sebagai asisten belajar selama mengerjakan Tugas 1, dengan strategi utama yaitu meminta penjelasan konsep dan hint/referensi terlebih dahulu untuk kemudian dicoba dikulik dan diketik kkodenya sendiri.  

Bagian yang dibantu AI:
- Penjelasan konsep struktur HTML semantik (kenapa memilih `<div>` dibanding `<article>` untuk kartu proyek)
- Penjelasan CSS Grid (`grid-template-areas`, `grid-template-columns`, `clamp()`) yang saya terapkan ke `.hero-grid` dan `.project-grid`
- Penjelasan pola `repeat(auto-fit, minmax(...))` untuk membuat grid skill & project otomatis responsive
- Saat membangun fitur filter skill dengan JavaScript, saya secara eksplisit meminta AI memberi hint dan referensi per bagian struktur alih-alih kode utuh langsung pakai
- Merapikan `script.js` menjadi file terpisah dari HTML dan menambahkan komentar dokumentasi
- Membuat draf awal deskripsi proyek, cara setup proyek, dan deskripsi progres mingguan
- Debugging

Keterbatasan AI: AI tidak tahu bagian mana dari kode saya yang asli buatan sendiri vs hasil contoh tutorial kecuali saya beri tahu, jadi saya perlu mengoreksi draf refleksi secara manual agar jujur mencerminkan proses belajar saya.

Log chat AI: lihat `docs/ai-chat-log.pdf` di repo ini.