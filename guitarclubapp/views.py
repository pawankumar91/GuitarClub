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

#band pages

from models import bandPage

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

@login_required
def loggedin(request):
    profile = UserProfile.objects.select_related("user").get(user__username = request.user)
    self = request.user
    return render_to_response("home.html", {'form':profile, 'self':self})

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



def navbar(id):
    profile= UserProfile.objects.select_related('user').get(user__id = id)
    return profile


#edit profile
@csrf_protect
@login_required
def edit_profile(request):
    args = {}
    args.update(csrf(request))
    #test navbar func
    self = navbar(request.user.id)

    #self = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        follow = userFollowActivity.objects.get(user=request.user)
        generes = Generes.objects.get(user=request.user)

 #       generes =u','.join(self.cleaned_data['generes'])
        first_name = request.user.first_name
        last_name = request.user.last_name
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/loggedin/')
    else:
        form=UserProfileForm(instance=request.user.profile)
        try:
            generes = Generes.objects.get(user=request.user)
        except Generes.DoesNotExist:
            generes = None
        follow = userFollowActivity.objects.get(user=request.user)
        first_name = request.user.first_name
        last_name = request.user.last_name

    args={}
    args.update(csrf(request))
    args['form']=form

    return render_to_response('editprofilepage.html',  {'from_user':self, 'self':self, 'form':form , 'follow':follow, 'first_name':first_name , 'last_name':last_name,'generes':generes}
    ,context_instance=RequestContext(request))


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




#########################################Search for users####################################
from django.db.models import Q
@login_required
def search(request):
    q = request.GET.get('q')
    self = request.user
    if q is not None:
        test= UserProfile.objects.select_related("user").filter(Q(user__first_name__contains = q)
        | Q(user__last_name__contains = q)
        | Q(user__username__contains = q ))
        profile = UserProfile.objects.select_related("user").get(user__username = request.user)
        from_user = profile.user.id
        for i in test:
            i.user1=from_user
            to_user = i.user.id
            i.user2 = str(from_user)+"|"+str(to_user)
    return render_to_response( 'search.html', { 'pp':test, 'form':profile , 'self':self,"to":to_user},  context_instance = RequestContext(request))

#form = self
########################view profile page###################################################
@login_required
def viewprofile(request , user_id = 40 , ctx = None):
    test= UserProfile.objects.select_related("user").get(user = user_id)
    follow = userFollowActivity.objects.get(user=user_id)
    c={}
    c.update(csrf(request))
    from_user = request.user.id
    to_user = test.user.id
    use = str(from_user)+"|"+str(to_user)
    self = request.user
    profile = UserProfile.objects.select_related("user").get(user__username = request.user)
    return render_to_response('viewprofilepage.html',  {'profile':test ,'form':profile, 'follow':follow, 'ctx':ctx, 'from_user':use, 'self':self}, context_instance = RequestContext(request) )
###################################################################

############################add friend#############################
from exception import AlreadyExistsError
from models import Friend, Follow, FriendshipRequest
from django.conf import settings
try:
    from django.contrib.auth import get_user_model
    user_model = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
    user_model = User

get_friendship_context_object_name = lambda: getattr(settings, 'FRIENDSHIP_CONTEXT_OBJECT_NAME', 'user')
get_friendship_context_object_list_name = lambda: getattr(settings, 'FRIENDSHIP_CONTEXT_OBJECT_LIST_NAME', 'users')


##view friends

def view_friends(request, username):
    """ View the friends of a user """
    user = get_object_or_404(user_model, username=username)
    qs = Friend.objects.select_related("UserProfile").filter(to_user=user)
    friends = [u.from_user for u in qs]
    return render_to_response( 'view_friends.html', {'friends': friends})


from django.contrib.auth.decorators import login_required


# add friends
@login_required
def friendship_add_friend(request, to_username):
    """ Create a FriendshipRequest """
    ctx = {'to_username': to_username}
    args = {}
    args.update(csrf(request))

    if request.method == 'POST':
        to_user = user_model.objects.get(username=to_username)
        from_user = request.user
        try:
            Friend.objects.add_friend(from_user, to_user)
        except AlreadyExistsError as e:
            ctx['errors'] = ["%s" % e]

        else:
            template = '/profiles/'+str(to_user.id)
            return HttpResponseRedirect(template)
    to_user = User.objects.get(username=to_username)
    template = '/profiles/'+str(to_user.id)
    return HttpResponseRedirect(template, ctx)

# all the request list[ throws list of all friend request ]
@login_required
def friendship_request_list(request, template_name='/friend/requests_list.html'):
    """ View unread and read friendship requests """
    # friendship_requests = Friend.objects.requests(request.user)
    friendship_requests = FriendshipRequest.objects.filter(rejected__isnull=True)

    return render(request, template_name, {'requests': friendship_requests})

