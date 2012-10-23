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
import pytz
import logging

logger= logging.getLogger(__name__)

def set_user_location(user,request):
    if 'lat' in request.GET and 'lon' in request.GET:
        lat = float(request.GET['lat'])
        lon = float(request.GET['lon'])
        user.current_location = (lat,lon) 
        g = geocoders.Google()
        loc, (lat, lng) = g.geocode(str(lat)+", " + str(lon),exactly_one=False)[0] 
        #logger.debug(str(user.current_location))
        user.location_name = loc
        #TODO figure out a better way to do this 
        nyc = pytz.timezone("America/New_York")
        user.timezone=nyc
    else:
        g = geocoders.Google()
        loc, (lat, lng) = g.geocode("08540",exactly_one=False)[0] 
        user.current_location = (float(lat),float(lng)) 
        nyc = pytz.timezone("America/New_York")
        user.timezone=nyc
        user.location_name = loc
        logger.debug("Centering user in Princeton, NJ by default")
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
    #logger.debug('Creating a new device')
    deviceID=request.GET['deviceID']
    #logger.debug('device id is ' + str(deviceID))
    try:
        device = Device.objects.create(deviceID=deviceID,os=1,model=1, manufacturer =0)
    except Exception as e:
        logger.debug(str(e))
#    logger.debug('creation done')
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

class RegistrationFailed(Exception):
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
        #if not user.is_superuser:
        #    raise AuthorizationError("User not authorized to edit")
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
    except Exception as e:
        logger.error('Error in generating a fake user!' + str(e) + str(maxid))  
        raise('Error in generating a fake user!')
    return genuser
        
def create_asuser(user,device):
    if AllsortzUser.objects.filter(device=device).count() > 0:
        AllsortzUser.objects.filter(device=device).delete()
    asuser =  AllsortzUser.objects.create(user=user,device=device,metric=False,distance_threshold=DISTANCE,registered=False)    
    return asuser


def register_asuser(user, newUname, password, email, deviceID):
    asuser = AllsortzUser.objects.get(user=user)
    device = Device.objects.filter(deviceID=deviceID)[0]
    
    if password != '':
        user.set_password(password)
    else:
      pass

    if not asuser.registered: 
        if newUname != '':
            user.username = newUname
        else:
            raise RegistrationFailed('Username should not be blank.')
    else:
      logger.debug('Updating the user ' + str(asuser.user))
      pass

    if email != '':
        user.email = email
    else:
        raise RegistrationFailed('Email should not be blank!')
    user.save()
    
    asuser.registered = True
    asuser.save()
    return user

def authenticate_api_request(request):
#    logger.debug('authenticating user')
    if 'uname' not in request.GET or 'password' not in request.GET or 'deviceID' not in request.GET:
        logger.error("Username and password not specified in request URL")
        raise AuthenticationFailed("Username and password not specified in request URL")
    else:
        uname = request.GET['uname']
        password = request.GET['password']
        deviceID = request.GET['deviceID']
    
    
#    logger.debug('uname is ' + str(uname) + ' password is ' + str(password))
    #using only the device ID
    try:
        device = Device.objects.get(deviceID=deviceID)
    except Device.DoesNotExist:
        device = create_device(request)
#        logger.debug('device created' + str(device))  
    
#    logger.debug("device is " + str(device))
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
            msg = 'user with username ' + str(uname) + ' not found'
            logger.error(msg)   
            raise AuthenticationFailed(msg)


    #auth the user by device alone   
    else:            
        if AllsortzUser.objects.filter(device=device).count() == 0:
            logger.debug('creating an ASUSER')
            logger.debug('Creating a new AllSortz User')
            genuser = create_fake_user()  
            asuser = create_asuser(genuser, device)
                
        else:
            asuser = AllsortzUser.objects.get(device=device) 
    
    
    logger.debug('authenticate user ' + str(asuser.user))
    user = authenticate(username=asuser.user, password=password)
    if not  user:
        raise AuthenticationFailed('Incorrect username password combination')
    
    login(request, user)
    set_user_location(user, request)
    logger.info('Authenticate as ' + str(user.current_location))
    return user
        

        
