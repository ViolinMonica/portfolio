from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience
from main.models import Project
class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Teaching Assistant of Programming Foundations 1",
            description="<ul><li>Supervising programming lab sessions</li><li>Developed problems and sample solutions for programming lab exercises</li><li>Graded and evaluated student quizzes and programming lab results</li><li>Helped students understand Python programming foundations</li></ul>",
            category="part-time",
            ended_at=timezone.now()
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Teaching Assistant of Programming Foundations 1")
        self.assertEqual(self.experience.category, "part-time")
        self.assertFalse(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, "Supervising programming lab sessions")
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Done")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "No experience added yet.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Done")
        self.assertNotContains(response, "Ongoing")

    def test_project_page(self):
        project = Project.objects.create(
            title="NUSA-CROP",
            description="Crop recommendation system.",
            status="completed",
        )
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")
        self.assertContains(response, "NUSA-CROP")
        self.assertContains(response, "Crop recommendation system.")
        self.assertContains(response, "Completed")   # dari get_status_display

    def test_empty_project_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, "No project added yet.")

    def test_project_model(self):
        project = Project.objects.create(
            title="NUSA-CROP",
            description="Crop recommendation system.",
            status="completed",
        )
        self.assertEqual(str(project), "NUSA-CROP")
        self.assertEqual(project.status, "completed")