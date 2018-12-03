from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.conf import settings


class MyUserManager(BaseUserManager):
    def create_user(self, phone, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not phone:
            raise ValueError('Вы не ввели номер телефона')

        user = self.model(
            phone=phone,

        )

        user.set_password(password)
        user.save(using=self._db)
        #Следующая строчна необходима для предоставления админки всем новым пользователям
        #user.is_admin = True
        return user

    def create_superuser(self, phone, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            phone,
            password=password,

        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    # email = models.EmailField(
    #     verbose_name='email address',
    #     max_length=255,
    #     unique=True,
    # )
    phone = models.CharField(max_length=16, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    token = models.CharField(max_length=256)
    photo = models.FileField(blank=True)

    newbe = models.BooleanField(default=True)
    objects = MyUserManager()

    USERNAME_FIELD = 'phone'
    #REQUIRED_FIELDS = ['date_of_birth']


    def get_full_name(self):
        # The user is identified by their email address
        return "%s %s" %(self.first_name, self.last_name)

    def get_short_name(self):
        # The user is identified by their email address
        return self.first_name

    def __str__(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission? "
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin



class Languages(models.Model):

    title = models.CharField(max_length=64)
    iso_3166_a2 = models.CharField(max_length=2)

    def __str__(self):
        return self.title


class Currencies(models.Model):

    title = models.CharField(max_length=64)
    iso_4217 = models.CharField(max_length=3)

    def __str__(self):
        return self.title

class Countries(models.Model):

    iso_3166_a2 = models.CharField(max_length=2)
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class CountryDetails(models.Model):

    iso_3166_a2 = models.CharField(max_length=2)
    language = models.ForeignKey(Languages, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Categories(models.Model):

    cat_name = models.CharField(max_length=256)
    cat_img = models.ImageField(blank=True, upload_to='img')

    def __str__(self):
        return self.cat_name



class CategoryDetails(models.Model):

    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    language = models.ForeignKey(Languages, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)

    def __str__(self):
        return self.title


class Region(models.Model):

    reg_name = models.CharField(max_length=256)
    reg_country = models.ForeignKey(Countries, on_delete=models.CASCADE)

    def __str__(self):
        return self.reg_name


class RegionDetails(models.Model):

    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    language = models.ForeignKey(Languages, on_delete=models.CASCADE)
    title = models.CharField(max_length=64)

    def __str__(self):
        return self.title


class ItemStatus(models.Model):

    status = models.CharField(max_length=64)
    color = models.CharField(max_length=32)


class Logo(models.Model):

    uzver = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    logo_img = models.ImageField(blank=True, upload_to='img',)
    logo_name = models.CharField(max_length= 64)


class Products(models.Model):

    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, blank=True, null=True)
    #currency = models.ForeignKey(Currencies, on_delete=models.CASCADE)
    price = models.FloatField(default=0)
    city = models.IntegerField(default=0)
    kids_price = models.FloatField(default=0)
    #delivery_price = models.FloatField(default=0)
    create_date = models.DateTimeField(auto_now=True)
    #iso_3166_a2 = models.ForeignKey(Countries, on_delete=models.CASCADE)
    #region = models.ForeignKey(Region, on_delete=models.CASCADE)
    main_img = models.ImageField(upload_to='img', blank=True)
    is_set = models.BooleanField(default=False)
    in_active = models.BooleanField(default=True)
    status = models.ForeignKey(ItemStatus, on_delete=models.CASCADE)
    is_popular = models.BooleanField(default=False)
    logo = models.ForeignKey(Logo, on_delete=models.CASCADE, blank=True, null=True)
    share = models.TextField(default="gg wp")
    location = models.CharField(max_length=40)
    reservdate = models.CharField(max_length=1000,  blank=True, null=True, default='')

class Products_details(models.Model):

    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    language = models.ForeignKey(Languages, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    descriptions = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Order_statuses(models.Model):

    finished = models.BooleanField(default=False)


class Order_status_detail(models.Model):
    order_status = models.ForeignKey(Order_statuses, on_delete=models.CASCADE)
    language = models.ForeignKey(Languages, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)


class Orders(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_amount = models.FloatField(default=0.0)
    currencies = models.ForeignKey(Currencies, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now=True)
    delivery_adress = models.CharField(max_length=420)
    delivery_datetime = models.CharField(max_length=100)
    count = models.IntegerField(default=1)
    kids_count = models.IntegerField(default=0)
    buyer_fullname = models.CharField(max_length=200)
    buyer_phone = models.CharField(max_length=200)
    checkid = models.CharField(max_length=200)
    is_paid = models.BooleanField(default=False)
    birthday = models.CharField(max_length= 36, blank=True)
    city = models.CharField(max_length= 36,blank=True)
    sex = models.CharField(max_length= 36,blank=True)
    description = models.TextField(blank=True)
    description_img = models.ImageField(blank=True, upload_to='img',)


class OrdersItems(models.Model):

    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    item = models.ForeignKey(Products, on_delete=models.CASCADE)


class Exchange_Rates(models.Model):

    exchange_from = models.ForeignKey(Currencies, on_delete=models.CASCADE, related_name='exchange_from')
    exchange_to = models.ForeignKey(Currencies, on_delete=models.CASCADE, related_name='exchange_to')


class Gallery_Photo(models.Model):

    photo = models.FileField(upload_to = 'img')
    item = models.ForeignKey(Products, on_delete=models.CASCADE)


class ItemSet(models.Model):

    vendor = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    img = models.FileField()
    in_active = models.BooleanField(default=True)
    price = models.FloatField(default=0)
    delprice = models.FloatField(default=0)
    currency = models.ForeignKey(Currencies, on_delete=models.CASCADE)
    iso_3166_a2 = models.ForeignKey(Countries, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)


class Set_details(models.Model):

    set = models.ForeignKey(ItemSet, on_delete=models.CASCADE)
    language = models.ForeignKey(Languages, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    descriptions = models.TextField()





class Itemsinset(models.Model):

    set = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='set')
    item = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='item_in_set')
