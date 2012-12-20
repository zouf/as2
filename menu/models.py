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
import wiki.models.article
import StringIO
import datetime
import simplejson
import urllib
import urllib2

AMOUNTS = (
       (u'L', u'Low'),
       (u'M', u'Medium'),
       (u'H', u'High'),
       (u'N', u'None'),
       (u'U', u'Unknown'),
)
    
BOOLEAN = (
       (u'N', u'No'),
       (u'Y', u'Yes'),
       (u'U', u'Unknown'),
) 

AVAILABILITY = (
       (u'B', u'Breakfast'),
       (u'L', u'Lunch'),
       (u'D', u'Dinner'),
       (u'LN', u'Late-Night'),
       (u'AL', u'Always'),
       (u'O', u'Other'),
       (u'U', u'Unknown'),
)


REDMEAT =  (
       (u'AN', u'Angus'),
       (u'GN', u'Grain Fed'),
       (u'GS', u'Grass Fed'),
       (u'Y', u'Yes'),
       (u'N', u'None'),
       (u'U', u'Unknown'),
)


''' A photo. To be associated with a business or a user '''
class  BasePhoto(models.Model):
    user = models.ForeignKey(User,db_index=True) 
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
            #logger.debug(imgFile)
            if imgFile.mode not in ('L', 'RGB'):
                imgFile = imgFile.convert('RGB')
            
            #Save a thumbnail for each of the given dimensions
            #The IMAGE_SIZES looks like:
            IMAGE_SIZES = {'image'    : (320, 120),
                           'image_medium'    : (225,225),
                           'image_thumb'    : (125,125)}
    
            #each of which corresponds to an ImageField of the same name
            for field_name, size in IMAGE_SIZES.iteritems():
                width, height = imgFile.size
                
                #if width > height:
                #    fitSize = (height, height)
                #else:
                #    fitSize = (width,width)
                fitSize = size 
               
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
    

   # Create your models here.
class InterestedBusiness(models.Model):
    name = models.CharField('Restaurant Name',max_length=250)
    description = models.TextField('Description')
    owner = models.ForeignKey(User,null=True)
    date = models.DateTimeField(auto_now=True)
    search = SphinxSearch()
    lat = models.FloatField()
    lon = models.FloatField()
    geom = models.PointField()

    address = models.CharField('Address', max_length=250)
    city = models.CharField(max_length=100)
    # Right now: America centric 
    state = USStateField()  
    zipcode = models.CharField('Zipcode', max_length=10,blank=True)
    phone = PhoneNumberField('Phone',blank=True)
    url = models.URLField('URL')
        
    objects = models.GeoManager()
    def __unicode__(self):
        return self.name
    
    #gets distance between this business and a user
    def get_distance(self,user):
        if user.current_location:
            return distance.distance(user.current_location,(self.lat,self.lon))
        else:
            return None

    
    def save(self):
        
        #dont redo this if lat and lng is set
        if (not self.lat and not self.lon) or (self.lat == 0 and self.lon==0):
            
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
        else:
            #use existing lat lng
            lat = self.lat
            lng = self.lon
            
        if lat and lng:
            self.lat = lat
            self.lon = lng 
            self.geom = fromstr('POINT('+str(self.lon)+ ' '+str(self.lat)+')', srid=4326)
            self.point = fromstr('POINT('+str(self.lon)+ ' '+str(self.lat)+')')
        else:
            self.lat = 0
            self.lon = 0 
            self.geom = fromstr('POINT('+str(self.lon)+ ' '+str(self.lat)+')', srid=4326)
            self.point = fromstr('POINT('+str(self.lon)+ ' '+str(self.lat)+')')
        super(InterestedBusiness, self).save()
    class Admin:
        pass
    



class MenuItem(models.Model):
    business = models.ForeignKey('menu.InterestedBusiness', related_name='menuitem')
    name = models.CharField("Dish Name",max_length=60,db_index=True)
    description = models.TextField("Description of Dish")
    category = models.CharField("Dish Type (e.g. Appetizer)",max_length=60,db_index=True)
    meal = models.CharField("Meal",max_length=2,choices=AVAILABILITY,default='U')
    price = models.DecimalField("Price",max_digits=10, decimal_places=2,null=True)
    
    
    
    class Admin:
        pass

