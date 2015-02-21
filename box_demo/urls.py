from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', 'main.views.index', name='index'),
    url(r'^box/$', 'main.views.box', name='box'),
    url(r'^edit/$', 'main.views.edit', name='edit'),
    url(r'^about/$', 'main.views.about', name='about'),

    url(r'^admin/', include(admin.site.urls)),
)
