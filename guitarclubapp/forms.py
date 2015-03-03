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
from models import bandSettings
from models import bandAudioFiles
from models import bandFollow
from django.forms.formsets import formset_factory
from django.conf import settings
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField


class LoginForm(forms.Form):
  remember_me = forms.BooleanField(required=False)



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
        raise forms.ValidationError(_("This email-id already exists. Please try another one."),code=error1)

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields did not match."),code=error2)
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
    #dob = forms.DateField(attrs={'class':'datepicker'})

    class Meta:
        model=UserProfile
        widgets = {
            'dob': forms.DateInput(attrs={'class':'datepicker'}),
        }
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

############################################################################################################################
#band pages revisited - pawan

class bandPageForm1(forms.ModelForm):
    bandLogo = forms.ImageField(label=_('Band Logo or DP'),required = False, error_messages = {'inavlid':_("Image Files Only")}, widget=forms.FileInput)
    bandCover = forms.ImageField(label=_('Band Cover Picture '),required = False, error_messages = {'inavlid':_("Image Files Only")}, widget=forms.FileInput)
    genres = forms.MultipleChoiceField(label='Music Stlyes that you like', choices=Select_Generes, widget=forms.CheckboxSelectMultiple)
    class Meta:
        model=bandPage
        fields=("bandName","bandLogo","bandCover","doc","genres",)
        labels = {"doc": _("when was the band formed"),}


    #def save(self, commit=True):
    #    form = super(bandPageForm1, self).save()
    #    form.generes = u'     '.join(self.cleaned_data['genres'])

    #    form.save()
    #    return form

class bandSettingsForm(forms.ModelForm):
    profanity_words = forms.CharField(label='Filter Profane Words',widget=forms.TextInput({ "placeholder": "Block posts or comments containing the following words: Add words to block, seperated by commas" }))

    class Meta:
        model = bandSettings
        fields = ("profanity_words","age_filter","wcvp")
        labels = {"age_filter": _("Age Filter"),"wcvp": _("who can view your page"),}


#add more to the list
user_roles  = (('1','Vocalist'), ('2','Guitarist'), ('3','Pianoist'), ('4','Keyboard'), ('5','Drummer'),('6','Percussionist'),('7','Manager'),('8','DJ'),('9','Base Guitarist'),('10','Violonist'),('11','Others'),)

class bandPageForm2(forms.ModelForm):
    member_username = forms.EmailField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("Email address"),error_messages={ 'invalid': _("This value must contain only letters, numbers and underscores.") })
    user_roles = forms.MultipleChoiceField(label='User Roles', choices=user_roles, widget=forms.SelectMultiple)

    class Meta:
        model=bandMembers
        fields=("member_username","access","user_roles","other_roles",)

    #def save(self, commit = True):
    #    data = self.cleaned_data

    #    form = super(bandPageForm2, self).save(commit = False)
    #    form.user_roles = u'     '.join(self.cleaned_data['user_roles'])
    #    form.user = x
    #    form.band = 41
    #    form.save()
    #    return form

    def clean_email_id(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['member_username'])
            if user:
                return self.cleaned_data['member_username']
        except User.DoesNotExist:
            return ("No user found with the mentioned e-mail address")
        raise forms.ValidationError(_("This email-id does not exists"))



import os
class bandAudioFilesForm(forms.ModelForm):
    artists = forms.ModelMultipleChoiceField(queryset = None,widget=forms.CheckboxSelectMultiple)
    audiofile = forms.FileField( label = _(u"Audio File" ))
     # Add some custom validation to our file field

    def __init__(self , *args, **kwargs):
        #band = kwargs.pop('band_pk',None)
        super(bandAudioFilesForm, self).__init__(*args, **kwargs)
        #self.fields['artists'].widget = forms.SelectMultiple()
        #bandmembers = bandMembers.objects.values_list('member_username', flat = True).filter(band_id= 41)
        #memberNames = User.objects.values_list('first_name', flat = True).filter(username__in = bandmembers)
        self.fields['artists'].queryset = bandMembers.objects.filter(band_id= 41)


    class Meta:
        model=bandAudioFiles
        fields=("album","songname","description","audiofile","artists",)


    def clean_audio_file(self):
        file = self.cleaned_data.get('audiofile',False)
        if file:
            if file._size > 4*1024*1024:
                raise ValidationError("Audio file too large ( > 4mb )")
            if not file.content-type in ["audio/mpeg","audio/x-wav"]:
                raise ValidationError("Content-Type is not mpeg or wave")
            if not os.path.splitext(file.name)[1] in [".mp3",".wav"]:
                raise ValidationError("Doesn't have proper extension")
            # Here we need to now to read the file and see if it's actually
            # a valid audio file. I don't know what the best library is to
            # to do this
            if not some_lib.is_audio(file.content):
                raise ValidationError("Not a valid audio file")
                return file
        else:
            raise ValidationError("Couldn't read uploaded file")


#band follow

##############################################################################################################################

class bandPageForm3(forms.Form):
    bandPageForm2Set = formset_factory(bandPageForm2, can_delete=True, extra=5)


#test
from models import audioupload

class audiouploadForm(forms.ModelForm):
    audiofile = forms.FileField()
    class Meta:
        model = audioupload
        fields = ('audiofile',)