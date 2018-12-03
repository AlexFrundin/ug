from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth import authenticate,logout,login
import random, datetime, calendar, json
from datetime import timedelta
from api.models import MyUser, Products, Products_details,Order_statuses, Orders, Languages, Currencies, Countries, Region, Categories, CategoryDetails, ItemStatus, OrdersItems, Gallery_Photo, ItemSet, Itemsinset, Set_details, Logo
from django.views.decorators.csrf import csrf_exempt


def index(request):
    context = {}
    template = loader.get_template('app/index.html')
    return HttpResponse(template.render(context, request))

def mainpage(request):

    if request.user.is_authenticated:
        context = {}
        return redirect('/profile')
    else:
        return redirect("/login.html")

def gentella_html(request):
    context = {}
    # The template to be loaded as per gentelella.
    # All resource paths for gentelella end in .html.

    # Pick out the html file name from the url. And load that template.
    load_template = request.path.split('/')[-1]
    template = loader.get_template('app/' + load_template)
    return HttpResponse(template.render(context, request))

def confirmcode(request):

    context = {}
    formtype = request.POST.get("formtype")
    phone = request.POST.get('phone')

    if formtype == 'register':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        passwd = request.POST.get('password')
        try:
            uzver = MyUser.objects.create_user(phone=phone)
            uzver.set_password(passwd)
            uzver.first_name = firstname
            uzver.last_name = lastname
            uzver.save()
            context['message'] = "User created. Now log in"
            return render(request, "app/login.html", context)
        except:
            context['message'] = "User alredy register. Now log in"
            return render(request, "app/login.html", context)

    if formtype == 'login':
        try:
            uzver = MyUser.objects.get(phone=phone)
            pswd = request.POST.get('password')
            print(pswd)
            user = authenticate(phone=phone, password=pswd)
            if user is not None:
                login(request, user)
                print("GOOD")
                return redirect('/profile')
            else:
                print('bad')
                context['message'] = 'Invalid user or password'
                context['phone'] = phone
                return render(request, 'app/login.html', context)
        except:
            print('ERROR')
            context['message'] = 'User not found. Pls register'
            return render(request, 'app/login.html', context)

def profile(request):
    if request.user.is_authenticated:
        context = {}
        return render(request, 'app/profile.html', context )
    else:
        return redirect("/login.html")

def itemlist(request):
    if request.user.is_authenticated:
        context = {}
        ln = Languages.objects.get(iso_3166_a2='EN')
        items = Products.objects.filter(vendor = request.user, in_active=True).order_by("-id")
        itemsarr = []
        for i in items:
            try:
                print (i.id)
                pd = Products_details.objects.get(product=i, language=ln)
                itemsarr.append({
                    'main_img': i.main_img,
                    'id' : i.id,
                    'title': pd.title,
                    'status': i.status.status,
                    'scolor': i.status.color,
                    'price': i.price,
                    'currency': "SAR",
                })
            except:
                print ("err")
        context['items'] = itemsarr
        print(itemsarr)

        return render(request, 'app/itemlist.html', context)
    else:
        return redirect("/login.html")

def createitem(request):
    if request.user.is_authenticated:
        context = {}
        ln = Languages.objects.get(iso_3166_a2='EN')
        #cr = Currencies.objects.all()
        logo = Logo.objects.filter(uzver = request.user)
        #co = Countries.objects.all()
        #rg = Region.objects.all()
        ct = Categories.objects.all()
        cta = []
        for i in ct:
            # print(i.cat_name)
            # ctd = CategoryDetails.objects.get(language=ln, category=i)
            # cta.append(ctd.title)
            cta.append(i.cat_name)



        context['logo'] = logo
        context['languages'] = ln
        #context['currencies'] = cr
        #context['countries'] = co
       # context['regions'] = rg
        context['categories'] = cta

        return render(request, 'app/createitem.html', context)
    else:
        return redirect("/login.html")

