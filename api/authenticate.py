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
        print(str(user.current_location))
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
   
def create_fake_user():  
    maxid = User.objects.all().order_by("-id")[0]
    try:
        genuser = User.objects.create(username="gen"+str(maxid.id))
        genuser.set_password("generated_password")
        genuser.save()
    except: 
        logger.error('Error in generating a fake user!')  
        raise('Error in generating a fake user!')
        
def create_asuser(user,device):
    if AllsortzUser.objects.filter(device=device).count() > 0:
        AllsortzUser.objects.filter(device=device).delete()
    asuser =  AllsortzUser.objects.create(user=user,device=device,metric=False,distance_threshold=DISTANCE,registered=False)    
    return asuser
        
def authenticate_api_request(request):
    print('auth')
    if 'uname' not in request.GET or 'password' not in request.GET or 'deviceID' not in request.GET:
        logger.error("Username and password not specified in request URL")
        raise AuthenticationFailed("Username and password not specified in request URL")
    else:
        uname = request.GET['uname']
        password = request.GET['password']
    
    
    print('uname is ' + str(uname) + ' password is ' + str(password))
    if 'deviceID' in request.GET:   #using only the device ID
        deviceID = request.GET['deviceID']
        try:
            device = Device.objects.get(deviceID=deviceID)
        except Device.DoesNotExist:
            device = create_device(request)
            print('device created' + str(device))  
    
    print("device is " + str(device))
    if uname != 'none':
        try:
            user = User.objects.get(username=uname)      
            if AllsortzUser.objects.filter(device=device).count() == 0:
                asuser = create_asuser(user,device)
            else:
                asuser = AllsortzUser.objects.get(device=device)
                asuser.user = user
                asuser.save()
        except User.DoesNotExist:
            msg = 'user with username ' + str(uname) + ' str not found'
            logger.error(msg)   
            raise AuthenticationFailed(msg)


    #auth the user by device alone   
    else:            
        if AllsortzUser.objects.get(device=device).count() == 0:
            print('creating an ASUSER')
            logger.debug('Creating a new AllSortz User')
            genuser = create_fake_user()  
            create_asuser(genuser, device)
                
        else:
            asuser = AllsortzUser.objects.get(device=device) 
    
    
    print('authenticate user ' + str(asuser.user))
    user = authenticate(username=asuser.user, password=password)
    if not  user:
        raise AuthenticationFailed('Incorrect username password combination')
    
    login(request, user)
    set_user_location(user, request)
    logger.info('Authenticate as ' + str(user.current_location))
    return user
        

        