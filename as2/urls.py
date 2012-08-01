from as2 import settings
from as2.settings import APPEND_SLASH
from django.conf.urls import url, patterns, include
from django.contrib import admin


admin.autodiscover()

print settings.APPEND_SLASH

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('api.urls')),
    url(r'^wiki/', include('wiki.urls')),       
    


)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',  {'document_root':     settings.MEDIA_ROOT}),
		(r'^(?P<path>.*)$', 'django.views.static.serve',  {'document_root':     settings.MEDIA_ROOT}),
    )


