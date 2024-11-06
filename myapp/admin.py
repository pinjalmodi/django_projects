from django.contrib import admin
from . models import User,Contact,RegistrationRequest,Notice,Member,Image,PaymentOrder
# Register your models here.
admin.site.register(User)
admin.site.register(Contact)
admin.site.register(RegistrationRequest)
admin.site.register(Notice)
admin.site.register(Member)
admin.site.register(PaymentOrder)
admin.site.register(Image)


