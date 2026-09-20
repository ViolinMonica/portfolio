from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import ProjectForm, SkillForm
from main.models import Experience, Project, Skill, SkillCategory


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


def create_project(request):
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
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")


def show_projects(request):
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
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")

    return redirect("main:show_projects")


def get_skills_json(request):
    return HttpResponse(
        serializers.serialize("json", Skill.objects.all()),
        content_type="application/json",
    )


def _categories_with_skills(request):
    """Ambil skill lewat endpoint JSON, deserialisasi, lalu kelompokkan per kategori."""
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
    return render(
        request, "skill.html", {"category_list": _categories_with_skills(request)}
    )


def create_skill(request):
    form = SkillForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Skill baru berhasil ditambahkan!")
        return redirect("main:show_skills")

    return render(request, "skills_form.html", {"form": form})


def edit_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    form = SkillForm(request.POST or None, instance=skill)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Skill berhasil diperbarui!")
        return redirect("main:show_skills")

    return render(request, "skills_form.html", {"form": form, "skill": skill})


def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)

    if request.method == "POST":
        skill.delete()
        messages.success(request, "Skill berhasil dihapus!")

    return redirect("main:show_skills")
