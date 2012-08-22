'''
Created on Aug 16, 2012

@author: zouf
'''
from api.models import TypeOfBusiness, Business, BusinessType, BusinessCache
import logging

logger = logging.getLogger(__name__)

def associate_business_type(b,t): 
    if BusinessType.objects.filter(business=b,bustype=t).count() > 0:
        return
    BusinessType.objects.create(business=b,bustype=t)
    return

def associate_business_with_types(bus,types):
    for tdescr in types:
        try:
            t = TypeOfBusiness.objects.get(descr=tdescr) 
            associate_business_type(bus, t)  
        except TypeOfBusiness.MultipleObjectsReturned:
            logger.error("Multiple types returned")
            t = TypeOfBusiness.objects.filter(descr=tdescr)[0] 
            pass
        except TypeOfBusiness.DoesNotExist:
            print("Does not exist")
            logger.error('Type does not exist")')
            pass

def edit_business_server(bus,name,addr,city,state,phone,url,types):
    print("Editing business!\n")
    print(name)
    print(addr)
    print(city)
    print(state)
    print(phone)
    print(url)
    print(types)
    if name != '':
        bus.name = name
    if addr != '':
        bus.addr = addr
    if bus.city != '':
        bus.city = city
    if bus.state != '':
        bus.state = state
    if bus.phone != '':
        bus.phone = phone
    if bus.url != '':
        bus.url = url
        
    if types != '': 
        associate_business_with_types(bus,types)   
        
    BusinessCache.objects.filter(business=bus).delete()
    bus.save()
    return bus

def add_business_server(name,addr,city,state,phone,url,types):
    print("Creating business!\n")
    print(name)
    print(addr)
    print(city)
    print(state)
    print(phone)
    print(url)
    print(types)
    try:
        bset = Business.objects.filter(name=name,address=addr,city=city,state=state)    
        if bset.count() ==  0:
            bus = Business(name=name,address=addr,city=city,state=state,phone=phone,url=url)
            bus.save()
        elif bset.count() > 1: #too many
            bset.delete()
            bus = Business(name=name,address=addr,city=city,state=state,phone=phone,url=url)
            bus.save()
        else:
            bus = Business.objects.get(name=name,address=addr,city=city,state=state)
  
        associate_business_with_types(bus,types)
        print('creating of business done')
        return bus
    except Exception as e:
        logger.error(e.value)
        return None