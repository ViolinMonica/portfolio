from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from main.views import show_main, show_experience, show_projects

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
     path('projects/', show_projects, name='show_projects'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)