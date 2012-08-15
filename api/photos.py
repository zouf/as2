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
def get_photo_url(b):
    qset  = Photo.objects.filter(business=b)
    if qset.count() < 1:
        return DEFAULT_IMAGE
    ph = qset[0].image
    return ph.url

def get_photo_id(b):
    qset  = Photo.objects.filter(business=b)
    if qset.count() < 1:
        return False
    return qset[0].id




def add_photo_by_url(phurl, business,user,default,caption,title):
    outpath =settings.STATIC_ROOT+str(business.id)+"_"+str(business.city)+"_"+str(business.state)
    #print('retrieve'+str(urlparse.urlunparse(phurl)))
    
    try:
        urlretrieve(phurl, outpath)
    except:
        print('exception')
        return None

    p = Photo(user=user, business=business, image=outpath, title=title, caption=caption,is_default=default)
    p.save(isUpload = False,isTextMod = False)
    print(p)
    return p

def add_photo_by_upload(img,b,user,default,caption,title):
    bp =Photo(user=user, business=b, image=img, title=title, caption=caption,is_default=default)
    bp.save(isUpload = True,isTextMod = False)
    return bp
