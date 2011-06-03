from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from signedauth.models import UserKey

import logging
log = logging.getLogger(__name__)

class BmProfileManager(models.Manager):
    def force_for_user(self, user):
        try:
            profile = self.get(user=user)
        except BmProfile.DoesNotExist:
            log.debug('creating profile for %s', user)
            profile = BmProfile(user=user)
            profile.save()
        return profile

class BmProfile(models.Model):
    user = models.ForeignKey(User)
    playaname = models.CharField(max_length=100, default = '', blank=True)
    userkey = models.ForeignKey(UserKey, null=True)\

    objects = BmProfileManager()

    @property
    def name(self):
        if not self.playaname:
            name = self.user.get_full_name()
            if not name:
                name = self.user.username
            return name

        return self.playaname

    def save(self, *args, **kwargs):
        super(BmProfile, self).save()
        if not self.userkey:
            log.debug('creating userkey for %s', self.user.username)
            key = UserKey(label='key')
            key.save()
            self.userkey = key
            self.save()


# maybe monkeypatch user to use BmProfile as its profile without forcing all users to have keys
if settings.AUTH_PROFILE_MODULE == 'bmprofile.BmProfile':
    User.profile = property(lambda u: BmProfile.objects.force_for_user(u))


