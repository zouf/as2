from django.contrib.auth.models import User
from django.db import models
from api.models import Tag

# Create your models here.




#decribes a listing   
class Query(models.Model):
    name = models.CharField(max_length=250)
    date = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User)
    
    #a query created by Us (developers)
    is_default = models.BooleanField()
    
    #weights for the sliders
    proximity = models.IntegerField()
    score = models.IntegerField()
    price = models.IntegerField()
    value = models.IntegerField()
    
    #part of allsortz network
    networked = models.BooleanField()
    #business has deal
    deal = models.BooleanField()
    #user has visited / not visited before
    visited = models.BooleanField()
    unvisited = models.BooleanField()
    
    #The text built into this search 
    text = models.CharField(max_length=250)
    def __unicode__(self):
        return self.name


class QueryTag(models.Model):
    query = models.ForeignKey(Query)
    tag = models.ForeignKey(Tag)


class UserQueryRelation(models.Model):
    user = models.ForeignKey(User)
    query = models.ForeignKey(Query)
    favorite = models.BooleanField()
    