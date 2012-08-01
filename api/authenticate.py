'''
Created on Jul 26, 2012

@author: zouf
'''

from api.models import AllsortzUser, Device
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.views import login
from geopy import geocoders
from queries.views import DISTANCE
import logging

logger= logging.getLogger(__name__)

def get_default_user():
    try:
        user = User.objects.get(username='matt')
    except:
        user = User(first_name='Matt', email='matty@allsortz.com', username='zouf')
        user.set_password("testing")
        user.save()
        
    return user

def create_device(request):
    logger.debug('Creating a new device')
    deviceID=request.GET['deviceID']
    device = Device.objects.create(deviceID=deviceID)
    device.os = "ios"
    device.model = "iphone"
    device.manufacturer = "apple"
    return device

class AuthenticationFailed(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class AuthorizationError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)





def authorize_user(user, request, request_type):
    if request_type == "delete":
        if not user.is_superuser:
            raise AuthorizationError("User not authorized to delete")
        return True
    elif request_type == "get":
        return True
    elif request_type == "edit":
        if not user.is_superuser:
            raise AuthorizationError("User not authorized to delete")
        return True
    elif request_type == "add":
        return True
    elif request_type == "rate":
        return True
    elif request_type == "superuser":
        if not user.is_superuser:
            raise AuthorizationError("User not authorized to delete")
        return True
    else:
        raise AuthorizationError("Invalid request type")
        
def authenticate_api_request(request):
    if 'deviceID' in request.GET:   #using only the device ID
        deviceID = request.GET['deviceID']
        try:
            device = Device.objects.get(deviceID=deviceID)
        except Device.DoesNotExist:
            device = create_device(request)  
            
        
        try:
            asuser = AllsortzUser.objects.get(device=device)                 
        except AllsortzUser.DoesNotExist:
            logger.debug('Creating a new AllSortz User')
            maxid = User.objects.all().order_by("-id")[0]
            try:
                genuser = User.objects.create(username="gen"+str(maxid))
                genuser.set_password("generated_password")
                genuser.save()
            except:
                logger.error('Error in generating a new user!')
            asuser = AllsortzUser.objects.create(user=genuser,device=device,metric=False,distance_threshold=DISTANCE)
        
        
        print("An AllSortz user with device ID "+str(device.deviceID))
        newuser = authenticate(username=asuser.user, password="generated_password")
        login(request, newuser)
        g = geocoders.Google()
        _, (lat, lng) = g.geocode("Princeton, NJ") 
        request.user.current_location = (lat,lng) 
        return request.user
    else:
        user = get_default_user()
        g = geocoders.Google()
        _, (lat, lng) = g.geocode("Princeton, NJ") 
        user.current_location = (lat,lng) 
        print(user.current_location)
        
        return user
        

        