def createitemhandle(request):
    if request.user.is_authenticated:
        #try:
        cat = request.POST.get('category')
        pr = request.POST.get('price')
        try:
            gavno = request.POST.get('gavno')
        except:
            gavno = "---"
        cit = int(request.POST.get('city')[:1])
        try:
            kids_pr = request.POST.get('kids_price')
        except:
            kids_pr = 0
        main_photo = request.FILES['upload']
        gall_photo = request.FILES.getlist('images')
        try:
            logo = request.POST.get('logo')
            ll =  Logo.objects.get(uzver = request.user, logo_name = logo)
        except:
            pass
        #isset = request.POST.get('set')
        ent = request.POST.get('ent')
        art = request.POST.get('art')
        ardes = request.POST.get('ardes')
        endes = request.POST.get('endes')
        loc = request.POST.get('location')
        ist = ItemStatus.objects.get(status="Moderate")
        cat2 = Categories.objects.get(cat_name=cat)
        gg = Products(vendor=request.user, price=float(pr), kids_price=float(kids_pr),
                      main_img=main_photo, status=ist, category=cat2, city=cit, share=gavno, location=loc)
        #if isset != None:
        #    gg.is_set = True
        try:
            gg.logo = ll
        except:
            pass
        gg.save()
        arleng = Languages.objects.get(iso_3166_a2='AR')
        enleng = Languages.objects.get(iso_3166_a2='EN')
        if gall_photo != []:
            for i in gall_photo:
                try:
                    gg5 = Gallery_Photo(item=gg,photo=i)
                    gg5.save()
                except:
                    print('err')
        else:
            print("LOLOLOLOLO")


        gg2 = Products_details(product=gg, title=art, descriptions=ardes, language=arleng)
        gg3 = Products_details(product=gg, title=ent, descriptions=endes, language=enleng)

        gg2.save()
        gg3.save()

        return redirect('/itemlist')
        # except:
        #     return redirect('/createitem')
    else:
        return redirect("/login.html")
    ####333333333333333333333333333333333333

def orderlist_all(request):
    if request.user.is_authenticated:
        context = {}
        dataarr = []
        oo = Orders.objects.filter(user = request.user, is_paid = True).order_by("-id")
        for i in oo:
            oi = OrdersItems.objects.get(order=i)
            dataarr.append(
            {   'id': i.id,
                'date': i.create_date,
                'img': oi.item.main_img,
                'buyer_fullname': i.buyer_fullname,
                'buyer_phone': i.buyer_phone,
                'status': i.status,
                'price': i.total_amount,
                'delivery_adress': i.delivery_adress,
                'delivery_datetime': i.delivery_datetime,
                'currency': i.currencies.iso_4217,
                'count': i.count,
                'birthday' : i.birthday,
                'sex' : i.sex,
                'city' : i.city,
                'description' : i.description,
                'description_img' : i.description_img

            })
        context['data'] = dataarr
        return render(request, 'app/orders.html', context)
    else:
        return redirect("/login.html")

def orderlist_new(request):

    if request.user.is_authenticated:
        context = {}
        dataarr = []
        oo = Orders.objects.filter(user=request.user, is_paid = True).order_by("-id")
        for i in oo:
            if i.status == False:

                oi = OrdersItems.objects.get(order=i)
                dataarr.append(
                    {'id': i.id,
                     'date': i.create_date,
                     'img': oi.item.main_img,
                     'buyer_fullname': i.buyer_fullname,
                     'buyer_phone': i.buyer_phone,
                     'status': i.status,
                     'price': i.total_amount,
                     'delivery_adress': i.delivery_adress,
                     'delivery_datetime': i.delivery_datetime,
                     'currency': i.currencies.iso_4217,
                     'count': i.count,
                     'birthday': i.birthday,
                     'sex': i.sex,
                     'city': i.city,
                     'description': i.description,
                     'description_img': i.description_img

                     })
        context['data'] = dataarr
        return render(request, 'app/orders.html', context)
    else:
        return redirect("/login.html")

