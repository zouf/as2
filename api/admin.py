'''
Created on Aug 2, 2012

@author: zouf
'''
from api.models import Business, Photo, AllsortzUser, Offer, BusinessAction, \
    CategoryDiscussion, BusinessDiscussion, PhotoDiscussion, Device, ASUserOffer, \
    ActionOption, ASUserCompletedAction, BusinessCategory, UserSubscription, \
    UserFavorite, Tag, BusinessRating, CategoryRating, PhotoRating
from django.contrib import admin


admin.site.register(Business)
admin.site.register(Photo)


admin.site.register(AllsortzUser)
admin.site.register(Device)
#admin.site.register(Offer)
#admin.site.register(ActionOption)
#admin.site.register(ASUserCompletedAction)
#admin.site.register(BusinessAction)
#admin.site.register(ASUserOffer)


admin.site.register(CategoryDiscussion)
admin.site.register(BusinessDiscussion)
admin.site.register(PhotoDiscussion)

admin.site.register(BusinessCategory)
admin.site.register(Tag)
admin.site.register(UserSubscription)
admin.site.register(UserFavorite)

admin.site.register(BusinessRating)
admin.site.register(CategoryRating)
admin.site.register(PhotoRating)