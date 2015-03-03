from django.db import models
# Create your models here.
import datetime

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django import forms

#import signals


class Choices(models.Model):
    description=models.CharField(max_length=100)


class UserProfile(models.Model):
    genderChoice = ( ('M','Male') , ('F','Female')) # adding choicefield for gender

    user = models.OneToOneField(User)
    activation_key = models.CharField(max_length=40, blank=True)
    key_expires = models.DateTimeField(default=datetime.date.today())
    profilePic = models.FileField(upload_to='media/profile/',default='media/profile/banners-analysis-sketch.jpg',null=True)
    dob = models.DateField(blank=True, null = True)
    gender=models.CharField(max_length=10,choices=genderChoice)
    homeTown=models.CharField(max_length=50,blank=True)
    currentPlace=models.CharField(max_length=50,blank=True)

#    interests = models.CharField(max_length=256,blank=True)
#    genreLikes=models.CharField(max_length=256,blank=True)

    lastUpdated=models.DateField(auto_now=True)


    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural=u'User profiles'

User.profile=property(lambda u:UserProfile.objects.get_or_create(user=u)[0])

class userFollowActivity(models.Model):
    user=models.ForeignKey(User)
    bandFollows = models.CharField(default = "None", blank=True,max_length=256)
    bandLikes = models.CharField(default = "None" , blank=True,max_length=256)

User.follow=property(lambda u:userFollowActivity.objects.get_or_create(user=u)[0])


class multiChoice(models.Model):
    user=models.ForeignKey(User)
    Options = (
                ("AUT", "Australia"),
                ("DEU", "Germany"),
                ("NLD", "Neitherlands")
                )
    Countries = models.ManyToManyField(Choices,choices=Options)

User.multiChoice=property(lambda u:multiChoice.objects.get_or_create(user=u)[0])



###############################################Friends#################################################
from django.db import models
from django.conf import settings
from django.db.models import Q
from django.core.cache import cache
from django.core.exceptions import ValidationError

#from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from exception import AlreadyExistsError
from signals import friendship_request_created, \
    friendship_request_rejected, friendship_request_canceled, \
    friendship_request_viewed, friendship_request_accepted, \
    friendship_removed, follower_created, following_created, follower_removed,\
    following_removed

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

CACHE_TYPES = {
    'friends': 'f-%d',
    'followers': 'fo-%d',
    'following': 'fl-%d',
    'requests': 'fr-%d',
    'sent_requests': 'sfr-%d',
    'unread_requests': 'fru-%d',
    'unread_request_count': 'fruc-%d',
    'read_requests': 'frr-%d',
    'rejected_requests': 'frj-%d',
    'unrejected_requests': 'frur-%d',
    'unrejected_request_count': 'frurc-%d',
}

BUST_CACHES = {
    'friends': ['friends'],
    'followers': ['followers'],
    'following': ['following'],
    'requests': [
        'requests',
        'unread_requests',
        'unread_request_count',
        'read_requests',
        'rejected_requests',
        'unrejected_requests',
        'unrejected_request_count',
    ],
    'sent_requests': ['sent_requests'],
}


def cache_key(type, user_pk):
    """
    Build the cache key for a particular type of cached value
    """
    return CACHE_TYPES[type] % user_pk


def bust_cache(type, user_pk):
    """
    Bust our cache for a given type, can busfriendship_requests_sentt multiple caches
    """
    bust_keys = BUST_CACHES[type]
    keys = [CACHE_TYPES[k] % user_pk for k in bust_keys]
    cache.delete_many(keys)