def orderlist_finished(request):
    if request.user.is_authenticated:
        context = {}
        dataarr = []
        oo = Orders.objects.filter(user=request.user, is_paid = True).order_by("-id")
        for i in oo:
            if i.status == True:
                oi = OrdersItems.objects.get(order=i)
                dataarr.append(
                    {'id': i.id,
                     'date': i.create_date,
                     'img': oi.item.main_img,
                     'buyer_fullname': i.buyer_fullname,
                     'buyer_phone': i.buyer_phone,
                     'status': i.status,
                     'price': i.total_amount,
                     'delivery_adress': i.delivery_adress,
                     'delivery_datetime': i.delivery_datetime,
                     'currency': i.currencies.iso_4217,
                     'count': i.count,
                     'birthday': i.birthday,
                     'sex': i.sex,
                     'city': i.city,
                     'description': i.description,
                     'description_img': i.description_img
                     })
        context['data'] = dataarr
        return render(request, 'app/orders.html', context)
    else:
        return redirect("/login.html")

def editprofile(request):
    if request.user.is_authenticated:
        context = {}
        return render(request, 'app/editprofile.html', context)
    else:
        return redirect("/login.html")

def editprofilehandle(request):
    if request.user.is_authenticated:
        uzver = MyUser.objects.get(id = request.user.id)
        fname = request.POST.get('fname')
        sname = request.POST.get('sname')
        uzver.first_name = fname
        uzver.last_name = sname
        uzver.photo = request.FILES['upload']
        #TODO Check if photo empty
        uzver.save()
        return redirect('/profile')
    else:
        return redirect("/login.html")


def endsession(request):
    logout(request)
    return redirect('/')

def edititem(request, id):
    if request.user.is_authenticated:

        prod = Products.objects.get(id=id)
        if request.user == prod.vendor or request.user.is_admin:
            enln = Languages.objects.get(iso_3166_a2='EN')
            arln = Languages.objects.get(iso_3166_a2='AR')
            enprod = Products_details.objects.get(product=prod, language= enln)
            arprod = Products_details.objects.get(product=prod, language= arln)
            context = {}
            ln = Languages.objects.get(iso_3166_a2='EN')
            ct = Categories.objects.all()
            try:
                ei = Logo.objects.filter(uzver = request.user)
            except:
                pass
            cta = []
            for i in ct:
                # print(i.cat_name)
                # ctd = CategoryDetails.objects.get(language=ln, category=i)
                # cta.append(ctd.title)
                cta.append(i.cat_name)
            context['languages'] = ln
            context['categories'] = cta
            context['t_category'] = prod.category.cat_name
            context['t_price'] = prod.price
            context['gavno'] = prod.share
            context['t_kids_price'] = prod.kids_price
            context['t_img'] = prod.main_img
            context['t_ent'] = enprod.title
            context['t_art'] = arprod.title
            context['t_endes'] = enprod.descriptions
            context['t_ardes'] = arprod.descriptions
            context['t_id'] = prod.id
            context['t_location'] = prod.location
            try:
                context['t_logo'] = prod.logo.logo_name
            except:
                context['t_logo'] = "Choice your logo"

            context['logo'] = ei

            context['t_gimg'] = Gallery_Photo.objects.filter(item=prod)

            return render(request, 'app/edititem.html', context)
        else:
            return redirect('/itemlist')
    else:
        return redirect("/login.html")



def deactivate(request, id):
    if request.user.is_authenticated:
        gg = Products.objects.get(id=id)
        if request.user.is_admin or gg.vendor == request.user:
            gg = Products.objects.get(id=id)
            gg.in_active = False
            gg.save()
            if request.user.is_admin:

                return redirect(request.META.get('HTTP_REFERER'))
            else:
                return redirect(request.META.get('HTTP_REFERER'))
        else:
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect("/login.html")



def moderate(request, id):
    if request.user.is_authenticated:
        if request.user.is_admin:
            gg = Products.objects.get(id=id)

            ist = ItemStatus.objects.get(status="Active")
            gg.status = ist
            gg.save()

            return redirect(request.META.get('HTTP_REFERER'))
        else:
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect("/login.html")


def reservedate(request, id):
    if request.user.is_authenticated:
        prod = Products.objects.get(id=id)
        if request.user == prod.vendor or request.user.is_admin:
            if request.method == 'POST':
                prod.reservdate = request.POST.get('reserv')
                prod.save()
            context = {}
            context['data'] = prod.reservdate
            context['id'] = prod.id
            return render(request, 'app/reservedate.html', context)
        else:
            return redirect('/itemlist')
    else:
        return redirect("/login.html")

