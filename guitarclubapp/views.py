from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.http import HttpResponse

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, QueryDict
from django.template.response import TemplateResponse
from django.utils.http import base36_to_int, is_safe_url, urlsafe_base64_decode, urlsafe_base64_encode

from guitarclubapp.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
# Create your views here.
from django.contrib import auth

from forms import formForm

from models import Generes

import string

# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator

#for email activation
import datetime
import random
import sha
import hashlib
from django.core.mail import send_mail
from guitarclubapp.models import UserProfile
from django.shortcuts import get_object_or_404
from django.utils import timezone

#userprofileforms
from forms import UserProfileForm

#userFollowActivity
from models import userFollowActivity
from forms import userFollowActivityForm

#multichoice forms
from forms import multiChoiceForm
from models import multiChoice

#guestpage
def guestpage(request):
    c={}
    c.update(csrf(request))

    args = {}
    args.update(csrf(request))

    args['form'] = MyRegistrationForm()


    return render_to_response('guestpage.html', args)
    #return render_to_response('guestpage.html',c)



def login(request):
    c={}
    c.update(csrf(request))
    return render_to_response('login.html',c)



def auth_view(request):
    username = request.POST.get('Username', '')
    password = request.POST.get('Password', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        # Correct password, and the user is marked "active"
        auth.login(request, user)
        # Redirect to a success page.
        return HttpResponseRedirect("/accounts/loggedin/")
    else:
        # Show an error page
        #return render_to_response("testit.html" ,{'username':username , 'password':password})
        return HttpResponseRedirect("/accounts/invalid/")

def loggedin(request):
    return render_to_response("home.html", {"full_name":request.user.username})

def invalid_login(request):
    return render_to_response("invalid_login.html")

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/guest_login/")
    #return render_to_response("loggedout.html")

#new user registration

@csrf_protect
def register_user(request):
    args = {}
    args.update(csrf(request))
    if request.method == 'POST':
        form = MyRegistrationForm(request.POST)
        args['form'] = form
        if form.is_valid():
            form.save()  # save user to database if form is valid
            username = form.cleaned_data['username']
            email = form.cleaned_data['username']
            password=form.cleaned_data['password1']
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']


            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
            activation_key = hashlib.sha1(salt+email).hexdigest()
            key_expires = datetime.datetime.today() + datetime.timedelta(2)

            #Get user by username
            user=User.objects.get(username=username)

            # Create and save user profile
            new_profile = UserProfile(user=user, activation_key=activation_key,
                key_expires=key_expires)
            new_profile.save()

            # Send email with activation key
            email_subject = 'Account confirmation'
            email_body = "Hey %s, thanks for signing up. To activate your account, click this link within \
            48hours http://pakumar1.pythonanywhere.com/accounts/confirm/%s" % (username, activation_key)

            send_mail(email_subject, email_body, 'pawan.kumar.13.1991@gmail.com',
                [email], fail_silently=False)

            return HttpResponseRedirect('/accounts/register/activate')
    else:
        args['form'] = MyRegistrationForm()

    return render_to_response('guestpage.html', args, context_instance=RequestContext(request))
        #return HttpResponseRedirect('/accounts/register/success/')

def register_activate(request):
    return render_to_response('register_activate.html')

def register_confirm(request, activation_key):
    #check if user is already logged in and if he is redirect him to some other url, e.g. home
    if request.user.is_authenticated():
        HttpResponseRedirect('/accounts/loggedin/')

    # check if there is UserProfile which matches the activation key (if not then display 404)
    user_profile = get_object_or_404(UserProfile, activation_key=activation_key)

    #check if the activation key has expired, if it hase then render confirm_expired.html
    #if user_profile.key_expires < timezone.now():
    #    return render_to_response('activation_confirm_expired.html')
    #if the key hasn't expired save user and set him as active and render some template to confirm activation
    user = user_profile.user
    user.is_active = True
    user.save()
    return render_to_response('activation_confirm.html')


def register_success(request):
    return render_to_response('register_success.html')




@login_required
def home(request):
    return render_to_response('home.html',{ 'user': request.user })

def logout_view(request):
    auth.logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/account/loggedout/")


# 4 views for password reset:
# - password_reset sends the mail
# - password_reset_done shows a success message for the above
# - password_reset_confirm checks the link the user clicked and
#   prompts for a new password
# - password_reset_complete shows a success message for the above
def password_reset(request):
    # Wrap the built-in password reset view and pass it the arguments
    # like the template name, email template name, subject template name
    # and the url to redirect after the password reset is initiated.
    return password_reset(request, template_name='password_reset.html',
        email_template_name='password_reset_email.html',
        subject_template_name='reset_subject.txt',
        post_reset_redirect=reverse('success'))

# This view handles password reset confirmation links. See urls.py file for the mapping.
# This view is not used here because the password reset emails with confirmation links
# cannot be sent from this application.
def password_reset_confirmation(request, uidb36=None, token=None):
    # Wrap the built-in reset confirmation view and pass to it all the captured parameters like uidb64, token
    # and template name, url to redirect after password reset is confirmed.
    return password_reset_confirm(request, template_name='password_reset_confirmation.html',
        uidb36=uidb36, token=token, post_reset_redirect=reverse('success'))


# This view renders a page with success message.
def password_reset_success(request):
  return render(request, "password_reset_success.html")

def password_resetv1(request, is_admin_site=False,
                   template_name='password_reset.html',
                   email_template_name='password_reset_email.html',
                   subject_template_name='reset_subject.txt',
                   password_reset_form=PasswordResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect=None,
                   from_email=None,
                   current_app=None,
                   extra_context=None):
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_done')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
            }
            if is_admin_site:
                opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form': form,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)

