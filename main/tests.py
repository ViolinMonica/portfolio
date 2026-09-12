from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.context_processors import site_identity
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

class ContextProcessorTest(TestCase):
    def test_site_identity_returns_name(self):
        self.assertEqual(site_identity(None)["name"], "Violin Monica")

    def test_name_available_on_pages_without_being_in_view(self):
        # show_projects tidak menaruh "name" di context; harus datang
        # dari context processor.
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, "Violin Monica")

class ExperiencePageTest(TestCase):
    def test_url_accessible_and_uses_template(self):
        response = self.client.get(reverse("main:show_experience"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")

    def test_data_shown_when_present(self):
        Experience.objects.create(
            title="Teaching Assistant", description="Supervising labs"
        )
        response = self.client.get(reverse("main:show_experience"))
        self.assertContains(response, "Teaching Assistant")

    def test_empty_message_when_no_data(self):
        response = self.client.get(reverse("main:show_experience"))
        self.assertContains(response, "No ongoing experience.")
        self.assertContains(response, "No past experience yet.")

    def test_ongoing_and_past_grouped_correctly(self):
        Experience.objects.create(title="Current Role", description="d")
        Experience.objects.create(
            title="Old Role", description="d", ended_at=timezone.now()
        )
        response = self.client.get(reverse("main:show_experience"))
        ongoing = list(response.context["ongoing_list"])
        past = list(response.context["past_list"])
        self.assertEqual([e.title for e in ongoing], ["Current Role"])
        self.assertEqual([e.title for e in past], ["Old Role"])

class ProjectsPageTest(TestCase):
    def test_url_accessible_and_uses_template(self):
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")

    def test_data_shown_when_present(self):
        Project.objects.create(title="NUSA-CROP", description="Crop recommender")
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, "NUSA-CROP")

    def test_empty_message_when_no_data(self):
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, "No project added yet.")