def edititemhandle(request, id):
    if request.user.is_authenticated:
        gg = Products.objects.get(id=id)
        if gg.vendor == request.user or request.user.is_admin:

            cat = request.POST.get('category')
            lg = request.POST.get('logo')
            cit = int(request.POST.get('city')[:1])
            pr = request.POST.get('price')
            gavno = request.POST.get('gavno')
            kids_pr = request.POST.get('kids_price')
            dp = 1000
            cr = "SAR"
            try:
                main_photo = request.FILES['upload']
            except:
                print('err')
            try:
                gall_photo = request.FILES.getlist('images')
                print(gall_photo)
            except:
                print('err')
            ent = request.POST.get('ent')
            art = request.POST.get('art')
            ardes = request.POST.get('ardes')
            endes = request.POST.get('endes')
            loc = request.POST.get('location')


            ist = ItemStatus.objects.get(status="Moderate")

            cat2 = Categories.objects.get(cat_name=cat)



            #gg.vendor=request.user
            gg.sahre = gavno
            gg.kids_price = float(kids_pr)
            gg.city = cit
            gg.price=float(pr)
            gg.delivery_price=float(dp)
            try:
                gg.main_img=main_photo
            except:
                print("Err")
            #try:
            for i in gall_photo:
                gg5 = Gallery_Photo(item=gg, photo=i)
                gg5.save()
           # except:
           #     print('err')
            try:
                logos = Logo.objects.get(uzver = request.user, logo_name = lg)
                gg.logo = logos
            except:
                pass
            gg.status=ist
            gg.category=cat2
            gg.location=loc
            gg.save()


            arleng = Languages.objects.get(iso_3166_a2='AR')
            enleng = Languages.objects.get(iso_3166_a2='EN')

            gg2 = Products_details.objects.get(product=gg,language=arleng)
            gg2.title=art
            gg2.descriptions=ardes

            gg3 = Products_details.objects.get(product=gg, language=enleng)
            gg3.title = ent
            gg3.descriptions = endes
            gg2.save()
            gg3.save()
            if request.user.is_admin:
                return redirect('/admin-items')
            else:
                return redirect('/itemlist')
    else:
        return redirect("/login.html")

