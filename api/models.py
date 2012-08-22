from PIL import Image, ImageOps
from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos.factory import fromstr
from django.contrib.localflavor.us.models import USStateField, PhoneNumberField
from django.core.files.base import ContentFile
from django.utils.encoding import smart_str
from djangosphinx.models import SphinxSearch
from geopy import distance
from os.path import basename
import StringIO
import datetime
import simplejson
import urllib
import urllib2




''' A business can be any kind of merchant '''
class Business(models.Model):
    name = models.CharField(max_length=250)
    date = models.DateTimeField(auto_now=True)
    search = SphinxSearch()
    lat = models.FloatField()
    lon = models.FloatField()
    geom = models.PointField()

    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    url = models.URLField()
    
    
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
            return distance.distance(user.current_location,(self.lat,self.lon)).miles
        else:
            return None
        
    def average_price(self):
        return BusinessMeta.objects.get(business=self).average_price
    
    def serves_alcohol(self):
        return BusinessMeta.objects.get(business=self).serves
    
    def has_wifi(self):
        return BusinessMeta.objects.get(business=self).wifi
    
    def hours(self):
        return BusinessMeta.objects.get(business=self).hours
    
    
    
    def save(self):
        loc = self.address + " " + self.city + ", " + self.state        
        location = urllib.quote_plus(smart_str(loc))
        dd = urllib2.urlopen("http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false" % location).read() 
        ft = simplejson.loads(dd)
        zipcode = None
        lat = None
        lng = None
        if ft["status"] == 'OK':
            lat = str(ft["results"][0]['geometry']['location']['lat']) 
            lng = str(ft["results"][0]['geometry']['location']['lng'])
            zipcode = None
            for jsonStr in ft["results"][0]['address_components']:
#                print jsonStr
                if 'types' in jsonStr:
                    for tp in jsonStr['types']:
                        if tp == "postal_code":
                            zipcode = jsonStr['long_name']
                            break
       
        if zipcode is not None:
            self.zipcode  = zipcode
        else:
            self.zipcode = ''
            
        if lat and lng:
            self.lat = lat
            self.lon = lng 
            self.geom = fromstr('POINT('+str(self.lon)+ ' '+str(self.lat)+')', srid=4326)
        else:
            self.lat = 0
            self.lon = 0 
            self.geom = fromstr('POINT('+str(self.lon)+ ' '+str(self.lat)+')', srid=4326)

        super(Business, self).save()
    class Admin:
        pass
    


class BusinessCache(models.Model):
    business = models.ForeignKey(Business)
    cachedata = models.CharField(max_length=1500)
    
class BusinessMeta(models.Model):
    average_price = models.IntegerField()
    wifi = models.NullBooleanField()
    serves = models.NullBooleanField()
    hours = models.CharField(max_length=100)

    business = models.ForeignKey(Business)


''' A photo. To be associated with a business or a user '''
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
    class Admin:
        pass
    def save(self, isUpload,isTextMod):
        #Original photo
        if not isTextMod:
            if isUpload:
                imgFile = Image.open(self.image)
            else:
                imgFile = Image.open(str(self.image))
            #Convert to RGB
            #print(imgFile)
            if imgFile.mode not in ('L', 'RGB'):
                imgFile = imgFile.convert('RGB')
            
            #Save a thumbnail for each of the given dimensions
            #The IMAGE_SIZES looks like:
            IMAGE_SIZES = {'image'    : (225, 225),
                           'image_medium'    : (125,125),
                           'image_thumb'    : (80,80)}
    
            #each of which corresponds to an ImageField of the same name
            for field_name, size in IMAGE_SIZES.iteritems():
                width, height = imgFile.size
                
                if width > height:
                    fitSize = (height, height)
                else:
                    fitSize = (width,width)
                
               
                #img.thumbnail(size, Image.ANTIALIAS)              
                
                field = getattr(self, field_name)
                working = imgFile.copy()
                working = ImageOps.fit(working,fitSize, Image.ANTIALIAS)
                working.thumbnail(size,Image.ANTIALIAS)
                fp=StringIO.StringIO()
                working.save(fp, "png", quality=95)
                cf = ContentFile(fp.getvalue())
                field.save(name=self.image.name, content=cf, save=False);
            
        #Save instance of Photo
        super(Photo, self).save()
     
