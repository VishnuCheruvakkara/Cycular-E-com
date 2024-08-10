from django.contrib.auth import get_user_model
from social_core.exceptions import AuthException

User=get_user_model()

def merge_accounts(backend,uid,user=None,*args,**kwargs):
    if user:
        return {'user':user}
    
    email=kwargs['user':user].get('email')
    if email:
        existing_user=User.objects.filter(email=email).first()
        if existing_user:
            social=backend.strategy.storage.user.get_social_auth(backend.name,uid)
            if social:
                if social.user != existing_user:
                    raise AuthException(backend,'This g-mail account is already in use.')
            else:
                backend.strategy.storage.user.create_social_auth(
                    existing_user,uid,backend.name
                )
            return { 'user':existing_user }
    return {}