def userlist(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            context = {}
            context['users'] = MyUser.objects.all()

            return render(request, 'app/a-userlist.html', context)
    else:
        return redirect("/login.html")

def itemlistforadmall(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            context = {}
            ln = Languages.objects.get(iso_3166_a2='EN')
            items = Products.objects.filter(in_active=True, is_set=False).order_by("-id")
            itemsarr = []
            for i in items:
                pd = Products_details.objects.get(product=i, language=ln)
                itemsarr.append({
                    'main_img': i.main_img,
                    'id': i.id,
                    'title': pd.title,
                    'status': i.status.status,
                    'scolor': i.status.color,
                    'price': i.price,
                    'currency': "SAR",
                    'pop': i.is_popular
                })
            context['items'] = itemsarr

            return render(request, 'app/a-items.html', context)
    else:
        return redirect("/login.html")

def itemlistforadmnew(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            context = {}
            ln = Languages.objects.get(iso_3166_a2='EN')
            ist = ItemStatus.objects.get(status="Moderate")
            items = Products.objects.filter(in_active=True, is_set=False, status=ist).order_by("-id")

            itemsarr = []
            for i in items:
                pd = Products_details.objects.get(product=i, language=ln)
                itemsarr.append({
                    'main_img': i.main_img,
                    'id': i.id,
                    'title': pd.title,
                    'status': i.status.status,
                    'scolor': i.status.color,
                    'price': i.price,
                    'currency': "SAR",
                    'pop': i.is_popular
                })
            context['items'] = itemsarr

            return render(request, 'app/a-items.html', context)
    else:
        return redirect("/login.html")

def itemlistforadmpop(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            context = {}
            ln = Languages.objects.get(iso_3166_a2='EN')
            items = Products.objects.filter(in_active=True, is_set=False, is_popular=True).order_by("-id")

            itemsarr = []
            for i in items:
                pd = Products_details.objects.get(product=i, language=ln)
                itemsarr.append({
                    'main_img': i.main_img,
                    'id': i.id,
                    'title': pd.title,
                    'status': i.status.status,
                    'scolor': i.status.color,
                    'price': i.price,
                    'currency': "SAR",
                    'pop': i.is_popular
                })
            context['items'] = itemsarr

            return render(request, 'app/a-items.html', context)

    else:
        return redirect("/login.html")

def admin_orderlist_new(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            context = {}
            dataarr = []

            oo = Orders.objects.filter(status = False , is_paid = True).order_by("-id")
            for i in oo:
                try:
                    oi = OrdersItems.objects.get(order=i)
                    dataarr.append(
                        {'id': i.id,
                         'vendor': i.user.last_name,
                         'vendorphone': i.user.phone,
                         'date': i.create_date,
                         'itemid': oi.item.id,
                         'buyer_fullname': i.buyer_fullname,
                         'buyer_phone': i.buyer_phone,
                         'status': i.status,
                         'price': i.total_amount,
                         'delivery_adress': i.delivery_adress,
                         'delivery_datetime': i.delivery_datetime,
                         'currency': i.currencies.iso_4217,
                         'count': i.count,
                         'count_kids': i.kids_count,

                         })
                except:
                    pass
            context['data'] = dataarr
            return render(request, 'app/a-orders.html', context)
    else:
        return redirect("/login.html")

def admin_orderlist_finished(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            context = {}
            dataarr = []

            oo = Orders.objects.filter(status = True, is_paid = True ).order_by("-id")
            for i in oo:
                try:
                    oi = OrdersItems.objects.get(order=i)
                    dataarr.append(
                        {'id': i.id,
                         'vendor': i.user.last_name,
                         'vendorphone': i.user.phone,
                         'date': i.create_date,
                         'itemid': oi.item.id,
                         'buyer_fullname': i.buyer_fullname,
                         'buyer_phone': i.buyer_phone,
                         'status': i.status,
                         'price': i.total_amount,
                         'delivery_adress': i.delivery_adress,
                         'delivery_datetime': i.delivery_datetime,
                         'currency': i.currencies.iso_4217,
                         'count': i.count,
                         'count_kids': i.kids_count,

                         })
                except:
                    pass
            context['data'] = dataarr
            return render(request, 'app/a-orders.html', context)
    else:
        return redirect("/login.html")

def setlistforadmall(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            context = {}
            ln = Languages.objects.get(iso_3166_a2='EN')
            items = Products.objects.filter(in_active=True, is_set=True).order_by("-id")
            itemsarr = []
            for i in items:
                pd = Products_details.objects.get(product=i, language=ln)
                itemsarr.append({
                    'main_img': i.main_img,
                    'id': i.id,
                    'title': pd.title,
                    'status': i.status.status,
                    'scolor': i.status.color,
                    'price': i.price,
                    'currency':"SAR",
                    'pop': i.is_popular
                })
            context['items'] = itemsarr
            context['set'] = True

            return render(request, 'app/a-items.html', context)
    else:
        return redirect("/login.html")

# def setlistforadmnew(request):
#     if request.user.is_authenticated:
#         if request.user.is_admin:
#             context = {}
#             ln = Languages.objects.get(iso_3166_a2='EN')
#             ist = ItemStatus.objects.get(status="Moderate")
#             items = Products.objects.filter(in_active=True, status=ist, is_set=True).order_by("-id")
#
#             itemsarr = []
#             for i in items:
#                 pd = Products_details.objects.get(product=i, language=ln)
#                 itemsarr.append({
#                     'main_img': i.main_img,
#                     'id': i.id,
#                     'title': pd.title,
#                     'status': i.status.status,
#                     'scolor': i.status.color,
#                     'price': i.price,
#                     'currency':"SAR",
#                     'pop': i.is_popular
#                 })
#             context['items'] = itemsarr
#
#             return render(request, 'app/a-items.html', context)
#     else:
#         return redirect("/login.html")

def setlistforadmpop(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            context = {}
            ln = Languages.objects.get(iso_3166_a2='EN')
            items = Products.objects.filter(in_active=True, is_popular=True, is_set=True).order_by("-id")

            itemsarr = []
            for i in items:
                pd = Products_details.objects.get(product=i, language=ln)
                itemsarr.append({
                    'main_img': i.main_img,
                    'id': i.id,
                    'title': pd.title,
                    'status': i.status.status,
                    'scolor': i.status.color,
                    'price': i.price,
                    'currency':"SAR",
                    'pop': i.is_popular
                })
            context['items'] = itemsarr

            return render(request, 'app/a-items.html', context)
    else:
        return redirect("/login.html")

def setpop(request, id):
    if request.user.is_authenticated:
        if request.user.is_admin:

            gg = Products.objects.get(id=id)
            gg.is_popular = True
            gg.save()
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect("/login.html")

def unsetpop(request, id):
    if request.user.is_authenticated:
        if request.user.is_admin:
            gg = Products.objects.get(id=id)
            gg.is_popular = False
            gg.save()
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect("/login.html")

def ban(request, id):
    if request.user.is_admin:
        uzver = MyUser.objects.get(id=id)
        uzver.is_active = False
        uzver.save()
        return redirect(request.META.get('HTTP_REFERER'))

def unban(request, id):
    if request.user.is_admin:
        uzver = MyUser.objects.get(id=id)
        uzver.is_active = True
        uzver.save()
        return redirect(request.META.get('HTTP_REFERER'))

def confirmorder(request, id):
    gg = Orders.objects.get(id=id)
    if request.user.id == gg.user.id:
        gg.status = True
        gg.save()
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect(request.META.get('HTTP_REFERER'))

def astat(request):
    if request.user.is_authenticated:
        aa = datetime.date.today()
        cmonth = aa.month
        cyear = aa.year
        sdate = datetime.date.today()
        start_week = sdate - datetime.timedelta(sdate.weekday())
        end_week = start_week + datetime.timedelta(7)
        if request.user.is_admin:

            gg = Orders.objects.all()
            today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
            today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)


            gg1 = Orders.objects.filter(create_date__range=(today_min, today_max))
            gg2 = Orders.objects.filter(create_date__range=[start_week, end_week])
            gg3 = Orders.objects.filter(create_date__month=cmonth,create_date__year=cyear )

            total = 0
            today = 0
            this_week = 0
            this_month = 0

            for i in gg:
                if i.is_paid:
                    total += i.total_amount
            for i in gg1:
                if i.is_paid:
                    today += i.total_amount
            for i in gg2:
                if i.is_paid:
                    this_week += i.total_amount
            for i in gg3:
                if i.is_paid:
                    this_month += i.total_amount
            k = 1
            grapharr = []


            cyear = aa.year
            mdays = calendar.monthrange(cyear,cmonth)
            md = mdays[1]
            ii = 1
            while ii<= md:
                k = ii

                gg3 = Orders.objects.filter(create_date__month=cmonth,create_date__day=k)
                total_for_graph = 0
                for i in gg3:
                    if i.is_paid:
                        total_for_graph += i.total_amount
                if len(str(k)) == 1:
                    s = str(k)
                    k = "0" + s
                if len(str(cmonth)) == 1:
                    s = str(cmonth)
                    cmonth = "0" + s
                grapharr.append({
                    'month' : "%s-%s" %(k, cmonth),
                    'sum'   : int(total_for_graph)
                })
                ii+=1

            dict = {}
            dict['today'] = today
            dict['total'] = total
            dict['this_week'] = this_week
            dict['this_month'] = this_month
            dict['grapharr'] = grapharr

            return render(request, 'app/a-statistics.html', dict)
        else:

            gg = Orders.objects.filter(user = request.user)
            today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
            today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
            startweek = datetime.date.today()
            endweek = datetime.datetime.combine(startweek + timedelta(days=6), datetime.time.max)
            endmonth = datetime.datetime.combine(startweek + timedelta(days=31), datetime.time.max)
            gg1 = Orders.objects.filter(create_date__range=(today_min, today_max), user = request.user)
            gg2 = Orders.objects.filter(create_date__range=[start_week, end_week], user = request.user)
            gg3 = Orders.objects.filter(create_date__month=cmonth,create_date__year=cyear,user = request.user)

            total = 0
            today = 0
            this_week = 0
            this_month = 0

            for i in gg:
                if i.is_paid:
                    total += i.total_amount
            for i in gg1:
                if i.is_paid:
                    today += i.total_amount
            for i in gg2:
                if i.is_paid:
                    this_week += i.total_amount
            for i in gg3:
                if i.is_paid:
                    this_month += i.total_amount
            k = 1
            grapharr = []
            aa = datetime.date.today()
            cmonth = aa.month

            cyear = aa.year
            mdays = calendar.monthrange(cyear, cmonth)
            md = mdays[1]
            ii = 1
            while ii <= md:
                k = ii

                gg3 = Orders.objects.filter(create_date__month=cmonth, create_date__day=k, user = request.user)
                total_for_graph = 0
                for i in gg3:
                    if i.is_paid:
                        total_for_graph += i.total_amount
                if len(str(k)) == 1:
                    s = str(k)
                    k = "0" + s
                if len(str(cmonth)) == 1:
                    s = str(cmonth)
                    cmonth = "0" + s
                grapharr.append({
                    'month': "%s-%s" % (k, cmonth),
                    'sum': int(total_for_graph)
                })
                ii += 1
            dict = {}
            dict['today'] = today
            dict['total'] = total
            dict['this_week'] = this_week
            dict['this_month'] = this_month
            dict['grapharr'] = grapharr

            return render(request, 'app/a-statistics.html', dict)
    else:
        return redirect("/login.html")

@csrf_exempt
def freshorders(request):

    id = request.POST.get('id')

    uz = MyUser.objects.get(id=id)
    gg = Orders.objects.filter(user=uz, is_paid = True, status=False).count()

    return HttpResponse(json.dumps({'gg':gg}).encode('utf8'), content_type='application/json')


def createset(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            context = {}
            ln = Languages.objects.get(iso_3166_a2='EN')
            # cr = Currencies.objects.all()
            # co = Countries.objects.all()
            # rg = Region.objects.all()
            ct = Categories.objects.all()
            cta = []
            for i in ct:
                # print(i.cat_name)
                # ctd = CategoryDetails.objects.get(language=ln, category=i)
                # cta.append(ctd.title)
                cta.append(i.cat_name)

            context['languages'] = ln
            context['categories'] = cta

            st = ItemStatus.objects.get(status="Active")

            prod = Products.objects.filter(in_active = True, status = st, is_set = False)
            prodarr = []
            for i in prod:
                hh = Products_details.objects.get(product = i, language = ln)
                prodarr.append({'main_img': i.main_img,
                                'id': i.id,
                                'title': hh.title})
            context['prods'] = prodarr


            return render(request, 'app/a-createset.html', context)
        else:
            return redirect("/")
    else:
        return redirect("/login.html")


def createsethandler(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            try:
                its = request.POST.getlist('images[]')
                pr = 999
                main_photo = request.FILES['upload']
                gall_photo = request.FILES.getlist('images')

                ent = request.POST.get('ent')
                art = request.POST.get('art')
                ardes = "no description"
                endes = "no description"

                ist = ItemStatus.objects.get(status="Active")


                gg = Products(vendor=request.user, price=float(pr), main_img=main_photo, status=ist, is_set=True)
                gg.save()
                arleng = Languages.objects.get(iso_3166_a2='AR')
                enleng = Languages.objects.get(iso_3166_a2='EN')

                if gall_photo != []:
                    for i in gall_photo:
                        try:
                            gg5 = Gallery_Photo(item=gg, photo=i)
                            gg5.save()
                        except:
                            print('err')

                else:
                    print("LOLOLOLOLO")

                gg2 = Products_details(product=gg, title=art, descriptions=ardes, language=arleng)
                gg3 = Products_details(product=gg, title=ent, descriptions=endes, language=enleng)

                gg2.save()
                gg3.save()
                for i in its:
                    tt = Products.objects.get(id = int(i))
                    kk = Itemsinset(set = gg, item = tt )
                    kk.save()

                return redirect('/admin-sets')
            except:
                 return redirect('/createset')


def editset(request, id):
    if request.user.is_authenticated:

        prod = Products.objects.get(id=id)
        if request.user == prod.vendor or request.user.is_admin:
            enln = Languages.objects.get(iso_3166_a2='EN')
            arln = Languages.objects.get(iso_3166_a2='AR')
            st = ItemStatus.objects.get(status="Active")

            enprod = Products_details.objects.get(product=prod, language=enln)
            arprod = Products_details.objects.get(product=prod, language=arln)
            context = {}
            ln = Languages.objects.get(iso_3166_a2='EN')

            yy = Itemsinset.objects.filter(set = prod)
            iisar = []
            for i in yy:
                hh = Products_details.objects.get(product = i.item, language = enln)

                iisar.append({
                    "id": i.item.id,
                    "name": hh.title,


                })

            prod2 = Products.objects.filter(in_active=True, status=st, is_set=False)
            prodarr = []
            for i in prod2:
                hh = Products_details.objects.get(product=i, language=ln)
                prodarr.append({'main_img': i.main_img,
                                'id': i.id,
                                'title': hh.title})
            context['prods'] = prodarr
            context['languages'] = ln
            context['t_price'] = prod.price
            context['t_img'] = prod.main_img
            context['t_ent'] = enprod.title
            context['t_art'] = arprod.title
            context['t_id'] = prod.id
            context['iisar'] = iisar
            print(iisar)

            context['t_gimg'] = Gallery_Photo.objects.filter(item=prod)

            return render(request, 'app/editset.html', context)
        else:
            return redirect('/itemlist')
    else:
        return redirect("/login.html")




def editsethandler(request):
    if request.user.is_authenticated:
        if request.user.is_admin:
            # try:
            try:
                its = request.POST.getlist('images[]')
                main_photo = request.FILES['upload']
                gall_photo = request.FILES.getlist('images')
            except:
                pass

            ent = request.POST.get('ent')
            art = request.POST.get('art')
            ardes = "no description"
            endes = "no description"

            ist = ItemStatus.objects.get(status="Active")


            gg = Products.objects.get(id =request.POST.get('id') )
            try:
                gg.main_img=main_photo
            except:
                pass

            gg.save()
            arleng = Languages.objects.get(iso_3166_a2='AR')
            enleng = Languages.objects.get(iso_3166_a2='EN')
            try:
                if gall_photo != []:
                    for i in gall_photo:
                        try:
                            gg5 = Gallery_Photo(item=gg, photo=i)
                            gg5.save()
                        except:
                            print('err')

                else:
                    print("LOLOLOLOLO")
            except:
                pass

            gg2 = Products_details.objects.get(product=gg, language=arleng)
            gg2.title=art
            gg3 = Products_details.objects.get(product=gg, language=enleng)
            gg3.title = ent

            gg2.save()
            gg3.save()
            for i in its:
                tt = Products.objects.get(id = int(i))
                kk = Itemsinset(set = gg, item = tt )
                kk.save()

            return redirect('/admin-sets')
            # except:
            #      return redirect('/admin-sets')





def logo(request):

    if request.user.is_authenticated:
        gg = Logo.objects.filter(uzver = request.user)

        ara = []
        for i in gg:
            ara.append({
                "img": i.logo_img,
                "name": i.logo_name
            })
        context = {}
        context['logos'] = ara

        return render(request, 'app/logo.html', context)
    else:
        return redirect("/login.html")

def addlogohandler(request):
    if request.user.is_authenticated:
        try:
            name = request.POST.get('price')
            main_photo = request.FILES['upload']
            gg = Logo(uzver = request.user, logo_img = main_photo, logo_name = name)
            gg.save()
            return redirect('/logo')

        except:
            return redirect('/logo')

    else:
        return redirect("/login.html")
