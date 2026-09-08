from django.shortcuts import render

from main.models import Experience
from testapp.models import Mahasiswa


def show_main(request):
    context = {
        "name": "Violin Monica",
        "npm": "2506551794",
        "study_program": "S1 Ilmu Komputer",
        "bio": ("Computer Science student at Universitas Indonesia with a growing expertise in Cybersecurity and Data Science. I thrive at the intersection of rigorous logic and creative problem-solving. I am passionate about uncovering vulnerabilities and leveraging data to build secure, impactful solutions. Always open to discussing tech trends, security research, or potential collaborations. Reach me at: violin.monica@ui.ac.id or violin.monica@ristek.cs.ui.ac.id or violinmonica190207@gmail.com."),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Violin Monica",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)