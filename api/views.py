from django.shortcuts import render, render_to_response, redirect
import json
from django.http import HttpResponse
from api.models import Categories, CategoryDetails, Languages, Products, Products_details, Currencies, Order_statuses,Region, MyUser,Orders,  OrdersItems, Gallery_Photo, ItemStatus, Itemsinset
from random import choice
from string import ascii_uppercase
from django.views.decorators.csrf import csrf_exempt
import random
from django.contrib.auth import authenticate, login, logout as django_logau
import requests,json
import ast
import base64
from base64 import decodestring
import uuid
from django.core.files.base import ContentFile
# Create your views here.


@csrf_exempt
def get_home_page(request):

    ist = ItemStatus.objects.get(status="Active")
    lang = request.POST.get('language')
    cat = Categories.objects.all()
    lng = Languages.objects.get(iso_3166_a2=lang)
    response_dict = {}
    catarr = []
    setarr = []
    popitemarr = []
    for i in cat:

        catdet = CategoryDetails.objects.get(category=i, language=lng)
        catdetdict = {
            "id"    : i.id,
            "title" : "%s" %catdet.title

        }
        catarr.append(catdetdict)

    sets = Products.objects.filter(is_set=True, is_popular=True, in_active=True, status = ist)
    for i in sets:
        setdict = {
            "id": i.id,
            "imgUrl": "/media/%s" % i.main_img
        }
        setarr.append(setdict)

    popitems = Products.objects.filter(is_set=False, is_popular=True, in_active=True, status = ist)
    for i in popitems:
        popitemdict = {
            "id": i.id,
            "imgUrl": "/media/%s" % i.main_img
        }
        popitemarr.append(popitemdict)


    response_dict['categories'] = catarr
    response_dict['sets'] = setarr
    response_dict['popitems'] = popitemarr


    return HttpResponse(json.dumps(response_dict).encode('utf8'), content_type='application/json')

@csrf_exempt
def get_items_by_category(request):
    print("##########################################")
    print(request.POST.keys())
    print("##########################################")
    ist = ItemStatus.objects.get(status="Active")
    lang = request.POST.get('language')
    print('language = ', lang)
    lng = Languages.objects.get(iso_3166_a2=lang)
    #cat_id = request.POST.get('catId')
    from_p = request.POST.get('from')
    print('from = ', from_p)
    to_p = request.POST.get('to')
    print('to = ', to_p)
    city = request.POST.get('city')
    print('city = ', city)
    #cat = Categories.objects.get(id = cat_id)
    if int(city) == 0:
        prod = Products.objects.filter( is_set=False, in_active=True, status=ist)
    else:
        prod = Products.objects.filter( is_set=False, in_active=True, status=ist, city=city)
    response_dict = {}

    prodarr = []
    for i in prod[int(from_p):int(to_p)]:
        proddet = Products_details.objects.get(product=i,  language=lng)
        proddetdict = {

            "imgUrl": "/media/%s" %i.main_img,
            "title": "%s" %proddet.title,
            "price" : "%s" %i.price,
            # "currency" : "%s" %i.currency.iso_4217,
            "id" : i.id,
            "img_width": i.main_img.width,
            "img_height": i.main_img.height,
	    "stars": 3,
            "com":24,
            "location": i.location,
        }
        prodarr.append(proddetdict)

    response_dict['data'] = prodarr

    return HttpResponse(json.dumps(response_dict).encode('utf8'), content_type='application/json')