# user friend requests
@login_required
def friend_requests(request):
    self = request.user
    return render(request,'friendship/template_ags/friend_requests.html', {'self':self})

#accept friend request
@login_required
def friendship_accept(request, friendship_request_id):
    """ Accept a friendship request """
    #if request.method == 'POST':
    #id1 = get_object_or_404(request.user.friendship_requests_sent,id=friendship_request_id)
    f_request = FriendshipRequest.objects.get(from_user=friendship_request_id, to_user = request.user)
    from_user = request.user
    f_request.accept()
    return render (request , 'reload_page.html')
    #return render(request,'friendship/template_ags/friend_requests.html', {'from_user':from_user})

#decline friend request
@login_required
def friendship_reject(request, friendship_request_id):
    """ Reject a friendship request """
    #if request.method == 'POST':
    #f_request = get_object_or_404(request.user.friendship_requests_received,id=friendship_request_id)
    f_request = FriendshipRequest.objects.get(from_user=friendship_request_id, to_user = request.user)
    from_user = request.user
    f_request.reject()
    return render(request , 'reload_page.html')
    #return render(request,'friendship/template_ags/friend_requests.html', {'from_user':from_user})

#friendship Revoke
def friendship_revoke(request , friendship_request_id):
    """revoke friend request"""
    FriendshipRequest.objects.filter(from_user=request.user,to_user=friendship_request_id).delete()
    url = '/profiles/'+str(request.user.id)+'/'
    return HttpResponseRedirect(url)

#unfriend
def friendship_unfriend(request , friendship_request_id):
    Friend.objects.get(to_user_id=request.user.id, from_user_id=friendship_request_id).delete()
    Friend.objects.get(from_user_id=request.user.id, to_user_id=friendship_request_id).delete()
    template = '/view/friends/'+str(request.user.email)
    return render(request , 'reload_page.html')
    #return HttpResponseRedirect(template)


#friendship clear notification
from django.db.models import F

def friendship_clearnotify(request, username):
    self = request.user.id
    to_user = User.objects.values_list('id', flat=True).get(email = username)
    this_update= Friend.objects.get(from_user_id = self , to_user_id = to_user)
    this_update.notify = F('notify')-1
    this_update.save()
    return render(request , 'reload_page.html')

#load friends friend
def friendship_friends_friend(request , friendship_request_id):
    user = get_object_or_404(user_model, id=friendship_request_id)
    friends = Friend.objects.friends(user)
    profile = UserProfile.objects.select_related("user").get(user__id = request.user.id)
    user1 = profile.user.id
    for i in friends:
        to_user = i.id
        i.user2 = str(user1)+"|"+str(to_user)
    return render_to_response('view_friend_friends.html', {'friends': friends, 'profile':profile})



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

############################
@login_required
def testtmp(request):
    return render_to_response("Band_page.html")

@login_required
def test(request , user_id = 40):
    test= UserProfile.objects.select_related("user").get(user = user_id)
    follow = userFollowActivity.objects.get(user=user_id)
    c={}
    c.update(csrf(request))

    return render_to_response('test.html',  {'form':test , 'follow':follow}, context_instance=RequestContext(request))

###############Views for Band Pages##############################
from django.contrib.formtools.wizard.views import SessionWizardView
from django.contrib.formtools.wizard.storage import get_storage
from django.contrib.formtools.wizard.forms import ManagementForm
from django.core.files.storage import FileSystemStorage
import os
from forms import bandPageForm1, bandPageForm2
from django.forms.models import inlineformset_factory
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory

import logging
logr = logging.getLogger(__name__)


UserFormSet = modelformset_factory(bandMembers,
                                   form=bandPageForm2,
                                   extra=5,
                                   max_num=10,
                                   can_delete=True)

form_list = [
("uc", bandPageForm1),
("u", UserFormSet),
]

TEMPLATES = {"0": "editbandpage_pk.html",
             "1": "editbandpage2_pk.html",}






class createBandPage(SessionWizardView):
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'media'))
    template_name = 'editbandpage_pk.html'
    def get_form(self, step=None, data=None, files=None):
        form = super(createBandPage, self).get_form(step, data, files)

        # Determine the step if not given
        if step is None:
            step = self.steps.current

        if step == '1':
         # Return number of forms for formset requested
         # in previous step.
            userchoice = self.get_cleaned_data_for_step('0')
            num_users = userchoice['memberCount']
            UserFormSet.extra = num_users
            return UserFormSet
        return form



    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        form_data = process_form_data(form_list)
        return render_to_response("bandpage_pk.html" , {'form_data':form_data})

def process_form_data(form_list):
    form_data = [form.cleaned_data for form in form_list]
    return form_data
