document.addEventListener("DOMContentLoaded", function () {
    // Dropdown filter cuma ada di halaman utama (index).
    // Kalau di halaman lain elemennya null, blok ini dilewati
    // sehingga addEventListener tidak melempar TypeError.
    const skillFilter = document.querySelector("#skill-filter");
    if (!skillFilter) return;
    skillFilter.addEventListener("change", function () {
        const selectedValue = skillFilter.value;
        document.querySelectorAll(".skill-category").forEach(function (category) {
            const matches = selectedValue === "all" || category.dataset.category === selectedValue;
            category.style.display = matches ? "" : "none";
        });
    });
});