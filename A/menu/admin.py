from django.contrib import admin
from .models import QRMenu, MenuItem


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1



class MenuAdmin(admin.ModelAdmin):
    inlines = [MenuItemInline]
    fields = [
         'user', 'title', 'description', 'qr_code'
    ]



admin.site.register(QRMenu, MenuAdmin)
admin.site.register(MenuItem)
