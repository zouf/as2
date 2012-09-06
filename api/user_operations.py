'''
Created on Aug 30, 2012

@author: zouf
'''
from api.models import AllsortzUser
from django.contrib.auth.models import User
import api.views as view
import api.json_serializer as serial

def register_allsortz_user(user,uname,password,email): 
    if User.objects.filter(username=uname).count()> 0:
        return view.server_error('Username ' + str(uname) + ' taken')
    if User.objects.filter(email=email).count() > 0:
        return view.server_error('Email ' +str(email) + ' already in use')
       
    valid = True  
    if password != '':
        user.set_password('password')
    else:
        valid = False
    if uname != '':
        user.username = uname
    else:
        valid = False
    if email != '':
        user.email = email
    else:
        valid = False

    user.save()
    asuser = AllsortzUser.objects.get(user=user)

    if valid:
        asuser.registered = True
        
    return view.server_data(serial.get_user_details(user))

