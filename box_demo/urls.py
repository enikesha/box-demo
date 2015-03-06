from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'main.views.index', name='index'),
    url(r'^box/$', 'main.views.box', name='box'),
    url(r'^box/oauth2/$', 'main.views.box_oauth2', name='box_oauth2'),
    url(r'^edit/$', 'main.views.note_list', name='note_list'),
    url(r'^edit/add/$', 'main.views.note_add', name='note_add'),
    url(r'^edit/(?P<pk>\d+)/$', 'main.views.note_edit', name='note_edit'),
    url(r'^edit/(?P<pk>\d+)/delete/$', 'main.views.note_delete', name='note_delete'),
    url(r'^about/$', 'main.views.about', name='about'),
    url(r'^metadata/$', 'main.views.metadata', name='metadata'),
    url(r'^metadata/download/(?P<id>\d+)/$', 'main.views.file_download', name='metadata_download'),
    url(r'^metadata/template/select/$', 'main.views.metadata_select_template', name='metadata-select-template'),
    url(r'^metadata/templates/$', 'main.views.metadata_set_templates', name='metadata-set-templates'),
    url(r'^view/file/$', 'main.views.box_view_file', name='box-view-file'),
    url(r'^view/session/$', 'main.views.box_view_session', name='box-view-session'),
    url(r'^folder/(?P<folder_id>\d+)/items/$', 'main.views.folder_items', name='folder-items'),

    url(r'^admin/', include(admin.site.urls)),
)
