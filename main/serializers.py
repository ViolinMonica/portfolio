from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Project, Skill, SkillCategory


class ProjectSerializer(serializers.ModelSerializer):
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "title", "description", "tech_stack",
            "project_url", "project_image_url",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_description(self, value):
        return strip_tags(value)

    def validate_tech_stack(self, value):
        return strip_tags(value)

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())

class SkillSerializer(serializers.ModelSerializer):
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    icon_kind = serializers.CharField(read_only=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    # Jalan pintas dari SkillForm (Tugas 3): kategori baru dibuat langsung dari modal.
    # write_only karena ini input, bukan bagian dari representasi skill.
    new_category = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=50)

    class Meta:
        model = Skill
        fields = [
            "id", "name", "category", "category_name", "icon", "icon_kind",
            "is_featured", "star_count", "is_starred", "category_slug", "new_category",
        ]
        read_only_fields = ["id"]
        # category boleh kosong asal new_category diisi; aturan "salah satu wajib" ada di validate()
        extra_kwargs = {"category": {"required": False}}

    def validate_name(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        return value

    def validate_icon(self, value):
        return strip_tags(value).strip()

    def validate_new_category(self, value):
        return strip_tags(value).strip()

    def validate(self, attrs):
        """Pakai kategori dari dropdown, atau buat/cari kategori dari new_category.

        Dicocokkan dengan name__iexact supaya "machine learning" tidak membuat
        duplikat "Machine Learning". Kategori dibuat di sini karena validate()
        berjalan setelah semua validate_<field> lolos, jadi tidak ada kategori
        yatim akibat field lain yang gagal validasi.
        """
        new_name = attrs.pop("new_category", "")
        if new_name:
            category = SkillCategory.objects.filter(name__iexact=new_name).first()
            if category is None:
                last = SkillCategory.objects.order_by("-order").first()
                category = SkillCategory.objects.create(
                    name=new_name, order=(last.order + 1) if last else 1,
                )
            attrs["category"] = category
        elif "category" not in attrs and not self.partial:
            raise serializers.ValidationError(
                {"category": "Pilih kategori yang ada atau isi kategori baru."}
            )
        return attrs

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()
