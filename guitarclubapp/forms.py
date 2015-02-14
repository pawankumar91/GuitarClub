import re
from django import forms
from django.contrib.auth.models import User   # fill in custom user info then save it
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from models import UserProfile
#from album.forms import MyRegistrationForm
from models import userFollowActivity
from models import Choices
from models import multiChoice
from models import Generes
from models import bandPage
from models import bandMembers
from django.forms.formsets import formset_factory

class MyRegistrationForm(UserCreationForm):

    #username = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("Username"), error_messages={ 'invalid': _("This value must contain only letters, numbers and underscores.") })
    first_name = forms.CharField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)),label=_("First Name"))
    last_name=forms.CharField(widget=forms.TextInput(attrs=dict(required=True,max_length=30)),label=_("Last Name"))
    username = forms.EmailField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("Email address"),error_messages={ 'invalid': _("This value must contain only letters, numbers and underscores.") })
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label=_("Password (again)"))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password1', 'password2',)


    def clean_email_id(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_("This email-id already exists. Please try another one."))

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields did not match."))
        return self.cleaned_data

    #modify save() method so that we can set user.is_active to False when we first create our user
    def save(self, commit=True):
        user = super(MyRegistrationForm, self).save()
        user.email = self.cleaned_data['username']

        if commit:
            user.is_active = False # not active until he opens activation link
            user.save()
        return user


#userprofile forms
class UserProfileForm(forms.ModelForm):
    profilePic = forms.ImageField(label=_('profilePic'),required=False, \
                                    error_messages ={'invalid':_("Image files only")},\
                                    widget=forms.FileInput)
    class Meta:
        model=UserProfile
        fields=("profilePic","dob","gender","homeTown","currentPlace")

#userFollowActivity
class userFollowActivityForm(forms.ModelForm):
    class Meta:
        model=userFollowActivity
        fields=("bandLikes" , "bandFollows")

class multiChoiceForm(forms.ModelForm):
    Countries = forms.ModelMultipleChoiceField(queryset=Choices.objects.all(), required=False, widget=forms.CheckboxSelectMultiple)
    class Meta:
        model=multiChoice
        fields=("Countries",)

#PopUp for generes liked

Select_Generes  = (('Alternative','Alternative'),
     ('Bangra','Bangra'),
     ('Classical','Classical'),
     ('Dhrupad','Dhrupad'),)

class formForm(forms.ModelForm):
    generes = forms.MultipleChoiceField(label='Music Stlyes that you like', choices=Select_Generes, widget=forms.CheckboxSelectMultiple)
    class Meta:
        model=Generes
        fields=("generes",)

    def __init__(self, *args, **kwargs):
        super(formForm, self).__init__(*args, **kwargs)
        # assign a (computed, I assume) default value to the choice field
        #generes = Generes.objects.get(user=request.user)
        self.initial['generes'] = 'Alternative'

    def save(self, commit=True):
        genre = super(formForm, self).save()
        genre.generes = u'     '.join(self.cleaned_data['generes'])
        genre.save()


        return genre

########band pages revisited - pawan

class bandPageForm1(forms.ModelForm):
    bandLogo = forms.ImageField(label=_('bandLogo'),required = False, error_messages = {'inavlid':_("Image Files Only")}, widget=forms.FileInput)
    bandCover = forms.ImageField(label=_('bandLogo'),required = False, error_messages = {'inavlid':_("Image Files Only")}, widget=forms.FileInput)
    genres = forms.MultipleChoiceField(label='Music Stlyes that you like', choices=Select_Generes, widget=forms.CheckboxSelectMultiple)
    class Meta:
        model=bandPage
        fields=("bandName","bandLogo","bandCover","doc","memberCount","genres",)
    def save(self, commit=True):
        form = super(bandPageForm1, self).save()
        form.generes = u'     '.join(self.cleaned_data['genres'])
        form.save()
        return form

class bandPageForm2(forms.ModelForm):
    memberUserName = forms.EmailField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("Email address"),error_messages={ 'invalid': _("This value must contain only letters, numbers and underscores.") })

    class Meta:
        model=bandMembers
        fields=("memberUserName","access",)

    def clean_email_id(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['memberUserName'])
            if user:
                return self.cleaned_data['memberUserName']
        except User.DoesNotExist:
            return ("No user found with the mentioned e-mail address")
        raise forms.ValidationError(_("This email-id does not exists"))

class bandPageForm3(forms.Form):
    bandPageForm2Set = formset_factory(bandPageForm2, can_delete=True, extra=5)
