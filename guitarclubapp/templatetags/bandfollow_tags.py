from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from decimal import *

from guitarclubapp.models import User, bandFollow

register = template.Library()

@register.filter(name = 'check_follow')
def check_follow( user , args):
    if args is None:
        return False
    arg_list= args.split("|")
    follow_band = arg_list[0]
    user_followee = arg_list[1]

    try:
        follow = bandFollow.objects.filter(user_id = user_followee , band_id= follow_band)
    except ObjectDoesNotExist:
        follow = None

        if follow is None:
            template = """<form method="post" action="/follow/"""+str(follow_band)+"""/">
                                <button type="submit" class="add_friend fontawesome-plus scnd-font-color">Follow</button>
                        """
            return ( template )



    "Following"
    return( """<form method="post" action="/unfollow/"""+str(follow_band)+"""/">
                        <button type="submit" >Following</button>
            """)

register.simple_tag(check_follow)