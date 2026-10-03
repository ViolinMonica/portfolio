from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from main.context_processors import site_identity
from main.models import Experience, Project, Skill, SkillCategory

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

    # Daftar proyek sekarang dirender JS dari endpoint JSON, jadi datanya dicek di sana.
    def test_data_shown_when_present(self):
        Project.objects.create(
            title="NUSA-CROP", description="Crop recommender", tech_stack="Django"
        )
        response = self.client.get(reverse("main:get_projects_json"))
        self.assertContains(response, "NUSA-CROP")
        self.assertContains(response, "Django")

    def test_empty_list_when_no_data(self):
        response = self.client.get(reverse("main:get_projects_json"))
        self.assertEqual(response.json(), [])

    def test_search_filters_by_title(self):
        Project.objects.create(title="NUSA-CROP", description="d", tech_stack="t")
        Project.objects.create(title="Bobol", description="d", tech_stack="t")
        response = self.client.get(reverse("main:get_projects_json"), {"title": "nusa"})
        self.assertContains(response, "NUSA-CROP")
        self.assertNotContains(response, "Bobol")

    def test_search_empty_list_when_no_match(self):
        Project.objects.create(title="NUSA-CROP", description="d", tech_stack="t")
        response = self.client.get(reverse("main:get_projects_json"), {"title": "zzz"})
        self.assertEqual(response.json(), [])

class CreateProjectTest(TestCase):
    def setUp(self):
        self.client.force_login(
            User.objects.create_superuser("admin_test", password="rahasia123")
        )
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
        self.client.force_login(
            User.objects.create_superuser("admin_test", password="rahasia123")
        )
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

class SkillPermissionTest(TestCase):
    """Pastikan pembatasan akses dijalankan server-side"""

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse("main:create_skill"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_logged_in_without_permission_gets_403(self):
        self.client.force_login(
            User.objects.create_user("biasa", password="rahasia123")
        )
        response = self.client.get(reverse("main:create_skill"))
        self.assertEqual(response.status_code, 403)



class CreateSkillAjaxTest(TestCase):
    """View AJAX tambah skill: status HTTP, validasi, izin, CSRF, dan strip_tags."""

    def setUp(self):
        self.url = reverse("main:create_skill_ajax")
        self.category = SkillCategory.objects.create(name="Testing Category")
        self.admin = User.objects.create_superuser("admin", password="rahasia123")

    def test_anonymous_gets_403_json(self):
        response = self.client.post(self.url, {"name": "Go", "category": self.category.id})
        self.assertEqual(response.status_code, 403)
        self.assertIn("message", response.json())
        self.assertFalse(Skill.objects.filter(name="Go").exists())

    def test_user_without_permission_gets_403(self):
        self.client.force_login(User.objects.create_user("biasa", password="rahasia123"))
        response = self.client.post(self.url, {"name": "Go", "category": self.category.id})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Skill.objects.filter(name="Go").exists())

    def test_invalid_input_returns_400_with_field_errors(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url, {"name": ""})
        self.assertEqual(response.status_code, 400)
        errors = response.json()["errors"]
        self.assertIn("name", errors)
        self.assertIn("category", errors)

    def test_valid_input_returns_201_and_strips_tags(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            self.url, {"name": "<b>Go</b>", "category": self.category.id}
        )
        self.assertEqual(response.status_code, 201)
        skill = Skill.objects.get(pk=response.json()["id"])
        self.assertEqual(skill.name, "Go")

    def test_get_not_allowed(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_post_without_csrf_token_rejected(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)
        response = client.post(self.url, {"name": "Go", "category": self.category.id})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Skill.objects.filter(name="Go").exists())


class SkillsJsonTest(TestCase):
    """Endpoint JSON skill: info star per pengguna dan pencarian ?name=."""

    def setUp(self):
        self.url = reverse("main:get_skills_json")
        category = SkillCategory.objects.create(name="Testing Category")
        self.skill = Skill.objects.create(name="Zigzag", category=category)
        self.user = User.objects.create_user("biasa", password="rahasia123")
        self.skill.starred_by.add(self.user)

    def find_skill(self, response):
        for category in response.json():
            for skill in category["skills"]:
                if skill["id"] == str(self.skill.id):
                    return skill
        return None

    def test_anonymous_sees_star_count_but_not_starred(self):
        skill = self.find_skill(self.client.get(self.url))
        self.assertEqual(skill["star_count"], 1)
        self.assertFalse(skill["is_starred"])

    def test_logged_in_user_sees_own_star(self):
        self.client.force_login(self.user)
        self.assertTrue(self.find_skill(self.client.get(self.url))["is_starred"])

    def test_search_by_name_drops_other_skills_and_empty_categories(self):
        data = self.client.get(self.url, {"name": "zigz"}).json()
        names = [s["name"] for c in data for s in c["skills"]]
        self.assertEqual(names, ["Zigzag"])
        self.assertTrue(all(c["skills"] for c in data))
