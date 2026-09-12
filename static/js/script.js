document.addEventListener("DOMContentLoaded", function () {
    // Dropdown filter cuma ada di halaman utama (index).
    // Kalau di halaman lain elemennya null, blok ini dilewati
    // sehingga addEventListener tidak melempar TypeError.
    const skillFilter = document.querySelector("#skill-filter");
    if (!skillFilter) return;

    const skillCategories = document.querySelectorAll(".skill-category");

    skillFilter.addEventListener("change", function () {
        const selectedValue = skillFilter.value;

        skillCategories.forEach(function (category) {
            // Butuh data-category="..." di tiap .skill-category pada HTML.
            const matches =
                selectedValue === "all" ||
                category.dataset.category === selectedValue;

            // "" mengembalikan ke display bawaan CSS (mis. flex), bukan dipaksa "block".
            category.style.display = matches ? "" : "none";
        });
    });
});