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


#CODE NEEDS TO BE REFACTORED
def get_photo_url(b):
    qset  = Photo.objects.filter(business=b)
    if qset.count() < 1:
        return False
    ph = qset[0].image_thumb
    return ph.url


def add_photo_by_url(phurl, business,user,default,caption,title):
    outpath =settings.STATIC_ROOT+str(business.id)+"_"+str(business.city)+"_"+str(business.state)
    #print('retrieve'+str(urlparse.urlunparse(phurl)))
    try:
        urlretrieve(phurl, outpath)
    except:
        return None

    p = Photo(user=user, business=business, image=outpath, title=title, caption=caption,is_default=default)
    p.save(False)

    return p

def add_photo_by_upload(img,b,user,default,caption,title):
    bp =Photo(user=user, business=b, image=img, title=title, caption=caption,is_default=default)
    bp.save(True)
    return bp
