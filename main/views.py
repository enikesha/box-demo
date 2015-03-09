import os
import time
from contextlib import contextmanager
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from boxsdk.auth.oauth2 import OAuth2
from boxsdk.client import Client
from boxsdk.exception import BoxAPIException, BoxOAuthException
from boxsdk.object.file import File
from boxview import boxview

from .models import *

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

def File__copy(self, parent_folder, name=None):
    """Copy the item to the given folder.
    :param parent_folder:
    The folder to which the item should be copied.
    :type parent_folder:
    :class:`Folder`
    """
    import json
    url = self.get_url('copy')
    data = {
        'parent': {'id': parent_folder.object_id}
    }
    if name is not None:
        data['name'] = name
    box_response = self._session.post(url, data=json.dumps(data))
    response = box_response.json()
    return self.__class__(
        session=self._session,
        object_id=response['id'],
        response_object=response,
    )
File.copy = File__copy

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

def get_session(request):
    oauth = OAuth2(client_id=settings.BOX_CLIENT_ID,
                   client_secret=settings.BOX_CLIENT_SECRET)
    auth_url, csrf_token = oauth.get_authorization_url(request.build_absolute_uri(reverse('oauth2')))
    request.session['box_csrf_token'] = csrf_token
    return redirect(auth_url)

def oauth2(request):
    oauth = OAuth2(client_id=settings.BOX_CLIENT_ID,
                   client_secret=settings.BOX_CLIENT_SECRET)
    state = request.GET.get('state')
    code = request.GET.get('code')

    assert state == request.session['box_csrf_token']
    access_token, refresh_token = oauth.authenticate(code)

    request.session['access_token'] = access_token
    request.session['refresh_token'] =  refresh_token

    return redirect('index')

def index(request):
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

        templates_id = request.session.get('templates_folder')
        return render(request, "metadata.html", locals())
    # In case OAuth error
    return get_session(request)

def about(request):
    return render(request, "about.html")


def file_download(request, id):
    with get_client(request) as client:
        return redirect(client.file(id).content_url())
    return get_session(request)


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
    return JsonResponse({'status': 'not authenticated'}, status=403)

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

@require_POST
@csrf_exempt
def metadata_set_templates(request):
    with get_client(request) as client:
        folder_id = request.POST['folder_id']
        folder = client.folder(folder_id).get(fields=('name',))
        request.session['templates_folder'] = folder_id
        return JsonResponse({'id':folder_id})
    return JsonResponse({'status': 'not authenticated'}, status=403)

@require_POST
@csrf_exempt
def metadata_select_template(request):
    with get_client(request) as client:
        template = client.file(request.POST['template_id']).get(fields=('name',))
        file = client.file(request.POST['file_id']).get(fields=('name','parent'))
        parent = client.folder(file['parent']['id'])
        name, _ = os.path.splitext(file['name'])
        _, ext = os.path.splitext(template['name'])
        metadata = template.copy(parent, u"{0}_metadata{1}".format(name, ext))
        return JsonResponse({'id': metadata['id']})
    return JsonResponse({'status': 'not authenticated'}, status=403)

def folder_items(request, folder_id):
    with get_client(request) as client:
        folder = client.folder(folder_id)
        items = folder.get_items(limit=100, fields=('id','name','type'))
        return JsonResponse([{'id':i['id'],
                              'name': i['name'],
                              'type': i['type']} for i in items],
                            safe=False)
    return JsonResponse({'status': 'not authenticated'}, status=403)
