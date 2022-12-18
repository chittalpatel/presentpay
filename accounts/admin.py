from django.contrib import admin

from accounts.models import User, Company


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    pass
