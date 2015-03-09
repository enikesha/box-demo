from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'main.views.index', name='index'),
    url(r'^oauth2/$', 'main.views.oauth2', name='oauth2'),
    url(r'^about/$', 'main.views.about', name='about'),
    url(r'^metadata/download/(?P<id>\d+)/$', 'main.views.file_download', name='metadata_download'),
    url(r'^metadata/template/select/$', 'main.views.metadata_select_template', name='metadata-select-template'),
    url(r'^metadata/templates/$', 'main.views.metadata_set_templates', name='metadata-set-templates'),
    url(r'^view/file/$', 'main.views.box_view_file', name='box-view-file'),
    url(r'^view/session/$', 'main.views.box_view_session', name='box-view-session'),
    url(r'^folder/(?P<folder_id>\d+)/items/$', 'main.views.folder_items', name='folder-items'),

    url(r'^admin/', include(admin.site.urls)),
)
