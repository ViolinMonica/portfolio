from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import (
    api_view, permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Experience, Project, Skill
from main.permissions import IsPortfolioOwnerOrEditorOrReadOnly, IsPortfolioOwnerOrReadOnly
from main.serializers import ExperienceSerializer, ProjectSerializer, SkillSerializer


@api_view(["GET", "HEAD", "POST"])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_list(request):
    if request.method in ("GET", "HEAD"):
        projects = Project.objects.prefetch_related("starred_by").order_by("title", "id")
        title = request.query_params.get("title", "").strip()
        if title:
            projects = projects.filter(title__icontains=title)
        serializer = ProjectSerializer(
            projects, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = ProjectSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.prefetch_related("starred_by"), pk=project_id,
    )
    if request.method in ("GET", "HEAD"):
        serializer = ProjectSerializer(project, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ProjectSerializer(
        project, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def project_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)
    serializer = ProjectSerializer(project, context={"request": request})
    return Response(serializer.data)

@api_view(["GET", "HEAD", "POST"])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def skill_list(request):
    if request.method in ("GET", "HEAD"):
        skills = Skill.objects.select_related("category").prefetch_related("starred_by")
        name = request.query_params.get("name", "").strip()
        if name:
            skills = skills.filter(name__icontains=name)
        serializer = SkillSerializer(skills, many=True, context={"request": request})
        return Response(serializer.data)

    serializer = SkillSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def skill_detail(request, skill_id):
    skill = get_object_or_404(
        Skill.objects.select_related("category").prefetch_related("starred_by"), pk=skill_id,
    )
    if request.method in ("GET", "HEAD"):
        return Response(SkillSerializer(skill, context={"request": request}).data)

    if request.method == "DELETE":
        skill.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = SkillSerializer(
        skill, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def skill_star(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)
    if skill.starred_by.filter(pk=request.user.pk).exists():
        skill.starred_by.remove(request.user)
    else:
        skill.starred_by.add(request.user)
    return Response(SkillSerializer(skill, context={"request": request}).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_logout(request):
    if request.auth is not None:
        request.auth.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "HEAD", "POST"])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def experience_list(request):
    """GET publik (terbaru dulu); POST hanya pemilik portofolio (superuser)."""
    if request.method in ("GET", "HEAD"):
        experiences = Experience.objects.order_by("-started_at", "id")
        return Response(ExperienceSerializer(experiences, many=True).data)

    serializer = ExperienceSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@permission_classes([IsPortfolioOwnerOrReadOnly])
def experience_detail(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method in ("GET", "HEAD"):
        return Response(ExperienceSerializer(experience).data)

    if request.method == "DELETE":
        experience.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ExperienceSerializer(
        experience, data=request.data, partial=request.method == "PATCH",
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)
