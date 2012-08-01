from PIL import Image
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos.factory import fromstr

from django.contrib.localflavor.us.models import USStateField, USPostalCodeField, PhoneNumberField 
from django.core.files.base import ContentFile
from django.utils.encoding import smart_str
from geopy import distance
from os.path import basename
import StringIO
import datetime
import simplejson
import urllib
import urllib2

#from django.contrib.auth.models import User
#from ratings.models import Business
# Create your models here.

class Business(models.Model):
    name = models.CharField(max_length=250)
    date = models.DateTimeField(auto_now=True)

    lat = models.FloatField()
    lon = models.FloatField()
    geom = models.PointField()

    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    

    # Right now: America centric 
    state = USStateField()  
    phone = PhoneNumberField()
    zipcode = models.CharField(max_length=10,blank=True)
    
    objects = models.GeoManager()
    def __unicode__(self):
        return self.name
    
    #gets distance between this business and a user
    def get_distance(self,user):
        if user.current_location:
            distance.distance(user.current_location,(self.lat,self.lon)).miles
        else:
            return None
        
    def save(self):
        loc = self.address + " " + self.city + ", " + self.state        
        location = urllib.quote_plus(smart_str(loc))
        dd = urllib2.urlopen("http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false" % location).read() 
        ft = simplejson.loads(dd)
        if ft["status"] == 'OK':
            lat = str(ft["results"][0]['geometry']['location']['lat']) 
            lng = str(ft["results"][0]['geometry']['location']['lng'])
            zipcode = None
            for jsonStr in ft["results"][0]['address_components']:
#                print jsonStr
                if 'types' in jsonStr:
                    print('types there')
                    for tp in jsonStr['types']:
                        if tp == "postal_code":
                            zipcode = jsonStr['long_name']
                            break
        
        print(zipcode)
        self.zipcode  = zipcode
        self.lat = lat
        self.lon = lng 
        self.geom = fromstr('POINT('+str(self.lon)+ ' '+str(self.lat)+')', srid=4326)
        
        super(Business, self).save()

class  Photo(models.Model):
    user = models.ForeignKey(User) 
    business = models.ForeignKey(Business)   
    is_default = models.BooleanField()

    def image_upload_to_profile(self, filename):
        today = datetime.datetime.today()
        return 'user_uploads/profilepics/%s/%s-%s-%s.%s.%s/profile/%s' % (self.user.username, today.year, today.month, today.day, today.hour, today.minute, basename(filename))
            
    def image_upload_to_thumb(self, filename):
        today = datetime.datetime.today()
        return 'user_uploads/%s/%s-%s-%s.%s.%s/web/%s' % (self.user.username, today.year, today.month, today.day, today.hour, today.minute, basename(filename))
    
    def image_upload_to_medium(self, filename):
        today = datetime.datetime.today()
        return 'user_uploads/%s/%s-%s-%s.%s.%s/medium/%s' % (self.user.username, today.year, today.month, today.day, today.hour, today.minute, basename(filename))
#    
#    def image_upload_to_mini(self,filename):
#        today = datetime.datetime.today()
#        return 'user_uploads/%s/%s-%s-%s.%s.%s/thumb2/%s' % (self.user.username, today.year, today.month, today.day, today.hour, today.minute, filename)
#    
    image = models.ImageField(upload_to=image_upload_to_profile)
    image_medium = models.ImageField(upload_to=image_upload_to_medium)
    image_thumb = models.ImageField(upload_to=image_upload_to_thumb)

    #image_mini = models.ImageField(upload_to=image_upload_to_mini)

    date = models.DateTimeField(auto_now=True)
    
    
    title = models.CharField(blank=True, max_length=300)
    caption = models.TextField(blank=True)
    def save(self, isUpload):
        #Original photo
        
        if isUpload:
            imgFile = Image.open(self.image)
        else:
            imgFile = Image.open(str(self.image))
        #Convert to RGB
        print(imgFile)
        if imgFile.mode not in ('L', 'RGB'):
            imgFile = imgFile.convert('RGB')
        
        #Save a thumbnail for each of the given dimensions
        #The IMAGE_SIZES looks like:
        IMAGE_SIZES = {'image'    : (225, 225),
                       'image_medium'    : (125,125),
                       'image_thumb'    : (50,50)}

        #each of which corresponds to an ImageField of the same name
        for field_name, size in IMAGE_SIZES.iteritems():
            field = getattr(self, field_name)
            working = imgFile.copy()
            working.thumbnail(size, Image.ANTIALIAS)
            fp=StringIO.StringIO()
            working.save(fp, "png", quality=95)
            cf = ContentFile(fp.getvalue())
            field.save(name=self.image.name, content=cf, save=False);
        
        #Save instance of Photo
        super(Photo, self).save()
        