class FriendshipRequest(models.Model):
    """ Model to represent friendship requests """
    from_user = models.ForeignKey(AUTH_USER_MODEL, related_name='')
    to_user = models.ForeignKey(AUTH_USER_MODEL, related_name='friendship_requests_received')

    message = models.TextField(_('Message'), blank=True)

    created = models.DateTimeField(default=datetime.datetime.now())
    rejected = models.DateTimeField(blank=True, null=True)


    class Meta:
        verbose_name = _('Friendship Request')
        verbose_name_plural = _('Friendship Requests')
        unique_together = ('from_user', 'to_user')

    def __unicode__(self):
        return "User #%d friendship requested #%d" % (self.from_user_id, self.to_user_id)

    def accept(self):
        """ Accept this friendship request """
        relation1 = Friend.objects.create(
            from_user=self.from_user,
            to_user=self.to_user,
            notify = 1
        )

        relation2 = Friend.objects.create(
            from_user=self.to_user,
            to_user=self.from_user,
            notify = 0
        )

        friendship_request_accepted.send(
            sender=self,
            from_user=self.from_user,
            to_user=self.to_user
        )

        self.delete()

        # Delete any reverse requests
        FriendshipRequest.objects.filter(
            from_user=self.to_user,
            to_user=self.from_user
        ).delete()

        # Bust requests cache - request is deleted
        bust_cache('requests', self.to_user.pk)
        bust_cache('sent_requests', self.from_user.pk)
        # Bust reverse requests cache - reverse request might be deleted
        bust_cache('requests', self.from_user.pk)
        bust_cache('sent_requests', self.to_user.pk)
        # Bust friends cache - new friends added
        bust_cache('friends', self.to_user.pk)
        bust_cache('friends', self.from_user.pk)

        return True

    def reject(self):
        """ reject this friendship request """
        self.rejected = datetime.datetime.now()
        self.save()
        friendship_request_rejected.send(sender=self)
        bust_cache('requests', self.to_user.pk)

    def cancel(self):
        """ cancel this friendship request """
        self.delete()
        friendship_request_canceled.send(sender=self)
        bust_cache('requests', self.to_user.pk)
        bust_cache('sent_requests', self.from_user.pk)
        return True

    def mark_viewed(self):
        self.viewed = datetime.datetime.now()
        friendship_request_viewed.send(sender=self)
        self.save()
        bust_cache('requests', self.to_user.pk)
        return True


class FriendshipManager(models.Manager):
    """ Friendship manager """

    def friends(self, user):
        """ Return a list of all friends """
        key = cache_key('friends', user.pk)
        friends = cache.get(key)

        if friends is None:
            qs = Friend.objects.select_related('from_user', 'to_user').filter(to_user=user).all()
            friends = [u.from_user for u in qs]
            cache.set(key, friends)
        #irritating cache override
        qs = Friend.objects.select_related('from_user', 'to_user').filter(to_user=user).all()
        friends = [u.from_user for u in qs]
        cache.set(key, friends)

        return friends

    def requests(self, user):
        """ Return a list of friendship requests """
        key = cache_key('requests', user.pk)
        user_rqst = cache.get(key)

        if user_rqst is None:
            qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(to_user=user , rejected=None).all()
            user_rqst = [ u.from_user for u in qs]

            requests = list(qs)
            cache.set(key, user_rqst)

        return user_rqst

    def sent_requests(self, user):
        """ Return a list of friendship requests from user """
        key = cache_key('sent_requests', user.pk)
        requests = cache.get(key)

        if requests is None:
            qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
                from_user=user).all()
            requests = list(qs)
            cache.set(key, requests)

        return requests

    def unread_requests(self, user):
        """ Return a list of unread friendship requests """
        key = cache_key('unread_requests', user.pk)
        unread_requests = cache.get(key)

        if unread_requests is None:
            qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
                to_user=user,
                viewed__isnull=True).all()
            unread_requests = list(qs)
            cache.set(key, unread_requests)

        return unread_requests

    def unread_request_count(self, user):
        """ Return a count of unread friendship requests """
        key = cache_key('unread_request_count', user.pk)
        count = cache.get(key)

        if count is None:
            count = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
                to_user=user,
                viewed__isnull=True).count()
            cache.set(key, count)

        return count

    def read_requests(self, user):
        """ Return a list of read friendship requests """
        key = cache_key('read_requests', user.pk)
        read_requests = cache.get(key)

        if read_requests is None:
            qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
                to_user=user,
                viewed__isnull=False).all()
            read_requests = list(qs)
            cache.set(key, read_requests)

        return read_requests

    def rejected_requests(self, user):
        """ Return a list of rejected friendship requests """
        key = cache_key('rejected_requests', user.pk)
        rejected_requests = cache.get(key)

        if rejected_requests is None:
            qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
                to_user=user,
                rejected__isnull=False).all()
            rejected_requests = list(qs)
            cache.set(key, rejected_requests)

        return rejected_requests

    def unrejected_requests(self, user):
        """ All requests that haven't been rejected """
        key = cache_key('unrejected_requests', user.pk)
        unrejected_requests = cache.get(key)

        if unrejected_requests is None:
            qs = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
                to_user=user,
                rejected__isnull=True).all()
            unrejected_requests = list(qs)
            cache.set(key, unrejected_requests)

        return unrejected_requests

    def unrejected_request_count(self, user):
        """ Return a count of unrejected friendship requests """
        key = cache_key('unrejected_request_count', user.pk)
        count = cache.get(key)

        if count is None:
            count = FriendshipRequest.objects.select_related('from_user', 'to_user').filter(
                to_user=user,
                rejected__isnull=True).count()
            cache.set(key, count)

        return count

    def add_friend(self, from_user, to_user, message=None):
        """ Create a friendship request """
        if from_user == to_user:
            raise ValidationError("Users cannot be friends with themselves")

        if message is None:
            message = ''

        request, created = FriendshipRequest.objects.get_or_create(
            from_user=from_user,
            to_user=to_user,
            message=message,
        )

        if created is False:
            raise AlreadyExistsError("Friendship already requested")

        bust_cache('requests', to_user.pk)
        bust_cache('sent_requests', from_user.pk)
        friendship_request_created.send(sender=request)

        return request

    def remove_friend(self, to_user, from_user):
        """ Destroy a friendship relationship """
        try:
            qs = Friend.objects.filter(
                Q(to_user=to_user, from_user=from_user) |
                Q(to_user=from_user, from_user=to_user)
            ).distinct().all()

            if qs:
                friendship_removed.send(
                    sender=qs[0],
                    from_user=from_user,
                    to_user=to_user
                )
                qs.delete()
                bust_cache('friends', to_user.pk)
                bust_cache('friends', from_user.pk)
                return True
            else:
                return False
        except Friend.DoesNotExist:
            return False

    def are_friends(self, user1, user2):
        """ Are these two users friends? """
        friends1 = cache.get(cache_key('friends', user1.pk))
        friends2 = cache.get(cache_key('friends', user2.pk))
        if friends1 and user2 in friends1:
            return True
        elif friends2 and user1 in friends2:
            return True
        else:
            try:
                Friend.objects.get(to_user=user1, from_user=user2)
                return True
            except Friend.DoesNotExist:
                return False