''' A tag. It's a topic / discussion about a business as well as
annotate a user's interests ''' 
class Tag(models.Model):
    creator = models.ForeignKey(User)
    search = SphinxSearch()
    date = models.DateTimeField(auto_now=True)
    descr = models.TextField(max_length=100)
    icon = models.TextField(max_length=100)
    class Admin:
        pass
    def __unicode__(self):
        return self.descr
    
    
''' A tag. It's a topic / way to categorize businesses as well as
annotate a user's interests ''' 
class TypeOfBusiness(models.Model):
    search = SphinxSearch()
    creator = models.ForeignKey(User)
    date = models.DateTimeField(auto_now=True)
    descr = models.TextField(max_length=100)
    icon = models.TextField(max_length=100)
    class Admin:
        pass
    def __unicode__(self):
        return self.descr
    
''' A tag. It's a topic / way to categorize businesses as well as
annotate a user's interests ''' 
class BusinessType(models.Model):
    business = models.ForeignKey(Business)
    bustype = models.ForeignKey(TypeOfBusiness)
    def __unicode__(self):
        return str(self.business) + ": " + str(self.bustype)
    

    
''' A relationship between business and tag 
These are the business' sorts '''
class BusinessCategory(models.Model):
    business = models.ForeignKey(Business)
    tag = models.ForeignKey(Tag)
    def __unicode__(self):
        return str(self.business) + ": " + str(self.tag)
    
    
''' A user's subscription to a particular  tag '''
class UserSubscription(models.Model):
    user = models.ForeignKey(User)
    tag = models.ForeignKey(Tag)


''' A user's favorite business '''
class UserFavorite(models.Model):
    user = models.ForeignKey(User)
    business = models.ForeignKey(Business)

#Describes a device that a user owns. Right now, the only type of device shouldbe iphones


''' Begin usage of ALLSORTZ users instead of regular users
AllSortz users should be used for any kind of transactions made through us. The AllSortz users
have a one-to-one mapping between Django users, but include / will include additional information such 
as associated devices, number of check-ins etc. '''
    
''' A device that a user owns '''
OS_TYPES = (
    (0, 'iOS 4'),
    (1, 'iOS 5'),
    (2, 'iOS 6'),
    (3, 'Android 2.2 (Froyo)'),
    (4, 'Android 2.3 (Gingerbread)'),
    (5, 'Android 4.0 (Ice Cream Sandwich)'),
    (6, 'Android 4.1 (Jelly Bean)'),
)

MODEL_TYPES = (
    (0, 'iPhone 4'),
    (1, 'iPhone 4s'),
    (2, 'iPhone (6th Generation)'),
)

MANUFACTURER_TYPES = (
    (0, 'Apple'),
    (1, 'Samsung'),
    (2, 'HTC'),
    (3, 'LG'),
    (4, 'Motorola'),
)
class Device(models.Model):
    os = models.IntegerField(choices=OS_TYPES)
    model = models.IntegerField(choices=MODEL_TYPES)
    manufacturer =  models.IntegerField(choices=MANUFACTURER_TYPES)
    deviceID = models.IntegerField()
    def get_os_name(self):
        return OS_TYPES[self.os][1] 
    
    def get_model_name(self):
        return MODEL_TYPES[self.model][1] 
    
    def get_manufacturer_name(self):
        return MANUFACTURER_TYPES[self.manufacturer][1] 
    
    class Admin:
        pass
    def __unicode__(self):
        return self.get_os_name() + " - " + self.get_manufacturer_name() + " " + self.get_model_name()


#A wrapper class for us that allows us to describe 
# important attributes associated with a user (devices, deals, preferences, etc.)

class AllsortzUser(models.Model):
    ''' The user can set thresholds for distance here '''
    distance_threshold = models.IntegerField()
    
    '''Map to Django user'''
    user = models.OneToOneField(User)

    ''' Use metric of standard '''
    metric = models.BooleanField(default=False)
    
    '''Device (if owned) '''
    device = models.ForeignKey(Device)
    class Admin:
        pass
    def __unicode__(self):
        return self.user.username    
    

''' Begin offers and deals '''
'''
An offer is something the business is giving away.
For example, the offer might give away a free sandwich, or a 50% off coupon.
Offers are achieved through actions. Actions provide you with coins which are used 
to actually *purchase* an offer. For example, an action like check-in might provide you
with 50 coins. The 50% off coupon at a restaurant might cost 40 coins. Thus, you can purchase
the coupon and have 10 coins leftover.
'''

