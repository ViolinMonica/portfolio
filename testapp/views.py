from django.shortcuts import render
from .models import Mahasiswa

def index(request):
    mahasiswa_list = Mahasiswa.objects.all()
    return render(request, 'index.html', {'mahasiswa_list': mahasiswa_list})
