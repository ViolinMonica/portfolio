from django.test import TestCase
from django.urls import reverse

from main.models import Experience, Project


class ExperienceModelTest(TestCase):
    def test_is_ongoing_true_when_no_end_date(self):
        exp = Experience.objects.create(title="Intern", description="d")
        self.assertTrue(exp.is_ongoing)

    def test_is_ongoing_false_when_ended(self):
        from django.utils import timezone
        exp = Experience.objects.create(
            title="Intern", description="d", ended_at=timezone.now()
        )
        self.assertFalse(exp.is_ongoing)

    def test_str_returns_title(self):
        exp = Experience.objects.create(title="Research", description="d")
        self.assertEqual(str(exp), "Research")


class ProjectModelTest(TestCase):
    def test_skills_list_splits_and_strips(self):
        p = Project.objects.create(
            title="P", description="d", skills="Django,  React ,PostgreSQL"
        )
        self.assertEqual(p.skills_list, ["Django", "React", "PostgreSQL"])

    def test_skills_list_ignores_empty_entries(self):
        p = Project.objects.create(title="P", description="d", skills="Django, ,")
        self.assertEqual(p.skills_list, ["Django"])

    def test_skills_list_empty_when_blank(self):
        p = Project.objects.create(title="P", description="d", skills="")
        self.assertEqual(p.skills_list, [])


class ViewTest(TestCase):
    def test_main_view_status_and_template(self):
        response = self.client.get(reverse("main:show_main"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_experience_view_returns_list(self):
        Experience.objects.create(title="Intern", description="d")
        response = self.client.get(reverse("main:show_experience"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertEqual(len(response.context["experience_list"]), 1)

    def test_projects_view_returns_list(self):
        Project.objects.create(title="P", description="d")
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")
        self.assertEqual(len(response.context["projects_list"]), 1)