@csrf_exempt
def get_items_details(request):

    
    lang = request.POST.get('language')
    lng = Languages.objects.get(iso_3166_a2=lang)
    item_id = request.POST.get('itemId')
    prod = Products.objects.get(id = item_id)
    try:
        logo = prod.logo.logo_img.url
    except:
        logo = "No logo"
    if prod.is_set:
        
        lang = request.POST.get('language')
        lng = Languages.objects.get(iso_3166_a2=lang)
        item_id = request.POST.get('itemId')
        prod = Products.objects.get(id=item_id)
        proddesc = Products_details.objects.get(product=prod, language=lng)
        gal_photo = Gallery_Photo.objects.filter(item=prod)
        # catname = prod.category.cat_name
        # cat = prod.category
        # gg = CategoryDetails.objects.get(category = cat, language = lng)

        dd = Itemsinset.objects.filter(set=prod)
        itemsarr = []
        

        for i in dd:
            rr = Products_details.objects.get(product=i.item, language=lng)
            ee = CategoryDetails.objects.get(category=i.item.category, language=lng)

            itemsarr.append({
                'imgUrl': i.item.main_img.url,
                'id' : i.item.id,
                'title' : rr.title,
                'price' : "%s" %i.item.price,
                'kids_price' : "%s" %i.item.kids_price,
		'ff' : i.item.price,
                'catItemName' : ee.title,
                'logo' : logo,
                'location': i.item.location,


            })

        galarr = []
        for i in gal_photo:
            galarr.append(i.photo.url)

        proddict = {
            "id": prod.id,
            "main_img": "%s" % prod.main_img.url,
            "gallphoto": galarr,
            "title": "%s" % proddesc.title,
            'items': itemsarr,
            "country": "huyanti",
            "city": "huiti",
            "location" : "24.774 46.738",
            
            


        }

        return HttpResponse(json.dumps(proddict).encode('utf8'), content_type='application/json')
    else:
        #loc = '123 123 prof.NOT_IN_set '
        proddesc = Products_details.objects.get(product=prod, language=lng)
        gal_photo = Gallery_Photo.objects.filter(item=prod)
        #catname = prod.category.cat_name
        cat = prod.category

        gg = CategoryDetails.objects.get(category = cat, language = lng)

        galarr = []
        for i in gal_photo:
            galarr.append(i.photo.url)

        proddict = {
            "id" : prod.id,
            "main_img": "%s" %prod.main_img.url,
            "gallphoto": galarr,
            "cat_name": gg.title,
            "title": "%s" % proddesc.title,
            "price" : "%0.2f" %prod.price,
            "kids_price" : "%0.2f" %prod.kids_price,
            "currency" : "SAR",
            "descriptions": "%s" %proddesc.descriptions,
            "location" : prod.location,
            "logo": logo,
            "shared_content" : "{}\n{}".format(proddesc.descriptions,prod.share),
            "reserv": prod.reservdate,
        }

        return HttpResponse(json.dumps(proddict).encode('utf8'), content_type='application/json')

@csrf_exempt
def test(request):
    f = open('/home/ubuntu/logs/text.txt', 'a')
    # try:
    #     f.write(str(request.GET.get('id','')))
    #     f.write(str(request.GET.get('resourcePath','')))
    #     f.write(str(request.BODY))
    #
    # except:
    #     pass
    f.write(" GG W \n ")
    f.write( str(request.GET.get('resourcePath', '')))

    f.write(" GG W \n ")

    try:
        url2 = "https://test.oppwa.com/v1/checkouts/%s/payment" %str(request.GET.get('id',''))
        url2 += '?authentication.userId=8a82941861225c8b0161288d14221539'
        url2 += '&authentication.password=ERdpJNJ2Dh'
        url2 += '&authentication.entityId=8a829417612255630161288dbbe11330'
        r = requests.get(url2, "")
        json_acceptable_string = r.text  # .replace("'", "\"")
        jj = json.loads(json_acceptable_string)
        #f.write(r.text)

        if jj["result"]['code'] == '000.000.000' or '000.100.110' or '000.100.110' or '000.100.111' or '000.100.112' or '000.300.000':
            f.write(jj["result"]['code'])
            f.write(" \n ")
            f.write(" EZ PZ \n ")

    except:
        pass

    f.close()

    return (HttpResponse(str('hallo')))

