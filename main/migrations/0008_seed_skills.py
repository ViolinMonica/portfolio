from django.db import migrations

CATEGORIES = [
    (1, "Languages", "languages"),
    (2, "Programming Languages", "programming"),
    (3, "Fullstack", "fullstack"),
    (4, "Database", "database"),
    (5, "Cybersecurity", "cybersecurity"),
    (6, "Tools", "tools"),
    (7, "Robotic", "robotic"),
    (8, "Beside the Keyboard", "design"),
]

SKILLS = [
    ("languages", "Bahasa Indonesia (Native proficiency)", "\U0001F1EE\U0001F1E9", 5),
    ("languages", "English (Professional proficiency)", "\U0001F1EC\U0001F1E7", 4),
    ("languages", "Mandarin (Basic proficiency)", "\U0001F1E8\U0001F1F3", 2),
    ("programming", "Python", "devicon-python-plain", 3),
    ("programming", "Java", "devicon-java-plain", 3),
    ("programming", "C++", "devicon-cplusplus-plain", 3),
    ("programming", "SQL", "devicon-azuresqldatabase-plain", 3),
    ("fullstack", "Django", "devicon-django-plain", 3),
    ("fullstack", "Next.js", "devicon-nextjs-plain", 3),
    ("fullstack", "REST API", "", 3),
    ("fullstack", "HTML", "devicon-html5-plain", 3),
    ("fullstack", "CSS", "devicon-css3-plain", 3),
    ("fullstack", "Postman", "devicon-postman-plain", 3),
    ("fullstack", "React", "devicon-react-plain", 3),
    ("database", "PostgreSQL", "devicon-postgresql-plain", 3),
    ("database", "SQLite", "devicon-sqlite-plain", 3),
    ("cybersecurity", "Burp Suite", "https://cdn.simpleicons.org/burpsuite", 3),
    ("cybersecurity", "Wireshark", "https://cdn.simpleicons.org/wireshark", 3),
    ("cybersecurity", "Nmap", "https://nmap.org/images/sitelogo-2x.png", 3),
    ("cybersecurity", "Ghidra", "https://media.defense.gov/2023/Mar/06/2003173005/-1/-1/0/230306-D-IM742-4444.PNG", 3),
    ("tools", "Git", "devicon-git-plain", 3),
    ("tools", "Github", "devicon-github-plain", 3),
    ("tools", "Linux", "devicon-linux-plain", 3),
    ("tools", "Docker", "devicon-docker-plain", 3),
    ("tools", "Visual Studio Code", "devicon-vscode-plain", 3),
    ("robotic", "Robot Operating System (ROS)", "devicon-ros-original", 3),
    ("robotic", "Arduino", "devicon-arduino-plain", 3),
    ("design", "UI/UX", "", 3),
    ("design", "Figma", "devicon-figma-plain", 3),
    ("design", "Graphic Design", "", 3),
    ("design", "Painting", "", 3),
]


def seed(apps, schema_editor):
    SkillCategory = apps.get_model("main", "SkillCategory")
    Skill = apps.get_model("main", "Skill")

    by_slug = {
        slug: SkillCategory.objects.create(name=name, slug=slug, order=order)
        for order, name, slug in CATEGORIES
    }
    for slug, name, icon, proficiency in SKILLS:
        Skill.objects.create(
            category=by_slug[slug],
            name=name,
            icon=icon,
            proficiency=proficiency,
        )


def unseed(apps, schema_editor):
    apps.get_model("main", "Skill").objects.all().delete()
    apps.get_model("main", "SkillCategory").objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0007_alter_skill_options_alter_skill_icon"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]