def password_reset_done(request,
                        template_name='registration/password_reset_done.html',
                        current_app=None, extra_context=None):
    context = {}
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)

#edit profile
@csrf_protect
@login_required
def edit_profile(request):
    args = {}
    args.update(csrf(request))
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        follow = userFollowActivity.objects.get(user=request.user)
        generes = Generes.objects.get(user=request.user)

        first_name = request.user.first_name
        last_name = request.user.last_name
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/loggedin/')
    else:
        form=UserProfileForm(instance=request.user.profile)
        generes = Generes.objects.get(user=request.user)
        follow = userFollowActivity.objects.get(user=request.user)
        first_name = request.user.first_name
        last_name = request.user.last_name

    args={}
    args.update(csrf(request))
    args['form']=form

    return render_to_response('editprofilepage.html',  {'form':form , 'follow':follow, 'first_name':first_name , 'last_name':last_name, 'generes':generes},context_instance=RequestContext(request))


#pawan --> bandfollow test
def userFollow(request):
    args = {}
    args.update(csrf(request))
    if request.method == 'POST':
        form = userFollowActivityForm(request.POST, instance=request.user.follow)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/loggedin/')
    else:
        form=userFollowActivityForm(instance=request.user.follow)
    args={}
    args.update(csrf(request))
    args['follow']=form

    return render_to_response('editprofile_v1.html', args)
#Multi Choice Check
def multiChoice_v1(request):
    args = {}
    args.update(csrf(request))
    if request.method == 'POST':
        form = multiChoiceForm(request.POST)
        if form.is_valid():
            countries = form.cleaned_data.get('countries')
            countries.save()
            form.save_m2m()
            return HttpResponseRedirect('/accounts/loggedin/')
    else:
        form=multiChoiceForm()
    args={}
    args.update(csrf(request))
    args['form']=form

    return render_to_response('editprofile_v2.html', {'form':form})


def editprofilepage(request):
    return render_to_response('editprofilepage.html')



#########################################Search for users####################################
from django.db.models import Q
@login_required
def search(request):
    q = request.GET.get('q')
    test = None
    if q is not None:
        test= UserProfile.objects.select_related("user").filter(Q(user__first_name__contains = q)
        | Q(user__last_name__contains = q)
        | Q(user__username__contains = q ))
    return render_to_response( 'search.html', { 'pp':test},  context_instance = RequestContext(request))


