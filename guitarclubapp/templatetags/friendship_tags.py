from django import template
from django.core.exceptions import ObjectDoesNotExist
from decimal import *

from guitarclubapp.models import User, Friend, FriendshipRequest, Follow

register = template.Library()

@register.inclusion_tag('friendship/templatetags/friends.html')
def friends(user):
    """
    Simple tag to grab all friends
    """
    return {'friends': Friend.objects.friends(user)}

@register.inclusion_tag('friendship/templatetags/followers.html')
def followers(user):
    """
    Simple tag to grab all followers
    """
    return {'followers': Follow.objects.followers(user) }


@register.inclusion_tag('friendship/templatetags/following.html')
def following(user):
    """
    Simple tag to grab all users who follow the given user
    """
    return {'following': Follow.objects.following(user)}


@register.inclusion_tag('friendship/templatetags/friend_requests.html')
@register.filter(name = 'friend_requests')
def friend_requests(user , arg):
    """
    Inclusion tag to display friend requests
    """
    return (Friend.objects.requests(arg))
    #return {'friend_requests':Friend.objects.requests(arg)}


@register.inclusion_tag('friendship/templatetags/friend_request_count.html')
def friend_request_count(user):
    """
    Inclusion tag to display the count of unread friend requests
    """
    return {'friend_request_count': Friend.objects.unread_request_count(user)}



@register.filter(name = 'check_friendship')
def check_friendship( user , args):
    if args is None:
        return False
    arg_list= args.split("|")
    from_user = arg_list[0]
    to_user = arg_list[1]
    #check if they are friends
    if from_user == to_user:
        return ("""<form ><button type="submit" disabled class="add_friend_no_hover">Ha Ha! :) </button>
                        </form><form>""")
    else:
        try:
            frnds = Friend.objects.get(from_user_id = from_user , to_user_id= to_user)
        except ObjectDoesNotExist:
            frnds = None

        if frnds is None:
            try:
                frnd_sent = FriendshipRequest.objects.get(from_user_id = from_user , to_user_id  = to_user)
            except ObjectDoesNotExist:
                frnd_sent = None

            if frnd_sent is None:
                try:
                    frnd_respond = FriendshipRequest.objects.get(to_user_id = from_user , from_user_id  = to_user,rejected__isnull = True)
                except ObjectDoesNotExist:
                    frnd_respond = None

                if frnd_respond is None:
                    try:
                        frnd_decline = FriendshipRequest.objects.get(to_user_id = from_user , from_user_id  = to_user, rejected__isnull = False)
                    except ObjectDoesNotExist:
                        frnd_decline = None

                    if frnd_decline is None:
                        "add friends"
                        user_info= User.objects.get(id = to_user)
                        add_frnd = user_info.username

                        template = """<form method="post" action="/friend/add/"""+str(add_frnd)+"""/">
                                    <button type="submit" class="add_friend fontawesome-plus scnd-font-color">Add as Friend</button>
                                """
                        return ( template )
                    else:
                        "Frnd rqst Declined"
                        return ("""<form><button type="submit" disabled class="add_friend_no_hover">Friend Request Declined</button>
                                </form><form>""")
                else:
                    "Accept or decline friend request"
                    frnd_rqst= User.objects.get(id = to_user)
                    reqst_pk = frnd_rqst.pk
                    template = str("<a href = '/friend/accept/")+str(reqst_pk)+str("'/> Accept </a> &nbsp&nbsp <a href = '/friend/reject/")+str(reqst_pk)+ str("'/> Decline </a>")
                    return (template)
            else:

                "frnd reqst sent"
                #for revoke frnd reqst
                to_user_id = to_user
                template = str("""<a id="revoke" href = "/friend/revoke/""")+str(to_user_id)+"""/"> Revoke Friend Request </a>"""
                return("""<form ><button type="submit" disabled class="add_friend_no_hover" >Friend Request Sent</button>
                            </form>
                            <form>"""+str(template))
        else:
            "Are Frnds"
            return ("""<form ><button type="submit" disabled class="add_friend_no_hover">Are Friends</button>
                            </form><form>""")

@register.filter(name = 'friend_request_notify')
def friend_request_notify(user , from_user):
    # count frnd request
    frnd_reqst_count = FriendshipRequest.objects.filter(to_user_id = from_user ,rejected__isnull = True).count()
    frnd_accpt_count = Friend.objects.values_list('to_user_id', flat=True).filter(from_user_id = from_user , notify = 1).count()
    total_count = frnd_reqst_count + frnd_accpt_count
    return total_count

@register.filter(name = 'friend_accpt_notify')
def friend_accpt_notify(user , from_user):
    accpt_notify = Friend.objects.values_list('to_user_id', flat=True).filter(from_user_id = from_user , notify = 1)
    user_info = User.objects.filter(id__in = accpt_notify)
    return (user_info)

register.simple_tag(check_friendship)
register.simple_tag(friend_requests)
register.simple_tag(friend_request_notify)
register.simple_tag(friend_accpt_notify)
