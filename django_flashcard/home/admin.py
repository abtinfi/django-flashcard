from django.contrib import admin
from api import models
# Register your models here.

class UserFlashcardAdmin(admin.ModelAdmin):
    search_fields = ['user__username']
    list_filter = ['user__username']

admin.site.register(models.FlashCard)
admin.site.register(models.UserFlashCard, UserFlashcardAdmin)