class Friend(models.Model):
    """ Model to represent Friendships """
    to_user = models.ForeignKey(AUTH_USER_MODEL, related_name='friends')
    from_user = models.ForeignKey(AUTH_USER_MODEL, related_name='_unused_friend_relation')
    created = models.DateTimeField(default=datetime.datetime.now())
    notify = models.IntegerField(blank= True, null = True)

    objects = FriendshipManager()

    class Meta:
        verbose_name = _('Friend')
        verbose_name_plural = _('Friends')
        unique_together = ('from_user', 'to_user')

    def __unicode__(self):
        return "User #%d is friends with #%d" % (self.to_user_id, self.from_user_id)

    def save(self, *args, **kwargs):
        # Ensure users can't be friends with themselves
        if self.to_user == self.from_user:
            raise ValidationError("Users cannot be friends with themselves.")
        super(Friend, self).save(*args, **kwargs)


class FollowingManager(models.Manager):
    """ Following manager """

    def followers(self, user):
        """ Return a list of all followers """
        key = cache_key('followers', user.pk)
        followers = cache.get(key)

        if followers is None:
            qs = Follow.objects.filter(followee=user).all()
            followers = [u.follower for u in qs]
            cache.set(key, followers)

        return followers

    def following(self, user):
        """ Return a list of all users the given user follows """
        key = cache_key('following', user.pk)
        following = cache.get(key)

        if following is None:
            qs = Follow.objects.filter(follower=user).all()
            following = [u.followee for u in qs]
            cache.set(key, following)

        return following

    def add_follower(self, follower, followee):
        """ Create 'follower' follows 'followee' relationship """
        if follower == followee:
            raise ValidationError("Users cannot follow themselves")

        relation, created = Follow.objects.get_or_create(follower=follower, followee=followee)

        if created is False:
            raise AlreadyExistsError("User '%s' already follows '%s'" % (follower, followee))

        follower_created.send(sender=self, follower=follower)
        following_created.send(sender=self, follow=followee)

        bust_cache('followers', followee.pk)
        bust_cache('following', follower.pk)

        return relation

    def remove_follower(self, follower, followee):
        """ Remove 'follower' follows 'followee' relationship """
        try:
            rel = Follow.objects.get(follower=follower, followee=followee)
            follower_removed.send(sender=rel, follower=rel.follower)
            following_removed.send(sender=rel, following=rel.followee)
            rel.delete()
            bust_cache('followers', followee.pk)
            bust_cache('following', follower.pk)
            return True
        except Follow.DoesNotExist:
            return False

    def follows(self, follower, followee):
        """ Does follower follow followee? Smartly uses caches if exists """
        followers = cache.get(cache_key('following', follower.pk))
        following = cache.get(cache_key('followers', followee.pk))

        if followers and followee in followers:
            return True
        elif following and follower in following:
            return True
        else:
            try:
                Follow.objects.get(follower=follower, followee=followee)
                return True
            except Follow.DoesNotExist:
                return False


