'''
Created on Jul 30, 2012

@author: zouf
'''
from api.models import Photo
from as2 import settings
from urllib import urlretrieve

'''
Created on Jul 27, 2012

@author: zouf
'''

DEFAULT_IMAGE = 'https://s3.amazonaws.com/allsortz/icon.png'

#CODE NEEDS TO BE REFACTORED
def get_photo_url_medium(b):
    if b.profile_photo == None:
        return DEFAULT_IMAGE
    return b.profile_photo.image_medium.url
  

def get_photo_url_large(b):
    if b.profile_photo == None:
        return DEFAULT_IMAGE
    return b.profile_photo.image.url

def get_photo_id(b):
    return b.profile_photo.id





def add_photo_by_url(phurl, business,user,default,caption,title):
    outpath =settings.STATIC_ROOT+str(business.id)+"_"+str(business.city)+"_"+str(business.state)
    print('retrieve')
    
    try:
        urlretrieve(phurl, outpath)
        
    except Exception as e:
        print('exception')
        print(e)
        return None
    print('done')
    p = Photo(user=user, business=business, image=outpath, title=title, caption=caption,is_default=default)
    p.save(isUpload = False,isTextMod = False)
    business.profile_photo = p
    business.save()
    print(p)
    return p

def add_photo_by_upload(img,b,user,default,caption,title):
    bp =Photo(user=user, business=b, image=img, title=title, caption=caption,is_default=default)
    bp.save(isUpload = True,isTextMod = False)
    return bp
