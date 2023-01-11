from django.contrib import admin

from accounts.models import User, Company


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "is_staff", "associated_company")

    def associated_company(self, obj):
        return obj.company.name


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "address_line1", "city")
