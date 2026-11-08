import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Project, Skill, SkillCategory


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.project = Project.objects.create(
            title="Portfolio", description="My website", tech_stack="Django",
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {
            "title": "New project", "description": "A useful app", "tech_stack": "Python",
            "project_url": "https://example.com/", "project_image_url": "",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.project.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"project_url": "javascript:alert(1)"}, "project_url"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.description, "My website")
        response = self.client.put(self.detail_url, {"title": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        # The Browsable API form renders a real CSRF token into the response.
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class SkillEditorAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(username="owner", password="test-password")
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.editor = User.objects.create_user(username="editor", password="test-password")
        self.editor.groups.add(Group.objects.get_or_create(name="Editor")[0])
        self.category = SkillCategory.objects.create(name="Backend Test")
        self.skill = Skill.objects.create(name="Django", category=self.category)
        self.list_url = reverse("api:skill-list")
        self.detail_url = reverse("api:skill-detail", args=[self.skill.id])
        self.star_url = reverse("api:skill-star", args=[self.skill.id])
        self.payload = {"name": "FastAPI", "category": str(self.category.id), "icon": ""}

    def test_public_can_read(self):
        self.assertEqual(self.client.get(self.list_url).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get(self.detail_url).data["name"], "Django")

    def test_editor_can_patch_and_put(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {"name": "Django REST"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "FastAPI")

    def test_editor_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Skill.objects.filter(category=self.category).count(), 1)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.patch(self.detail_url, {"name": "X"}, format="json").status_code, 403)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "Django")
        self.assertFalse(Skill.objects.filter(name="FastAPI").exists())
        self.assertTrue(Skill.objects.filter(pk=self.skill.id).exists())

    def test_owner_can_create_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 201)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 204)
        self.assertFalse(Skill.objects.filter(pk=self.skill.id).exists())

    def test_new_category_created_or_reused(self):
        self.client.force_authenticate(user=self.owner)
        payload = {"name": "PyTorch", "new_category": "<b>Machine Learning</b>"}
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["category_name"], "Machine Learning")
        self.assertNotIn("new_category", response.data)
        # beda huruf besar-kecil tetap memakai kategori yang sama
        payload = {"name": "Keras", "new_category": "machine learning"}
        self.client.post(self.list_url, payload, format="json")
        self.assertEqual(SkillCategory.objects.filter(name__iexact="machine learning").count(), 1)

    def test_create_without_any_category_rejected(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {"name": "Go"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("category", response.data)
        self.assertFalse(Skill.objects.filter(name="Go").exists())

    def test_star_uses_is_authenticated_not_editor(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.skill.starred_by.count(), 0)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertTrue(self.skill.starred_by.filter(pk=self.visitor.pk).exists())

    def test_second_star_unstars(self):
        self.client.force_authenticate(user=self.visitor)
        self.client.post(self.star_url)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(self.skill.starred_by.exists())

    def test_star_count_does_not_expose_account_data(self):
        self.skill.starred_by.add(self.visitor)
        data = self.client.get(self.detail_url).data
        self.assertNotIn("starred_by", data)
        self.assertNotIn(self.visitor.email or "@", str(data))

    def test_validation_rejects_empty_and_tag_only_name(self):
        self.client.force_authenticate(user=self.owner)
        for name in ("", "   ", "<b></b>"):
            response = self.client.post(self.list_url, {**self.payload, "name": name}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("name", response.data)
        response = self.client.patch(self.detail_url, {"name": "<script></script>"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Skill.objects.filter(category=self.category).count(), 1)
        self.skill.refresh_from_db()
        self.assertEqual(self.skill.name, "Django")

    def test_validation_strips_tags(self):
        self.client.force_authenticate(user=self.owner)
        payload = {**self.payload, "name": "<b>Go</b>", "icon": "<i>🐹</i>"}
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        skill = Skill.objects.get(pk=response.data["id"])
        self.assertEqual((skill.name, skill.icon), ("Go", "🐹"))

    def test_search_by_name(self):
        # database test sudah berisi skill dari migrasi seed, jadi pakai nama yang unik
        Skill.objects.create(name="Zyxlang", category=self.category)
        names = [s["name"] for s in self.client.get(self.list_url, {"name": "ZYX"}).data]
        self.assertEqual(names, ["Zyxlang"])
        self.assertEqual(self.client.get(self.list_url, {"name": "zzz"}).data, [])

    def test_missing_skill_returns_404(self):
        missing = uuid.uuid4()
        self.assertEqual(self.client.get(reverse("api:skill-detail", args=[missing])).status_code, 404)
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(reverse("api:skill-detail", args=[missing])).status_code, 404)
        self.assertEqual(self.client.post(reverse("api:skill-star", args=[missing])).status_code, 404)

    def test_session_write_without_csrf_is_rejected(self):
        # force_authenticate melewati CSRF; .login() memakai session asli
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Skill.objects.filter(name="FastAPI").exists())
        response = client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(self.skill.starred_by.exists())
