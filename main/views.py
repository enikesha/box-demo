from django.shortcuts import render

def index(request):
    return render(request, "index.html")

def box(request):
    return render(request, "index.html")

def edit(request):
    return render(request, "index.html")

def about(request):
    return render(request, "index.html")
