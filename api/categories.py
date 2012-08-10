'''
Created on Aug 1, 2012

@author: zouf
'''
from api.models import Tag, BusinessCategory
from django.contrib.auth.models import User
from wiki.models import Page

def get_default_user():
    try:
        user = User.objects.get(username='matt')
    except:
        user = User(first_name='Matt', email='matty@allsortz.com', username='zouf')
        user.set_password("testing")
        user.save()
        
    return user

def add_tag_to_bus(b,tag,user=get_default_user()):    
    try: 
        bustag = BusinessCategory.objects.get(tag=tag,business=b)
    except:
        bustag = BusinessCategory.objects.create(tag=tag,business=b)
    
    try:
        Page.objects.get(category=bustag)
    except Page.DoesNotExist:
        pg = Page(name=tag.descr,category = bustag)
        pg.save()
        
def is_master_summary_tag(t): 
    if t == get_master_summary_tag():
        return True
    return False
    
    
def get_master_summary_tag():
    try:
        tag = Tag.objects.get(descr="The Bottom Line")
    except:
        tag = Tag.objects.create(descr="The Bottom Line", creator=get_default_user())
    return tag
