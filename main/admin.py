from django.contrib import admin

from .models import *

class NoteAdmin(admin.ModelAdmin):
    model = Note
    list_display = ('session', 'text', 'created_on', 'updated_on')
    readonly_fields = ('session', 'created_on', 'updated_on')
    fields = ('session', 'text', 'created_on', 'updated_on')

admin.site.register(Note, NoteAdmin)
