'''
Created on Jul 26, 2012

@author: zouf
'''

from api.models import AllsortzUser, Device, OS_TYPES, MODEL_TYPES,\
    MANUFACTURER_TYPES
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.views import login
from geopy import geocoders
from queries.views import DISTANCE
import logging

logger= logging.getLogger(__name__)

def set_user_location(user,request):
    if 'lat' in request.GET and 'lon' in request.GET:
        lat = request.GET['lat']
        lon = request.GET['lon']
        user.current_location = (lat,lon) 
    else:
        g = geocoders.Google()
        _, (lat, lng) = g.geocode("Princeton, NJ") 
        user.current_location = (lat,lng) 
        print("Centering user in Princeton, NJ by default")
    return user


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
    print('device id is ' + str(deviceID))
    try:
        device = Device.objects.create(deviceID=deviceID,os=1,model=1, manufacturer =0)
    except Exception as e:
        print(e)
    print('creation done')
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
    print('auth')
    if 'deviceID' in request.GET:   #using only the device ID
        deviceID = request.GET['deviceID']
        try:
            device = Device.objects.get(deviceID=deviceID)
        except Device.DoesNotExist:
            print('dev does not exist')
            device = create_device(request)
            print('dev created' + str(device))  
            
        print('here')
        try:
            asuser = AllsortzUser.objects.get(device=device)                 
        except AllsortzUser.DoesNotExist:
            logger.debug('Creating a new AllSortz User')
            maxid = User.objects.all().order_by("-id")[0]
            try:
                print('creating a fake user')
                genuser = User.objects.create(username="gen"+str(maxid))
                genuser.set_password("generated_password")
                genuser.save()
            except:
                
                logger.error('Error in generating a new user!')
            print('yoyo')
            asuser = AllsortzUser.objects.create(user=genuser,device=device,metric=False,distance_threshold=DISTANCE)
        
        
            
        
        
        print("An AllSortz user with device ID "+str(device.deviceID))
        newuser = authenticate(username=asuser.user, password="generated_password")
        login(request, newuser)
        
        user = newuser
    else:
        user = get_default_user()
        
    user = set_user_location(user, request)
    return user
        

        