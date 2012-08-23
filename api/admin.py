'''
Created on Aug 2, 2012

@author: zouf
'''
from api.models import Business, Photo, AllsortzUser, Offer, BusinessAction, \
    BusinessTopicDiscussion, BusinessDiscussion, PhotoDiscussion, Device, \
    ASUserOffer, ActionOption, ASUserCompletedAction, BusinessTopic, UserTopic, \
    UserFavorite, Topic, BusinessRating, BusinessTopicRating, PhotoRating
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


admin.site.register(BusinessTopicDiscussion)
admin.site.register(BusinessDiscussion)
admin.site.register(PhotoDiscussion)

admin.site.register(BusinessTopic)
admin.site.register(Topic)
admin.site.register(UserTopic)
admin.site.register(UserFavorite)

admin.site.register(BusinessRating)
admin.site.register(BusinessTopicRating)
admin.site.register(PhotoRating)