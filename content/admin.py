from django.contrib import admin

from .models import Document, DocumentCategory, Representative, Tender

admin.site.site_header = "Панель управления IK Backend"
admin.site.site_title = "IK Backend Admin"
admin.site.index_title = "Управление контентом"


@admin.register(Representative)
class RepresentativeAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name_ru", "role_ru", "order", "created_at")
    ordering = ("order", "id")


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title_ru", "created_at")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "title_ru", "category", "created_at")
    list_filter = ("category",)


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = ("id", "title_ru", "amount", "deadline", "is_active")

# Register your models here.