########################view profile page###################################################
@login_required
def viewprofile(request , user_id = 40):
    test= UserProfile.objects.select_related("user").get(user = user_id)
    follow = userFollowActivity.objects.get(user=user_id)

    return render_to_response('viewprofilepage.html',  {'form':test , 'follow':follow},context_instance=RequestContext(request))
###################################################################

############################add friend#############################
"""
Views
=====

.. _class-based-views:

Class Based Views
-----------------

All the views are implemented as
`classes <https://docs.djangoproject.com/en/dev/topics/class-based-views/>`_
but :ref:`view functions <view-functions>` are also provided.

.. autoclass:: BaseActionView
    :members:

.. autoclass:: FriendshipAcceptView

.. autoclass:: UserBlockView

.. autoclass:: FriendshipCancelView

.. autoclass:: FriendshipDeclineView

.. autoclass:: FriendshipDeleteView

.. autoclass:: FriendshipRequestView

.. autoclass:: UserUnblockView


.. _view-functions:

View Functions
--------------

.. tip::

    If you want to customize the views provided, check out
    :ref:`class-based-views` first.

.. autofunction:: friendship_request

.. autofunction:: friendship_accept

.. autofunction:: friendship_decline

.. autofunction:: friendship_cancel

.. autofunction:: friendship_delete

.. autofunction:: user_block

.. autofunction:: user_unblock
"""

from django.http import HttpResponseBadRequest, Http404
from django.db import transaction
from django.views.generic.base import RedirectView
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from models import FriendshipRequest, Friendship
from app_settings import REDIRECT_FALLBACK_TO_PROFILE