class NutritionInfo(models.Model):
  menuitem = models.OneToOneField(MenuItem, related_name='nutrition')
  calories = models.CharField("Calories",max_length=2,choices=AMOUNTS,default='U')
  fat = models.CharField("Total Fat",max_length=2,choices=AMOUNTS,default='u')
  saturatedfat = models.CharField("Saturated Fat",max_length=2,choices=AMOUNTS,default='U')
  transfat = models.CharField("Trans Fat",max_length=2,choices=AMOUNTS,default='U')
  carbs = models.CharField("Carbs",max_length=2,choices=AMOUNTS, default='U')
  protein = models.CharField("Protein",max_length=2,choices=AMOUNTS,default='U') 
  sodium = models.CharField("Sodium",max_length=2,choices=AMOUNTS,default='U') 
  sugar = models.CharField("Sugar",max_length=2,choices=AMOUNTS,default='U')
  highfructose = models.CharField("High Fructose Corn Syrup",max_length=2,choices=AMOUNTS,default='U')
  fiber = models.CharField("Fiber",max_length=2,choices=AMOUNTS,default='U')
  wholegrain = models.CharField("Whole Grain",max_length=2,choices=AMOUNTS,default='U')
  cholesterol = models.CharField("Cholesterol", max_length=2,choices=AMOUNTS,default='U')
  def attrs(self):
    for field in self._meta.fields:
      if field.name != 'menuitem' and field.name != 'id':
        yield field.verbose_name, getattr(self, field.name)
    

class OtherRestrictions(models.Model):
    menuitem = models.OneToOneField(MenuItem,related_name='otherinfo')
    #booleans to check for meats
    msg = models.CharField('Contains MSG',max_length=2,choices=BOOLEAN,default='U')
    chicken = models.CharField('Contains chicken',max_length=2,choices=BOOLEAN,default='U')
    fish = models.CharField('Contains fish',max_length=2,choices=BOOLEAN,default='U')
    shellfish = models.CharField('Contains shellfish',max_length=2,choices=BOOLEAN,default='U')
    redmeat = models.CharField('Red Meat',max_length=2,choices=REDMEAT,default='U')

   #sustainability 
    local = models.CharField('All Local',max_length=2,choices=BOOLEAN,default='U')
    organic = models.CharField('Organic',max_length=2,choices=BOOLEAN,default='U')
    natural = models.CharField('Natural',max_length=2,choices=BOOLEAN,default='U')
    
    
    #ethnic / cultural / social restrictions
    hallal = models.CharField('Hallal',max_length=2,choices=BOOLEAN,default='U')
    kosher = models.CharField('Kosher',max_length=2,choices=BOOLEAN,default='U')
    vegan = models.CharField('Vegan',max_length=2,choices=BOOLEAN,default='U')
    pescetarian = models.CharField('Pescetarian',max_length=2,choices=BOOLEAN,default='U')
    vegetarian = models.CharField('Vegetarian',max_length=2,choices=BOOLEAN,default='U')
    def attrs(self):
      for field in self._meta.fields:
        if field.name != 'menuitem' and field.name != 'id':
          yield field.verbose_name, getattr(self, field.name)
 



class AllergyInfo(models.Model):
  menuitem = models.OneToOneField(MenuItem, related_name='allergy')
  peanut_free = models.CharField("Peanut Free",max_length=2,choices=BOOLEAN,default='U')
  gluten_free = models.CharField("Gluten Free",max_length=2,choices=BOOLEAN,default='U')
  treenut_free = models.CharField("Treenut Free",max_length=2,choices=BOOLEAN,default='U')
  soy_free = models.CharField("Soy Free", max_length=2,choices=BOOLEAN,default='U')
  dairy_free = models.CharField("Dairy Free",max_length=2,choices=BOOLEAN,default='U')
  sesame_free = models.CharField("Sesame Free",max_length=2,choices=BOOLEAN,default='U')
  lactose_free = models.CharField("Lactose Free",max_length=2,choices=BOOLEAN,default='U')
  def attrs(self):
    for field in self._meta.fields:
      if field.name != 'menuitem' and field.name != 'id':
        yield field.verbose_name, getattr(self, field.name)
 

class BusinessPhoto(BasePhoto):
  business = models.ForeignKey(InterestedBusiness)

class DishPhoto(BasePhoto):
  menuitem  = models.ForeignKey(MenuItem)

