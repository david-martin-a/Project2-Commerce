from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(Users)
admin.site.register(Categories)
admin.site.register(Bids)
admin.site.register(Listings)
admin.site.register(Watch)
admin.site.register(Comments)

