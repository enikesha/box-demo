import csv
import mimetypes
import os
import time
from contextlib import contextmanager
from StringIO import StringIO
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from boxsdk.auth.oauth2 import OAuth2
from boxsdk.client import Client
from boxsdk.exception import BoxAPIException, BoxOAuthException
from boxsdk.object.file import File
from boxview import boxview

from .models import *
from .forms import *

# monkey-patch box's File object to provide download url
def File__content_url(self):
    url = self.get_url('content')
    box_response = self._session.get(url, expect_json_response=False,
                                     allow_redirects=False)
    if box_response.status_code == 302:
        return box_response.network_response.headers['Location']

    raise BoxAPIException(box_response.status_code,
                          message="Bad status code from file /content",
                          url=url, method="GET")
File.content_url = File__content_url

@contextmanager
def get_client(request):
    try:
        oauth = OAuth2(client_id=settings.BOX_CLIENT_ID,
                       client_secret=settings.BOX_CLIENT_SECRET,
                       access_token=request.session.get('access_token', None),
                       refresh_token=request.session.get('refresh_token', None))
        yield Client(oauth)
    except BoxOAuthException, e:
        print e
        for key in ('access_token', 'refresh_token'):
            if key in request.session:
                del request.session[key]

def index(request):
    return render(request, "index.html")

def box(request):
    if 'access_token' in request.session:
        with get_client(request) as client:
            user_info = client.user(user_id='me').get()
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
            if not request.session.session_key:
                request.session.flush()
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

def metadata(request):
    with get_client(request) as client:
        folder = client.folder(folder_id=request.REQUEST.get('folder', '0'))
        if request.method == 'POST':
            # Upload file, preserving original extension
            name, ext = os.path.splitext(request.FILES['file'].name)
            folder.upload_stream(request.FILES['file'], request.POST['filename']+ext)
            return redirect(request.get_full_path())
        # Browse folder, collecting metadata files
        folder_info = folder.get(fields=('name', 'path_collection'))
        items_info = []
        items_metadata = {}
        for item in folder.get_items(limit=100, fields=('id','name')):
            name, ext = os.path.splitext(item['name'])
            item.filename = name
            if name.endswith('_metadata'):
                item.ext = ext.lower()
                items_metadata[name[:-9]] = item
            else:
                items_info.append(item)
        for item in items_info:
            item.metadata = items_metadata.get(item.filename)

        if 'view' in request.GET:
            # View csv file
            try:
                file = client.file(request.GET['view']).get(fields=('name',))
                name, ext = os.path.splitext(file['name'])
                if ext.lower() == '.csv':
                    buffer = StringIO()
                    file.download_to(buffer)
                    buffer.seek(0)
                    metadata = list(csv.reader(buffer))
            except Exception, e:
                print e
        return render(request, "metadata.html", locals())
    # In case OAuth error
    return redirect('box')

def metadata_download(request, id):
    with get_client(request) as client:
        file = client.file(id).get(fields=('name',))
        filename = file['name']
        content = file.content()
        type, encoding = mimetypes.guess_type(filename)
        if type is None:
            type = 'application/octet-stream'
        response = HttpResponse(content)
        response['Content-Type'] = type
        response['Content-Length'] = str(len(content))
        if encoding is not None:
            response['Content-Encoding'] = encoding
        # To inspect details for the below code, see http://greenbytes.de/tech/tc2231/
        if u'WebKit' in request.META['HTTP_USER_AGENT']:
            # Safari 3.0 and Chrome 2.0 accepts UTF-8 encoded string directly.
            filename_header = 'filename=%s' % filename.encode('utf-8')
        elif u'MSIE' in request.META['HTTP_USER_AGENT']:
            # IE does not support internationalized filename at all.
            # It can only recognize internationalized URL, so we do the trick via routing rules.
            filename_header = ''
        else:
            # For others like Firefox, we follow RFC2231 (encoding extension in HTTP headers).
            filename_header = 'filename*=UTF-8\'\'%s' % urllib.quote(filename.encode('utf-8'))
        response['Content-Disposition'] = 'attachment; ' + filename_header
        return response
    return redirect('box')

def file_download(request, id):
    with get_client(request) as client:
        return redirect(client.file(id).content_url())
    return redirect('box')


@require_POST
@csrf_exempt
def box_view_file(request):
    view_api = boxview.BoxView(settings.BOX_VIEW_API_KEY)
    with get_client(request) as client:
        file = client.file(request.POST['file_id'])
        name = file.get(fields=('name',))['name']
        view_doc = view_api.create_document(url=file.content_url(),
                                            name=name)
        return JsonResponse(view_doc)
    return redirect('box')

@require_POST
@csrf_exempt
def box_view_session(request):
    view_api = boxview.BoxView(settings.BOX_VIEW_API_KEY)
    try:
        return JsonResponse(view_api.create_session(request.POST['document_id'],
                                                    is_downloadable=True))
    except boxview.RetryAfter as e:
        print "session retry after", e.seconds
        time.sleep(e.seconds) # waiting for next call
        return JsonResponse({'status': 'much undone'}, status=202)
