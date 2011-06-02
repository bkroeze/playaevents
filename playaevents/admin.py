from django.contrib import admin
from playaevents.models import Year, CircularStreet, TimeStreet, ThemeCamp, ArtInstallation, PlayaEvent
from swingtime.admin import EventNoteInline, OccurrenceInline

class YearAdmin(admin.ModelAdmin):
    list_display = ('year','location')

class TimeStreetAdmin(admin.ModelAdmin):
    list_display = ('name', 'year')
    list_filter = ['year']

class CircularStreetAdmin(admin.ModelAdmin):
    list_display = ('name', 'year','order', 'distance_from_center')
    list_filter = ['year']
    ordering = ('year','order')

class ThemeCampAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'bm_fm_id', 'location_string')
    list_filter = ['year', 'circular_street', 'time_address']
    ordering = ('name',)
    search_fields = ('name','description','bm_fm_id')
    list_per_page = 50

    def queryset(self, request):
        return ThemeCamp.all_objects

class ArtInstallationAdmin(admin.ModelAdmin):
    list_display = ('name','year', 'bm_fm_id', 'location_string', 'artist', 'url', 'contact_email')
    list_filter = ['year']
    search_fields = ('name','description', 'bm_fm_id')
    list_per_page = 50

class PlayaEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'year', 'print_description', 'moderation')
    list_filter = ['year', 'event_type', 'moderation']
    ordering = ['title']
    search_fields = ('title','description', 'print_description')
    inlines = [EventNoteInline, OccurrenceInline]

    actions = ['make_accepted', 'make_rejected', 'make_unmoderated']
    def make_accepted(self, request, queryset):
      rows_updated=queryset.update(moderation='A')
      if rows_updated == 1:
          message_bit = "1 event was"
      else:
          message_bit = "%s events were" % rows_updated
      self.message_user(request, "%s successfully marked as Accepted." % message_bit)
    make_accepted.short_description = "Moderate selected events as accepted"

    def make_rejected(self, request, queryset):
      rows_updated=queryset.update(moderation='R')
      if rows_updated == 1:
          message_bit = "1 event was"
      else:
          message_bit = "%s events were" % rows_updated
      self.message_user(request, "%s successfully marked as Rejected." % message_bit)
    make_rejected.short_description = "Moderate selected events as rejected"

    def make_unmoderated(self, request, queryset):
      rows_updated=queryset.update(moderation='U')
      if rows_updated == 1:
          message_bit = "1 event was"
      else:
          message_bit = "%s events were" % rows_updated
      self.message_user(request, "%s successfully marked as Unmoderated." % message_bit)
    make_unmoderated.short_description = "Moderate selected events as unmoderated"

admin.site.register(Year, YearAdmin)
admin.site.register(CircularStreet, CircularStreetAdmin)
admin.site.register(TimeStreet, TimeStreetAdmin)
admin.site.register(ThemeCamp, ThemeCampAdmin)
admin.site.register(ArtInstallation, ArtInstallationAdmin)
admin.site.register(PlayaEvent, PlayaEventAdmin)