@csrf_exempt
def prepear_checkout(request):


    data = json.loads(request.body.decode('utf-8'))
    #f = open('/home/ubuntu/logs/text.txt', 'a')
    #f.write(" GG W \n ")
    #f.write(data['fullname'])
    #f.close()
    #tt = data['fullname']
    #fh = open("/home/ubuntu/logs/imageToSave.png", "wb")
    #fh.write(tt.decode('base64'))
    #fh.close()

    #print(data['fullname'])






    fullname = data['fullname']
    phone = data['phonenumber']
    items = data['items']
    try:
        birthday = data['birthday']
    except:
        pass
    try:
        city = data['city']
    except:
        pass
    try:
        sex = data['sex']
    except:
        pass

    ###TODO

    ###TODO


    in_proc = False
    itemsarr = []
    total_price = 0
    ordersarr = []
    for i in items:

        gg = Products.objects.get(id=int(i['id']))
        itemsarr.append(gg)

        amount = i['number']
        #kids_amount = i['number_kids'] * gg.kids_price
        cur = Currencies.objects.get(iso_4217='SAR')
        gg1 = Orders(user=gg.vendor, total_amount=amount,currencies=cur, status=in_proc, delivery_adress='deliveryAdres',
                     delivery_datetime="%s %s" % (i['date'], i['Time']), count=i['number'], buyer_fullname=fullname,
                     buyer_phone=phone, kids_count=i['number_kids'])
        try:
            gg1.birthday = birthday
        except:
            pass
        try:
            gg1.city = city
        except:
            pass
        try:
            gg1.sex = sex
        except:
            pass
        try:
            description_img = i['comphoto']
            rr = description_img
            # image_data = base64.b64decode(rr.encode())
            # imgstr = image_data.split(';base64,')

            data = ContentFile(decodestring(b"%s" % rr.encode()))
            gg1.description_img.save("dd.jpg", data, save=True)
        except:
            pass
        try:
            description = i['comtext']
            gg1.description = description
        except:
            pass
        gg1.save()
        ordersarr.append(gg1)

        total_price += (i['number'] * gg.price + i['number_kids'] * gg.kids_price)

        gg3 = OrdersItems(order=gg1, item=gg)
        gg3.save()

    url = "https://test.oppwa.com/v1/checkouts"


    data = {
        'authentication.userId': '8a82941861225c8b0161288d14221539',
        'authentication.password': 'ERdpJNJ2Dh',
        'authentication.entityId': '8a829417612255630161288dbbe11330',

        'amount': "%.2f" %total_price,
        'currency': 'SAR',
        'testMode': 'EXTERNAL',
        'paymentType': 'DB',
        'shopperResultUrl': 'my.app://custom/url',
        'notificationUrl': 'http://test'
     #   'notificationUrl': 'http://52.56.235.17/api/test'
    }
    try:
        r = requests.post(url,data)
        json_acceptable_string = r.text #.replace("'", "\"")
        d = json.loads(json_acceptable_string)
        print(d['id'])
        for i in ordersarr:
            i.checkid = d['id']
            i.save()

        return HttpResponse(r.text, content_type='application/json')
    except :
        return "error"

def main2(request):

    if request.user.is_authenticated:
        return redirect('/profile')
    else:
        return render(request, 'app/login.html', {})

@csrf_exempt
def paycheck(request):

    gg = request.POST.get('id','')
    str = ""
    try:
        url2 = "https://test.oppwa.com/v1/checkouts/%s/payment" %gg
        url2 += '?authentication.userId=8a82941861225c8b0161288d14221539'
        url2 += '&authentication.password=ERdpJNJ2Dh'
        url2 += '&authentication.entityId=8a829417612255630161288dbbe11330'
        r = requests.get(url2, "")
        json_acceptable_string = r.text  # .replace("'", "\"")
        jj = json.loads(json_acceptable_string)
        str =  jj["result"]["description"]
        if jj["result"]["code"] == '000.000.000' or jj["result"]["code"] == '000.100.110' or jj["result"]["code"] == '000.100.111' or jj["result"]["code"] == '000.100.112' or jj["result"]["code"] == '000.300.000':

            gg1 = Orders.objects.filter(checkid=gg)
            for i in gg1:
                i.is_paid = True
                i.save()

    except:
        pass


    return  HttpResponse( str )

