from django.contrib import admin
from bmprofile.models import BmProfile

class BmProfileAdmin(admin.ModelAdmin):
    list_display = ('playaname','api_allowed')
    readonly_fields = ('userkey',)

    actions = ['allow_api', 'disallow_api']

    def allow_api(self, request, queryset):
      rows_updated=queryset.update(api_allowed=True)
      if rows_updated == 1:
          message_bit = "1 profile was"
      else:
          message_bit = "%s profiles were" % rows_updated
      self.message_user(request, "%s successfully marked API Allowed." % message_bit)
    allow_api.short_description = "Allow selected profiles to use the extended API"

    def disallow_api(self, request, queryset):
      rows_updated=queryset.update(api_allowed=False)
      if rows_updated == 1:
          message_bit = "1 profile was"
      else:
          message_bit = "%s profiles were" % rows_updated
      self.message_user(request, "%s successfully marked API Disallowed." % message_bit)
    disallow_api.short_description = "Disallow selected profiles to use the extended API"


admin.site.register(BmProfile, BmProfileAdmin)
