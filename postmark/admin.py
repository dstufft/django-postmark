from django.contrib import admin

from postmark.models import EmailMessage

class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ("to", "to_type", "subject", "tag", "status", "submitted_at")
    list_filter = ("status", "tag", "to_type", "submitted_at")
    search_fields = ("message_id", "to", "subject")

admin.site.register(EmailMessage, EmailMessageAdmin)