@csrf_exempt
def get_items_by_keyword(request):
    ist = ItemStatus.objects.get(status="Active")

    keyword = request.POST.get('keyword').lower()
    lang = request.POST.get('language')
    lng = Languages.objects.get(iso_3166_a2=lang)
    #cat_id = request.POST.get('catId')
    from_p = request.POST.get('from')
    to_p = request.POST.get('to')
    #cat = Categories.objects.get(id = cat_id)
    prod = Products.objects.filter( is_set=False, in_active=True, status = ist)
    response_dict = {}
    prodarr = []
    prod2 = []
    for i in prod:
        wp = Products_details.objects.get(product = i, language = lng)
        gg = wp.title.lower().find(keyword)
        if gg >= 0:
            prod2.append(i)
    for i in prod2[int(from_p):int(to_p)]:
        proddet = Products_details.objects.get(product=i,  language=lng)
        proddetdict = {

            "imgUrl": "/media/%s" %i.main_img,
 		"title": "%s" %proddet.title,
          "id" : i.id,
            "img_width": i.main_img.width,
            "img_height": i.main_img.height,
	    "stars": 3,
		"price" : "%s" %i.price,




        }
        prodarr.append(proddetdict)

    response_dict['data'] = prodarr

    return HttpResponse(json.dumps(response_dict).encode('utf8'), content_type='application/json')

@csrf_exempt
def get_wishlist(request):
    data = json.loads(request.body.decode('utf-8'))
    items = data['items']
    response_dict = {}
    prodarr = []
    for i in items:
        try:
            gg = Products.objects.get(id = i)
            proddetdict = {

                "imgUrl": "/media/%s" % gg.main_img,
                # "title": "%s" %proddet.title,
                # "price" : "%s" %i.price,
                # "currency" : "%s" %i.currency.iso_4217,
                "id": gg.id,
                "img_width": gg.main_img.width,
                "img_height": gg.main_img.height

            }
            prodarr.append(proddetdict)
        except:
            pass


    response_dict['data'] = prodarr

    return HttpResponse(json.dumps(response_dict).encode('utf8'), content_type='application/json')

@csrf_exempt
def get_sets(request):
    ist = ItemStatus.objects.get(status="Active")

    lang = request.POST.get('language')
    lng = Languages.objects.get(iso_3166_a2=lang)
    from_p = request.POST.get('from')
    to_p = request.POST.get('to')
    prod = Products.objects.filter(is_set=True, in_active=True, status = ist)
    response_dict = {}
    prodarr = []
    for i in prod[int(from_p):int(to_p)]:
        proddet = Products_details.objects.get(product=i,  language=lng)
        proddetdict = {

            "imgUrl": "/media/%s" %i.main_img,
           # "title": "%s" %proddet.title,
           # "price" : "%s" %i.price,
           # "currency" : "%s" %i.currency.iso_4217,
            "id" : i.id,
            "img_width": i.main_img.width,
            "img_height": i.main_img.height


        }
        prodarr.append(proddetdict)

    response_dict['data'] = prodarr

    return HttpResponse(json.dumps(response_dict).encode('utf8'), content_type='application/json')

@csrf_exempt
def search_items_by_keyword(request):
    ist = ItemStatus.objects.get(status="Active")
    keyword = request.POST.get('keyword').lower()
    lang = request.POST.get('language')
    lng = Languages.objects.get(iso_3166_a2=lang)
    from_p = request.POST.get('from')
    to_p = request.POST.get('to')
    prod = Products.objects.filter(in_active=True, status = ist)
    response_dict = {}
    prodarr = []
    prod2 = []
    for i in prod:
        wp = Products_details.objects.get(product = i, language = lng)
        gg = wp.title.lower().find(keyword)
        if gg >= 0:
            prod2.append(i)
    for i in prod2[int(from_p):int(to_p)]:
        proddet = Products_details.objects.get(product=i,  language=lng)

        proddetdict = {

            "imgUrl": "/media/%s" %i.main_img,
            "id" : i.id,
            "img_width": i.main_img.width,
            "img_height": i.main_img.height,
            "set": i.is_set

        }
        prodarr.append(proddetdict)

    response_dict['data'] = prodarr

    return HttpResponse(json.dumps(response_dict).encode('utf8'), content_type='application/json')

