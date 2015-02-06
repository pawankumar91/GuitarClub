from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout
from django.contrib.auth import views as auth_views

from django.conf.urls import patterns, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'guitarclub.views.home', name='home'),
    #url(r'^$', 'django.contrib.auth.views.login'),

    url(r'^$', 'guitarclubapp.views.guestpage'),
    url(r'^guest_login/$', 'guitarclubapp.views.guestpage'),

    url(r'^accounts/login/$',  'guitarclubapp.views.guestpage'),
    url(r'^accounts/auth/$',  'guitarclubapp.views.auth_view'),
    url(r'^accounts/logout/$',  'guitarclubapp.views.logout'),
    url(r'^accounts/loggedin/$', 'guitarclubapp.views.loggedin'),
    url(r'^accounts/invalid/$', 'guitarclubapp.views.invalid_login'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'), # If user is not login it will redirect to login page

    url(r'^accounts/register/$', 'guitarclubapp.views.register_user'),
    url(r'^accounts/register/success/', 'guitarclubapp.views.register_success'),
    url(r'^accounts/register/activate/', 'guitarclubapp.views.register_activate'),
    url(r'^accounts/confirm/(?P<activation_key>\w+)/', 'guitarclubapp.views.register_confirm'),


    #url(r'^accounts/register/success/$', 'guitarclubapp.views.register_success'),
    url(r'^accounts/password_reset/$', 'guitarclubapp.views.password_resetv1'),

          #override the default urls
      url(r'^password/change/$',
                    auth_views.password_change,
                    name='password_change'),
      url(r'^password/change/done/$',
                    auth_views.password_change_done,
                    name='password_change_done'),
      url(r'^password/reset/$',
                    auth_views.password_reset,
                    name='password_reset'),
      url(r'^password/reset/done/$',
                    auth_views.password_reset_done,
                    name='password_reset_done'),
      url(r'^password/reset/complete/$',
                    auth_views.password_reset_complete,
                    name='password_reset_complete'),
      url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
                    auth_views.password_reset_confirm,
                    name='password_reset_confirm'),

      #and now add the registration urls
      #url(r'', include('registration.backends.default.urls')),



    # Map the 'app.hello.reset_confirm' view that wraps around built-in password
    # reset confirmation view, to the password reset confirmation links.
    url(r'^accounts/password_reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'guitarclubapp.views.password_reset_confirmation'),
    # Map the 'app.hello.success' view to the success message page.
    url(r'^accounts/success/$', 'guitarclubapp.views.password_reset_success'),


#edit profile
url(r'^accounts/profile/$', 'guitarclubapp.views.edit_profile'),

#searchbar
url(r'^search/$', 'guitarclubapp.views.search'),

#view profile page
url(r'^profiles/(?P<user_id>\d+)/$', 'guitarclubapp.views.viewprofile'),

url(r'^friend_list/$', 'guitarclubapp.views.friend_list'),



    url(r'^add/(?P<username>[\+\w\.@-_]+)/$',
        'guitarclubapp.views.friendship_request',
        name='friendship_request'),
    url(r'^accept/(?P<username>[\+\w\.@-_]+)/$',
        'guitarclubapp.views.friendship_accept',
        name='friendship_accept'),
    url(r'^decline/(?P<username>[\+\w\.@-_]+)/$',
        'guitarclubapp.views.friendship_decline',
        name='friendship_decline'),
    url(r'^cancel/(?P<username>[\+\w\.@-_]+)/$',
        'guitarclubapp.views.friendship_cancel',
        name='friendship_cancel'),
    url(r'^delete/(?P<username>[\+\w\.@-_]+)/$',
        'guitarclubapp.views.friendship_delete',
        name='friendship_delete'),
    url(r'^block/(?P<username>[\+\w\.@-_]+)/$',
        'guitarclubapp.views.user_block',
        name='user_block'),
    url(r'^unblock/(?P<username>[\+\w\.@-_]+)/$',
        'guitarclubapp.views.user_unblock',
        name='user_unblock'),



#Generes Popup URLs
        url(r'^accounts/profile_v3/generes/$', 'guitarclubapp.views.generes_view'),
        url(r'^accounts/profile_v3/$', 'guitarclubapp.views.generes_choose'),
        url(r'^accounts/profile_v3/generes/return/$', 'guitarclubapp.views.generes_return'),
        url(r'^accounts/profile/music/$', 'guitarclubapp.views.display'),




#################################################################All the test pages will be marked down with comments#######################################


#testeditprofile
url(r'^accounts/profile_v1/$', 'guitarclubapp.views.userFollow'),
url(r'^accounts/profile_v2/$', 'guitarclubapp.views.multiChoice_v1'),
url(r'^accounts/editprofile/$', 'guitarclubapp.views.editprofilepage'),


url(r'^test/$', 'guitarclubapp.views.test'),


    #url(r'^login/', 'guitarclubapp.views.login_view', name='login'),

    # url(r'^blog/', include('blog.urls')),
    #url(r'', include('registration.backends.default.urls')),
url(r'', include('django.contrib.auth.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
