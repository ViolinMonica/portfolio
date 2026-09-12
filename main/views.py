from django.shortcuts import render

from main.models import Experience, Project


def show_main(request):
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
    experiences = Experience.objects.all().order_by("-started_at")
    context = {
        "ongoing_list": [e for e in experiences if e.is_ongoing],
        "past_list": [e for e in experiences if not e.is_ongoing],
    }
    return render(request, "experience.html", context)


def show_projects(request):
    context = {
        "projects_list": Project.objects.all().order_by("-created_at"),
    }
    return render(request, "projects.html", context)