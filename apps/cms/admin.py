from django.contrib import admin
from apps.cms.models import CMS, FAQ, Page
from unfold.admin import ModelAdmin

# Register your models here.
@admin.register(Page)
class CustomAdminClass(ModelAdmin):
    list_display = ('id', 'title','content')
    list_display_links = ('id', 'title','content')

    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'type', 'status')
        }),
    )

@admin.register(CMS)
class CMSAdmin(ModelAdmin):
    pass

@admin.register(FAQ)
class FAQAdmin(ModelAdmin):
    list_display = ('id', 'question', 'status')
    list_display_links = ('id', 'question')

    fieldsets = (
        (None, {
            'fields': ('question', 'answer', 'status')
        }),
    )