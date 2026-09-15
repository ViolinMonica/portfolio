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

class ContextProcessorTest(TestCase):
    def test_site_identity_returns_name(self):
        self.assertEqual(site_identity(None)["name"], "Violin Monica")

    def test_name_available_on_pages_without_being_in_view(self):
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
        self.assertTemplateUsed(response, "project.html")

    def test_data_shown_when_present(self):
        Project.objects.create(
            title="NUSA-CROP", description="Crop recommender", tech_stack="Django"
        )
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, "NUSA-CROP")
        self.assertContains(response, "Django")

    def test_empty_message_when_no_data(self):
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, "Belum ada proyek yang ditambahkan.")

    def test_search_filters_by_title(self):
        Project.objects.create(title="NUSA-CROP", description="d", tech_stack="t")
        Project.objects.create(title="Bobol", description="d", tech_stack="t")
        response = self.client.get(reverse("main:show_projects"), {"title": "nusa"})
        self.assertContains(response, "NUSA-CROP")
        self.assertNotContains(response, "Bobol")

    def test_search_empty_message_when_no_match(self):
        Project.objects.create(title="NUSA-CROP", description="d", tech_stack="t")
        response = self.client.get(reverse("main:show_projects"), {"title": "zzz"})
        self.assertContains(response, "Tidak ada proyek dengan nama tersebut.")

class CreateProjectTest(TestCase):
    def test_form_page_accessible(self):
        response = self.client.get(reverse("main:create_project"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects_form.html")

    def test_form_has_tutorial_fields(self):
        response = self.client.get(reverse("main:create_project"))
        for name in ["title", "description", "tech_stack", "project_url", "project_image_url"]:
            self.assertContains(response, f'name="{name}"')

    def test_valid_post_creates_project_and_redirects(self):
        response = self.client.post(
            reverse("main:create_project"),
            {
                "title": "Portfolio Website",
                "description": "Django portfolio",
                "tech_stack": "Django, Python, HTML, CSS",
                "project_url": "https://github.com/example/portfolio",
                "project_image_url": "",
            },
            follow=True,
        )
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertTrue(Project.objects.filter(title="Portfolio Website").exists())
        self.assertContains(response, "Portfolio Website")

    def test_invalid_post_shows_errors(self):
        response = self.client.post(reverse("main:create_project"), {"title": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Project.objects.count(), 0)
        self.assertContains(response, "form-error")

class ProjectsJsonTest(TestCase):
    def test_returns_json(self):
        Project.objects.create(title="NUSA-CROP", description="d", tech_stack="Django")
        response = self.client.get(reverse("main:get_projects_json"))
        self.assertEqual(response["Content-Type"], "application/json")
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["fields"]["title"], "NUSA-CROP")
        self.assertEqual(data[0]["fields"]["tech_stack"], "Django")

    def test_filters_by_title(self):
        Project.objects.create(title="NUSA-CROP", description="d", tech_stack="t")
        Project.objects.create(title="Bobol", description="d", tech_stack="t")
        response = self.client.get(reverse("main:get_projects_json"), {"title": "bob"})
        titles = [p["fields"]["title"] for p in response.json()]
        self.assertEqual(titles, ["Bobol"])

class DeleteProjectTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="NUSA-CROP", description="d", tech_stack="t"
        )
        self.url = reverse("main:delete_project", args=[self.project.id])

    def test_post_deletes_project(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_get_does_not_delete(self):
        self.client.get(self.url)
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())

    def test_unknown_project_returns_404(self):
        response = self.client.post(
            reverse("main:delete_project", args=["00000000-0000-0000-0000-000000000000"])
        )
        self.assertEqual(response.status_code, 404)
