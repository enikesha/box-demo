from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'main.views.index', name='index'),
    url(r'^box/$', 'main.views.box', name='box'),
    url(r'^edit/$', 'main.views.note_list', name='note_list'),
    url(r'^edit/add/$', 'main.views.note_add', name='note_add'),
    url(r'^edit/(?P<pk>\d+)/$', 'main.views.note_edit', name='note_edit'),
    url(r'^edit/(?P<pk>\d+)/delete/$', 'main.views.note_delete', name='note_delete'),
    url(r'^about/$', 'main.views.about', name='about'),

    url(r'^admin/', include(admin.site.urls)),
)
