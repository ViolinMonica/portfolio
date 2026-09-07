document.addEventListener("DOMContentLoaded", function () {
    // Ambil elemen dropdown filter (cuma 1 elemen, makanya pakai querySelector tunggal)
    const skillFilter = document.querySelector("#skill-filter");

    // Ambil SEMUA card kategori skill (Languages, Fullstack, dst)
    // querySelectorAll ngembaliin NodeList (kayak array) berisi semua elemen yang match
    const skillCategories = document.querySelectorAll(".skill-category");

    // Pasang "pendengar" event: tiap kali user ganti pilihan di dropdown,
    // function di dalam ini otomatis kejalan
    skillFilter.addEventListener("change", function () {

        // Ambil value dari opsi yang lagi dipilih user saat ini
        // (value ini sesuai atribut value="..." di tiap <option>, misal "fullstack")
        const selectedValue = skillFilter.value;

        // Looping satu-satu ke semua skill-category buat dicek
        skillCategories.forEach(function (category) {

            // category.dataset.category ngambil isi atribut data-category="..."
            // yang ditulis manual di HTML tiap .skill-category

            // Kondisi: tampilkan card ini KALAU
            // (a) user pilih "All", ATAU
            // (b) data-category card ini cocok sama value yang dipilih
            if (selectedValue === "all" || category.dataset.category === selectedValue) {
                // "" (string kosong) artinya balikin ke display bawaan CSS-nya
                // (bukan dipaksa jadi "block", biar tetap ngikut aturan display asli, misal "flex")
                category.style.display = "";
            } else {
                // Kalau kategori nggak match pilihan user, sembunyikan card-nya
                category.style.display = "none";
            }
        });
    });
});