'''Offer.objects.filter(business=<business>) will yield ALL offers at a business. '''
class Offer(models.Model):
    business = models.ForeignKey(Business)
    description = models.CharField(max_length=1000)
    restrictions = models.CharField(max_length=1000)

    created_on = models.DateTimeField(auto_now=True)
    
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()  
    
    ''' How many coins does it take to buy this deal? '''
    cost = models.IntegerField()
    
    ''' How many has the business allocated '''
    number_allocated = models.IntegerField()
    
    ''' How many have been used at the business '''
    number_used = models.IntegerField()
    class Admin:
        pass

''' A purchased offer '''
class ASUserOffer(models.Model):
    '''What user'''
    ASuser = models.ForeignKey(AllsortzUser)
    
    '''What offer'''
    offer = models.ForeignKey(Offer)
    
    '''purhcase price'''
    price = models.IntegerField()
    
    '''When purchased'''
    purchased_on = models.DateTimeField(auto_now=True)
    
    '''When used'''
    used_on = models.DateTimeField()  

    class Admin:
        pass
    

ACTION_TYPES = (
    (1, 'Check-in'),
    (2, 'Purchase'),
    (3, 'Referral'),
    (4, 'High Quality Review'),
)

''' Actions are class since they're the same no matter what the restaurant is.
A check-in is a check in. A user can check-in or buy 1000 sandwiches whereever they please. The assignemnt
of values as well as validity periods is left to the business
assigns  value to the actions '''
class ActionOption(models.Model):
    ''' The type of action. Hopefully there are only several '''
    action_type = models.IntegerField(choices=ACTION_TYPES)
    
    ''' brief description of what it takes to get the action '''
    description = models.CharField(max_length=1000)
    
    

''' Let's say the business wants to award users for actions. An instance
of this model will exist so that when a user completes an action of the appropriate type
at the appropriate business, we know if we can assign coins to the user '''
class BusinessAction(models.Model):
    ''' What action?'''
    action = models.ForeignKey(ActionOption)
    
    ''' What is the value of completing this action?'''
    value = models.IntegerField()
    
    '''When was this option created?'''
    created_on = models.DateTimeField(auto_now=True)
    
    '''Validitiy dates'''
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()  
    
    class Admin:
        pass

''' Whenever the user does something, like check in or make a purchase, we can assign the action here'''
class ASUserCompletedAction(models.Model):
    ''' Who completed the action '''
    ASuser = models.ForeignKey(AllsortzUser)
    
    '''What action?'''
    action = models.ForeignKey(ActionOption)
    
    ''' Where did the user complete the aciton? '''
    business = models.ForeignKey(Business)
    
    ''' a location (optional) that the user completed the action at'''
    geom = models.PointField()   
    
    ''' When was the action completed'''
    completed_on = models.DateTimeField(auto_now=True)

''' End offers and deals '''
    
    
    
''' types of discussions '''
#discussion-related items
class Discussion(models.Model):
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now=True)
    reply_to = models.ForeignKey('self', related_name='replies', 
        null=True, blank=True)
    content = models.TextField(max_length=2000)    
    class Admin:
        pass
    
class CategoryDiscussion(Discussion):
    businesstag = models.ForeignKey(BusinessCategory)
    class Admin:
        pass
    
class BusinessDiscussion(Discussion):
    business = models.ForeignKey(Business)
    class Admin:
        pass
    
class PhotoDiscussion(Discussion):
    photo = models.ForeignKey(Photo)
    class Admin:
        pass
    
''' end types of discussions '''


'''   Types of ratings  '''
class Rating(models.Model):
    user = models.ForeignKey(User)
    rating = models.FloatField()
    class Admin:
        pass
    
class DiscussionRating(Rating):
    discussion = models.ForeignKey(Discussion)
    class Admin:
        pass
    
class PhotoRating(Rating):
    photo = models.ForeignKey(Photo)
    class Admin:
        pass
    def __unicode__(self):
        return str(self.rating) + " : " + str(self.photo) + " - " + str(self.user) 
        
    
    
    
class CategoryRating(Rating):
    category = models.ForeignKey(BusinessCategory)
    class Admin:
        pass
    def __unicode__(self):
        return str(self.rating) + " : " + str(self.category) + " - " + str(self.user) 
    
class BusinessRating(Rating):
    business = models.ForeignKey(Business)
    class Admin:
        pass
    def __unicode__(self):
        return str(self.rating) + " : " + str(self.business) + " - " + str(self.user) 
    
''' end types of ratings '''  

