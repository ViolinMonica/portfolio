from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Project

class ExperienceModelTest(TestCase):
    def test_is_ongoing_true_when_no_end_date(self):
        exp = Experience.objects.create(title="Intern", description="d")
        self.assertTrue(exp.is_ongoing)

    def test_is_ongoing_false_when_ended(self):
        exp = Experience.objects.create(
            title="Intern", description="d", ended_at=timezone.now()
        )
        self.assertFalse(exp.is_ongoing)


class ProjectModelTest(TestCase):
    def test_skills_list_splits_and_strips(self):
        p = Project.objects.create(
            title="P", description="d", skills="Django,  React ,PostgreSQL"
        )
        self.assertEqual(p.skills_list, ["Django", "React", "PostgreSQL"])

    def test_skills_list_empty_when_blank(self):
        p = Project.objects.create(title="P", description="d", skills="")
        self.assertEqual(p.skills_list, [])

class ExperiencePageTest(TestCase):
    # Kasus 1: URL dapat diakses dan memakai template yang tepat.
    def test_url_accessible_and_uses_template(self):
        response = self.client.get(reverse("main:show_experience"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")

    # Kasus 2: data model muncul di HTML ketika ada data.
    def test_data_shown_when_present(self):
        Experience.objects.create(
            title="Teaching Assistant", description="Supervising labs"
        )
        response = self.client.get(reverse("main:show_experience"))
        self.assertContains(response, "Teaching Assistant")

    # Kasus 3: pesan kondisi kosong muncul ketika belum ada data.
    def test_empty_message_when_no_data(self):
        response = self.client.get(reverse("main:show_experience"))
        self.assertContains(response, "No experience added yet.")

class ProjectsPageTest(TestCase):
    # Kasus 1
    def test_url_accessible_and_uses_template(self):
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")

    # Kasus 2
    def test_data_shown_when_present(self):
        Project.objects.create(title="NUSA-CROP", description="Crop recommender")
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, "NUSA-CROP")

    # Kasus 3
    def test_empty_message_when_no_data(self):
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, "No project added yet.")