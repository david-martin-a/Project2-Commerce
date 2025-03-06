from django.contrib import admin

from .models import User, Categories, Bids, Listings, Watch, Comments

# Register your models here.

admin.site.register(User)
admin.site.register(Categories)
admin.site.register(Bids)
admin.site.register(Listings)
admin.site.register(Watch)
admin.site.register(Comments)