class Tag(models.Model):
    creator = models.ForeignKey(User)
    date = models.DateTimeField(auto_now=True)
    descr = models.TextField(max_length=100)
    icon = models.TextField(max_length=100)
    
class BusinessCategory(models.Model):
    business = models.ForeignKey(Business)
    tag = models.ForeignKey(Tag)

class UserSubscription(models.Model):
    user = models.ForeignKey(User)
    tag = models.ForeignKey(Tag)


#Describes a device that a user owns. Right now, the only type of device shouldbe iphones




class Device(models.Model):
    os = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    deviceID = models.IntegerField()

#A wrapper class for us that allows us to describe 
# important attributes associated with a user (devices, deals, preferences, etc.)

class AllsortzUser(models.Model):
    distance_threshold = models.IntegerField()
    user = models.OneToOneField(User)
    metric = models.BooleanField()
    device = models.ForeignKey(Device)

    def __unicode__(self):
        return self.user.username    
    

''' Begin offers and deals '''
#base class of all deals / offers
class Offer(models.Model):
    business = models.ForeignKey(Business)
    description = models.CharField(max_length=1000)
    restricitons = models.CharField(max_length=1000)

    created_on = models.DateTimeField(auto_now=True)
    
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()  

#what the business is offering as a deal
class BusinessDeal(Offer):
    cost = models.IntegerField()
    number_allocated = models.IntegerField()
    number_used = models.IntegerField()
    
#What you can do to get something
class BusinessAction(Offer):
    reward_deal = models.ForeignKey(BusinessDeal)
    reward_value = models.IntegerField()
    number_allocated = models.IntegerField()
    number_used = models.IntegerField()

    
class ASUserDeal(models.Model):
    ASuser = models.ForeignKey(AllsortzUser)
    businessdeal = models.ForeignKey(BusinessDeal)
    #YYYY-MM-DD HH:MM
    received_on = models.DateTimeField() 
    used_on = models.DateTimeField() 

#A user action such as a check-in, or a purchase
class ASUserAction(models.Model):
    ASuser = models.ForeignKey(AllsortzUser)
    action = models.ForeignKey(BusinessAction)
    description = models.CharField(max_length=1000)
    location = models.PointField()
    
    #YYYY-MM-DD HH:MM
    completed_on = models.DateTimeField() 

''' End offers and deals '''
    
''' types of discussions '''
#discussion-related items
class Discussion(models.Model):
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now=True)
    reply_to = models.ForeignKey('self', related_name='replies', 
        null=True, blank=True)
    content = models.TextField(max_length=2000)    

class CategoryDiscussion(Discussion):
    businesstag = models.ForeignKey(BusinessCategory)
  
class BusinessDiscussion(Discussion):
    business = models.ForeignKey(Business)

class PhotoDiscussion(Discussion):
    photo = models.ForeignKey(Photo)

''' end types of discussions '''


'''   Types of ratings  '''
class Rating(models.Model):
    user = models.ForeignKey(User)
    rating = models.IntegerField()
    
class DiscussionRating(Rating):
    discussion = models.ForeignKey(Discussion)
    
class PhotoRating(Rating):
    photo = models.ForeignKey(Photo)
    
class CategoryRating(Rating):
    category = models.ForeignKey(BusinessCategory)
    
class BusinessRating(Rating):
    business = models.ForeignKey(Business)
    
''' end types of ratings '''  

