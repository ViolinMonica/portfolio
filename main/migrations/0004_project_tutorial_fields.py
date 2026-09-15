from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0003_project_thumbnail_alter_experience_thumbnail"),
    ]

    operations = [
        migrations.RemoveField(model_name="project", name="status"),
        migrations.RemoveField(model_name="project", name="skills"),
        migrations.RemoveField(model_name="project", name="github_url"),
        migrations.RemoveField(model_name="project", name="demo_url"),
        migrations.RemoveField(model_name="project", name="thumbnail"),
        migrations.RemoveField(model_name="project", name="created_at"),
        migrations.AddField(
            model_name="project",
            name="tech_stack",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="project",
            name="project_url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="project",
            name="project_image_url",
            field=models.URLField(blank=True, max_length=500),
        ),
    ]
