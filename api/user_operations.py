'''
Created on Aug 30, 2012

@author: zouf
'''
from api.models import AllsortzUser
from django.contrib.auth.models import User

def get_user_profile(user,auth=False):
    result = dict()
    try:
        asuser = AllsortzUser.objects.get(user=user)
        result['profilePic'] =  asuser.profile_photo.image_medium.url
    except Exception as e:
        print('error in getting profile pic ' + str(e))
        pass
    return result  
