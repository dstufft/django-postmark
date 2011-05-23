from django.contrib import admin

from postmark.models import EmailMessage

class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ("to", "to_type", "subject", "tag", "status", "submitted_at")
    list_filter = ("status", "tag", "to_type", "submitted_at")
    search_fields = ("message_id", "to", "subject")
    
    readonly_fields = ("message_id", "status", "subject", "tag", "to", "to_type", "sender", "reply_to", "submitted_at", "text_body", "html_body", "headers", "attachments")
    
    fieldsets = (
        (None, {
            "fields": ("message_id", "status", "subject", "tag", "to", "to_type", "sender", "reply_to", "submitted_at")
        }),
        ("Text Body", {
            "fields": ("text_body",),
            "classes": ("collapse", "closed")
        }),
        ("HTML Body", {
            "fields": ("html_body",),
            "classes": ("collapse", "closed")
        }),
        ("Advanced", {
            "fields": ("headers", "attachments"),
            "classes": ("collapse", "closed")
        })
    )

admin.site.register(EmailMessage, EmailMessageAdmin)