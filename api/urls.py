from django.conf.urls import url
from api import views

urlpatterns = [
    # Matches any html file - to be used for gentella
    # Avoid using your .html in your resources.
    # Or create a separate django app.

    # The home page
    #url(r'^$', views.mainpage, name='index'),
    url(r'get-home-page', views.get_home_page, name='get_home_page'),
    url(r'get-items-by-category', views.get_items_by_category, name='get_items_by_category'),
    url(r'get-items-details', views.get_items_details, name='get_items_details'),
    url(r'get-set-details', views.get_set_details, name='get_set_details'),
    url(r'prepear-checkout', views.prepear_checkout, name='prepear_checkout'),
    url(r'test', views.test, name='test'),
    url(r'paycheck', views.paycheck, name='paycheck'), ### paycheck
    url(r'poycheck', views.poycheck, name='poycheck'), ### poycheck for ios
    url(r'get-items-by-keyword', views.get_items_by_keyword, name='get_items_by_keyword'),
    url(r'search-items-by-keyword', views.search_items_by_keyword, name='search_items_by_keyword'),
    url(r'search-for-set', views.search_for_set, name='search_for_set'),
    url(r'get-wishlist', views.get_wishlist, name='get_wishlist'),
    url(r'get-sets', views.get_sets, name='get_sets'),

]