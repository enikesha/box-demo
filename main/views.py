from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from .forms import *

def index(request):
    return render(request, "index.html")

def box(request):
    return render(request, "index.html")

def note_list(request):
    notes = Note.objects.filter(session=request.session.session_key)

    return render(request, "note_list.html", locals())

def note_add(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(False)
            note.session = request.session.session_key
            note.save()
            return redirect('note_list')
    else:
        form = NoteForm()

    return render(request, "note_form.html", locals())

def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk, session=request.session.session_key)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect('note_list')
    else:
        form = NoteForm(instance=note)
    return render(request, "note_form.html", locals())

def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, session=request.session.session_key)
    if request.method == 'POST':
        note.delete()
        return redirect('note_list')
    return render(request, "note_delete.html", locals())

def about(request):
    return render(request, "about.html")
