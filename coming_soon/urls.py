from django.conf.urls import url, patterns
from coming_soon.views import survey_detail
urlpatterns = patterns('coming_soon.views', 
 (r'^/?$', 'coming_soon'),
 (r'^health/?$', 'survey_detail'),
 (r'^login$', 'login_user'),
 (r'^logout$', 'logout_view'),


        (r'^learn/?$', 'learn'), 
        (r'^contact/?$', 'contact'), 
        (r'^about/?$', 'about'), 
        (r'^allergy/?$', 'survey_detail')
        )


