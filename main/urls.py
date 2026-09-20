from django.urls import path
from main.views import (
    show_main, show_experience, show_projects, create_project,
    get_projects_json, delete_project,
    show_skills, create_skill, edit_skill, delete_skill, get_skills_json
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("projects/add/", create_project, name="create_project"),
    path("experience/", show_experience, name="show_experience"),
    path("projects/", show_projects, name="show_projects"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("projects/<uuid:project_id>/delete/",delete_project,name="delete_project"),
    path("skills/", show_skills, name="show_skills"),
    path("skills/add/", create_skill, name="create_skill"),
    path("skills/<uuid:skill_id>/edit/", edit_skill, name="edit_skill"),
    path("skills/<uuid:skill_id>/delete/", delete_skill, name="delete_skill"),
     path("api/skills/", get_skills_json, name="get_skills_json"),
]