class Follow(models.Model):
    """ Model to represent Following relationships """
    follower = models.ForeignKey(AUTH_USER_MODEL, related_name='following')
    followee = models.ForeignKey(AUTH_USER_MODEL, related_name='followers')
    created = models.DateTimeField(default=datetime.datetime.now())

    objects = FollowingManager()

    class Meta:
        verbose_name = _('Following Relationship')
        verbose_name_plural = _('Following Relationships')
        unique_together = ('follower', 'followee')

    def __unicode__(self):
        return "User #%d follows #%d" % (self.follower_id, self.followee_id)

    def save(self, *args, **kwargs):
        # Ensure users can't be friends with themselves
        if self.follower == self.followee:
            raise ValidationError("Users cannot follow themselves.")
        super(Follow, self).save(*args, **kwargs)


#####################Notification##########################



############################################################################################



#################Pop-Up for Generes liked

class Generes(models.Model):
    user=models.ForeignKey(User)
    generes = models.TextField(max_length=150, null=False, blank=False,default="Alternative")

User.generes=property(lambda u:Generes.objects.get_or_create(user=u)[0])



############################Band Pages - User Created##########################


#band page revisted - pawan


class bandPage(models.Model):
    bandId = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    bandName = models.CharField(max_length=50, blank=False)
    bandLogo = models.FileField(upload_to='media/band/',default='media/band/banners-analysis-sketch.jpg',null=True)
    bandCover = models.FileField(upload_to='media/band/',default='media/band/banners-analysis-sketch.jpg',null=True)
    doc = models.DateField(blank=True, null = True)
    genres = models.TextField(max_length=150, null=False, blank=False)


    class Meta:
        verbose_name_plural=u'BandPages'


#band page - settings
#[profanity  filter , admins , age filter, who can view ur page(friends, only you, all) ]

class bandSettings(models.Model):
    ageChoice = ( ('13','Above 13') , ('15','Above 15'), ('17','Above 17'), ('18','Above 18'), ('21','Above 21'))
    pageChoice = ( ('0','Only Me') , ('1','Only Friends'), ('2','Anyone'))

    band = models.ForeignKey(bandPage)
    user = models.ForeignKey(User)
    profanity_words = models.TextField( max_length=150, null=True, blank=True)
    age_filter = models.CharField(max_length=10,choices=ageChoice, default = "18")
    wcvp=models.CharField( max_length=10 , choices=pageChoice , default = "2")
    remove = models.IntegerField(default = 0 , blank = False , null = True)


#band members and roles
class bandMembers(models.Model):
    accessChoice = ( ('0','Admin') , ('1','Editor'), ('2','Analyst'), ('3','Moderator'))

    user=models.ForeignKey(User)
    band = models.ForeignKey(bandPage)
    member_username = models.TextField(max_length=150, null=False, blank=False)
    access = models.CharField(max_length=10,choices=accessChoice)
    user_roles = models.TextField(max_length=150, null=False, blank=False)
    other_roles = models.CharField(max_length = 50 , blank = True , null = True)

    def __unicode__(self):
        return self.member_username


#bandpage Audio file upload
class bandAudioFiles(models.Model):
    user = models.ForeignKey(User)
    band=models.ForeignKey(bandPage)
    album = models.CharField(max_length = 100)
    songname = models.CharField(max_length=100)
    description = models.CharField(max_length = 250)
    artists = models.TextField(max_length = 150, null = False , blank = False)
    audiofile = models.FileField(upload_to='media/band/')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

#band page follow
class bandFollow(models.Model):
    user = models.ForeignKey(User)
    band=models.ForeignKey(bandPage)
    followDate = models.DateTimeField(default=datetime.datetime.now())


#test audio upload
class audioupload(models.Model):
    audiofile = models.FileField(upload_to='media/band/', blank=True)