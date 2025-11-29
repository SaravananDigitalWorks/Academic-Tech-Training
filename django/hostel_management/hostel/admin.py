from django.contrib import admin
from .models import HostelBuilding, Room, Student, HostelApplication, Warden

admin.site.register(HostelBuilding)
admin.site.register(Room)
admin.site.register(Student)
admin.site.register(HostelApplication)
admin.site.register(Warden)