@csrf_exempt
def get_set_details(request):
    lang = request.POST.get('language')
    lng = Languages.objects.get(iso_3166_a2=lang)
    item_id = request.POST.get('itemId')
    prod = Products.objects.get(id=item_id)
    try:
        logo = prod.logo.logo_img.url
    except:
        logo = "No logo"
    proddesc = Products_details.objects.get(product=prod, language=lng)
    gal_photo = Gallery_Photo.objects.filter(item=prod)
    # catname = prod.category.cat_name
    # cat = prod.category
    # gg = CategoryDetails.objects.get(category = cat, language = lng)

    dd = Itemsinset.objects.filter(set=prod)
    itemsarr = []

    for i in dd:
        rr = Products_details.objects.get(product=i.item, language=lng)
        ee = CategoryDetails.objects.get(category=i.item.category, language=lng)

        itemsarr.append({
            'imgUrl': i.item.main_img.url,
            'id': i.item.id,
            'title': rr.title,
            'price': i.item.price,
            'catItemName': ee.title,

        })

    galarr = []
    for i in gal_photo:
        galarr.append(i.photo.url)

    proddict = {
        "id": prod.id,
        "main_img": "%s" % prod.main_img.url,
        "gallphoto": galarr,
        "title": "%s" % proddesc.title,
        'items': itemsarr,
        "country": "Dimon",
        "city": "Kudimon",

    }

    return HttpResponse(json.dumps(proddict).encode('utf8'), content_type='application/json')


@csrf_exempt
def poycheck(request):

    gg = request.POST.get('id','')
    str = ""
    try:
        url2 = "https://test.oppwa.com/v1/checkouts/%s/payment" %gg
        url2 += '?authentication.userId=8a82941861225c8b0161288d14221539'
        url2 += '&authentication.password=ERdpJNJ2Dh'
        url2 += '&authentication.entityId=8a829417612255630161288dbbe11330'
        r = requests.get(url2, "")
        json_acceptable_string = r.text  # .replace("'", "\"")
        jj = json.loads(json_acceptable_string)
        str =  jj["result"]["description"]
        if jj["result"]["code"] == '000.000.000' or jj["result"]["code"] == '000.100.110' or jj["result"]["code"] == '000.100.111' or jj["result"]["code"] == '000.100.112' or jj["result"]["code"] == '000.300.000':

            gg1 = Orders.objects.filter(checkid=gg)
            for i in gg1:
                i.is_paid = True
                i.save()
            proddict = {
                "stroka": str,
                "uspeh": True
            }
        else:
            proddict = {
                "stroka": str,
                "uspeh": False
            }
    except:
        pass



    return HttpResponse(json.dumps(proddict).encode('utf8'), content_type='application/json')


@csrf_exempt
def search_for_set(request):
    ist = ItemStatus.objects.get(status="Active")
    keyword = request.POST.get('keyword').lower()
    lang = request.POST.get('language')
    lng = Languages.objects.get(iso_3166_a2=lang)
    from_p = request.POST.get('from')
    to_p = request.POST.get('to')
    prod = Products.objects.filter(in_active=True, status = ist, is_set = True)
    response_dict = {}
    prodarr = []
    prod2 = []
    for i in prod:
        wp = Products_details.objects.get(product = i, language = lng)
        gg = wp.title.lower().find(keyword)
        if gg >= 0:
            prod2.append(i)
    for i in prod2[int(from_p):int(to_p)]:
        proddet = Products_details.objects.get(product=i,  language=lng)

        proddetdict = {

            "imgUrl": "/media/%s" %i.main_img,
            "id" : i.id,
            "img_width": i.main_img.width,
            "img_height": i.main_img.height,
            "set": i.is_set

        }
        prodarr.append(proddetdict)

    response_dict['data'] = prodarr

    return HttpResponse(json.dumps(response_dict).encode('utf8'), content_type='application/json')
