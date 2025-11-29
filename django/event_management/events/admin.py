from django.contrib import admin
from .models import *

admin.site.register(UserRole)
admin.site.register(UserRoleMapping)
admin.site.register(Event)
admin.site.register(EventDate)
admin.site.register(Agenda)
admin.site.register(EventRegistration)
admin.site.register(EventImage)