class BaseActionView(RedirectView):
    """
    Base class for action views.
    """

    http_method_names = ['get', 'post']
    permanent = False

    def action(request, user, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement action()")

    def get(self, request, username, *args, **kwargs):
        if request.user.username == username:
            return HttpResponseBadRequest(
                ugettext(u'You can\'t befriend yourself.'),
            )
        user = get_object_or_404(User, username=username)
        self.action(request, user, *args, **kwargs)
        self.set_url(request, **kwargs)
        return super(BaseActionView, self).get(request, **kwargs)

    def set_url(self, request, **kwargs):

        #return render_to_response("home.html",{'kwargs':kwargs})
        """
        Set the ``url`` attribute so that it can be used when
        :py:meth:`~django.views.generic.base.RedirectView.get_redirect_url` is
        called.

        ``url`` is determined using the following methods, in order:

        - It can be set in the urlconf using ``redirect_to`` keyword argument.
        - If ``redirect_to_param`` keyword argument is set in urlconf, the
          request parameter with that name will be used. In this case the
          request parameter **must** be provided in runtime.
        - If the request has ``redirect_to`` to parameter is present, its
          value will be used.
        - If ``REDIRECT_FALLBACK_TO_PROFILE`` setting is ``True``, current
          user's profile URL will be used.
        - ``HTTP_REFERER`` header's value will be used if exists.
        - If all else fail, ``'/'`` will be used.
        """
        if 'redirect_to' in kwargs:
            self.url = kwargs['redirect_to']
        elif 'redirect_to_param' in kwargs and \
             kwargs['redirect_to_param'] in request.REQUEST:
            self.url = request.REQUEST[kwargs['redirect_to_param']]
        elif 'redirect_to' in request.REQUEST:
            self.url = request.REQUEST['next']
        elif REDIRECT_FALLBACK_TO_PROFILE:
            self.url = request.user.get_profile().get_absolute_url()
        else:
            self.url = request.META.get('HTTP_REFERER', '/accounts/loggedin/')
            #return render_to_response("friend/friendrequest_accepted.html")


class FriendshipAcceptView(BaseActionView):
    @transaction.commit_on_success
    def accept_friendship(self, from_user, to_user):
        get_object_or_404(
            FriendshipRequest,
            from_user=from_user,
            to_user=to_user,
        ).accept()

    def action(self, request, user, **kwargs):
        self.accept_friendship(user, request.user)
        #return render_to_response("friend/friendrequest_accepted.html" , { 'to_user':user } )

class FriendshipRequestView(FriendshipAcceptView):
    @transaction.commit_on_success
    def action(self, request, user, **kwargs):
        if Friendship.objects.are_friends(request.user, user):
            raise RuntimeError(
                '%r and %r are already friends' % (request.user, user),
            )
        try:
            # If there's a friendship request from the other user accept it.
            self.accept_friendship(user, request.user)

        except Http404:
            request_message = request.REQUEST.get('message', u'Hi, add me as your friend')
            # If we already have an active friendship request IntegrityError
            # will be raised and the transaction will be rolled back.
            FriendshipRequest.objects.create(from_user=request.user, to_user=user, message=request_message,)
            #return render_to_response("friend/friendrequest_sent.html" , {'to_user' : user } )


class FriendshipDeclineView(BaseActionView):
    def action(self, request, user, **kwargs):
        get_object_or_404(FriendshipRequest,
                          from_user=user,
                          to_user=request.user).decline()


class FriendshipCancelView(BaseActionView):
    def action(self, request, user, **kwargs):
        get_object_or_404(FriendshipRequest,
                          from_user=request.user,
                          to_user=user).cancel()


class FriendshipDeleteView(BaseActionView):
    def action(self, request, user, **kwargs):
        Friendship.objects.unfriend(request.user, user)


class UserBlockView(BaseActionView):
    def action(self, request, user, **kwargs):
        request.user.user_blocks.blocks.add(user)


class UserUnblockView(BaseActionView):
    def action(self, request, user, **kwargs):
        request.user.user_blocks.blocks.remove(user)


friendship_request = login_required(FriendshipRequestView.as_view())
friendship_accept = login_required(FriendshipAcceptView.as_view())
friendship_decline = login_required(FriendshipDeclineView.as_view())
friendship_cancel = login_required(FriendshipCancelView.as_view())
friendship_delete = login_required(FriendshipDeleteView.as_view())
user_block = login_required(UserBlockView.as_view())
user_unblock = login_required(UserUnblockView.as_view())


#for friends Snippet
#test

@login_required
def friend_list(request):
    return render_to_response("friend/add_new.html")


def fr(
                username=None,
                paginate_by=None,
                page=None,
                allow_empty=True,
                template_name='friend/friends_list.html',
                extra_context=None,
                template_object_name='friends'):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    friends = Friendship.objects.friends_of(user)
    if extra_context is None:
        extra_context = {}
    incoming_requests = FriendshipRequest.objects.filter( to_user=request.user,accepted=False)
    outgoing_requests = FriendshipRequest.objects.filter( from_user=request.user,accepted=False)
    extra_context['sender_user'] = request.user
    extra_context['target_user'] = user
    extra_context['friendship_requests'] = {'incoming':incoming_requests,'outgoing':outgoing_requests}
    extra_context['user_blocks'] =request.user.user_blocks.blocks.all()
    return object_list(request,
                       queryset=friends,
                       paginate_by=paginate_by,
                       page=page,
                       allow_empty=allow_empty,
                       template_name=template_name,
                       extra_context=extra_context,
                       template_object_name=template_object_name)




def test(request):
    return render_to_response('profile.html')



#PopUp for generes Liked
@csrf_protect
@login_required
def generes_view(request):
    args = {}
    args.update(csrf(request))
    if request.method == 'POST':
        form = formForm(request.POST, instance=request.user.generes)
        if form.is_valid():
            form.save()




            #return render_to_response(request,'generes_return.html',{'form':form})
            return HttpResponseRedirect('/accounts/profile_v3/generes/return/')
    else:
        form = formForm(instance=request.user.generes)
    args={}
    args.update(csrf(request))
    args['generes']=form

    return render_to_response('choose_generes.html', args,
        context_instance=RequestContext(request))


def generes_choose(request):
    return render (request,'popup_generes.html')

def generes_return(request):
    return render (request,'generes_return.html')

#display generes
#@login_required
#def display(request):
#    generes1 = Generes.objects.filter(user=request.user)
#    return render (request, 'generes_display.html', {'music_generes' : generes1})


