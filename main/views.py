from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect
from boxsdk.auth.oauth2 import OAuth2
from boxsdk.client import Client

from .models import *
from .forms import *

def index(request):
    return render(request, "index.html")

def box(request):
    if 'access_token' in request.session:
        oauth = OAuth2(client_id=settings.BOX_CLIENT_ID,
                       client_secret=settings.BOX_CLIENT_SECRET,
                       access_token=request.session['access_token'],
                       refresh_token=request.session['refresh_token'])
        user_info = Client(oauth).user(user_id='me').get()
    else:
        oauth = OAuth2(client_id=settings.BOX_CLIENT_ID,
                       client_secret=settings.BOX_CLIENT_SECRET)
        auth_url, csrf_token = oauth.get_authorization_url(request.build_absolute_uri(reverse('box_oauth2')))
        request.session['box_csrf_token'] = csrf_token

    return render(request, "box.html", locals())

def box_oauth2(request):
    oauth = OAuth2(client_id=settings.BOX_CLIENT_ID,
                   client_secret=settings.BOX_CLIENT_SECRET)
    state = request.GET.get('state')
    code = request.GET.get('code')

    assert state == request.session['box_csrf_token']
    access_token, refresh_token = oauth.authenticate(code)

    request.session['access_token'] = access_token
    request.session['refresh_token'] =  refresh_token

    return redirect('box')

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
