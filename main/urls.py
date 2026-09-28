from django.urls import path
from main.views import (
    show_main, show_experience, show_projects, create_project,
    get_projects_json, delete_project,
    show_skills, create_skill, edit_skill, delete_skill, get_skills_json, register, 
    login_user, logout_user, toggle_project_star, toggle_skill_star, create_project_ajax
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
    path("skills/<uuid:skill_id>/star/", toggle_skill_star, name="toggle_skill_star"),
    path("api/skills/", get_skills_json, name="get_skills_json"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("projects/<uuid:project_id>/star/",toggle_project_star,name="toggle_project_star",),
    path("projects/add-ajax/", create_project_ajax, name="create_project_ajax"),
]
