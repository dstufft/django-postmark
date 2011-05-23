from django.dispatch import receiver
from django.db import models
from itertools import izip_longest
from datetime import datetime
from pytz import timezone
import pytz

from postmark.signals import post_send

POSTMARK_DATETIME_STRING = "%Y-%m-%dT%H:%M:%S.%f"

TO_CHOICES = (
    ("to", "Recipient"),
    ("cc", "Carbon Copy"),
    ("bcc", "Blind Carbon Copy"),
)

BOUNCE_TYPES = (
    ("HardBounce", "Hard Bounce"),
    ("Transient", "Transient"),
    ("Unsubscribe", "Unsubscribe"),
    ("Subscribe", "Subscribe"),
    ("AutoResponder", "AutoResponder"),
    ("AddressChange", "AddressChange"),
    ("DnsError", "DNS Error"),
    ("SpamNotification", "Spam Notification"),
    ("OpenRelayTest", "Open Relay Test"),
    ("Unknown", "Unknown"),
    ("SoftBounce", "Soft Bounce"),
    ("VirusNotification", "Virus Notification"),
    ("ChallengeVerification", "Challenge Verification"),
    ("BadEmailAddress", "Bad Email Address"),
    ("SpamComplaint", "Spam Complaint"),
    ("ManuallyDeactivated", "Manually Deactivated"),
    ("Unconfirmed", "Unconfirmed"),
    ("Blocked", "Blocked"),
)

class EmailMessage(models.Model):
    message_id = models.CharField(max_length=40)
    submitted_at = models.DateTimeField()
    status = models.CharField(max_length=150)
    
    to = models.CharField(max_length=150)
    to_type = models.CharField(max_length=3, choices=TO_CHOICES)
    
    sender = models.CharField(max_length=150)
    reply_to = models.CharField(max_length=150)
    subject = models.CharField(max_length=150)
    tag = models.CharField(max_length=25)
    
    text_body = models.TextField()
    html_body = models.TextField()
    
    headers = models.TextField()
    attachments = models.TextField()
    
    def __unicode__(self):
        return u"%s" % (self.message_id,)

class EmailBounce(models.Model):
    bounce_id = models.PositiveIntegerField()
    message_id = models.ForeignKey(EmailMessage, related_name="bounces")
    
    inactive = models.BooleanField()
    can_activate = models.BooleanField()
    
    type = models.CharField(max_length=100, choices=BOUNCE_TYPES)
    description = models.TextField()
    details = models.TextField()
    
    bounced_at = models.DateTimeField()
    
    def __unicode__(self):
        return u"%s" % (self.bounce_id,)
    
    

@receiver(post_send)
def sent_message(sender, **kwargs):
    msg = kwargs["message"]
    resp = kwargs["response"]
    
    for recipient in (
        list(izip_longest(msg["To"].split(","), [], fillvalue='to')) +
        list(izip_longest(msg.get("Cc", "").split(","), [], fillvalue='cc')) +
        list(izip_longest(msg.get("Bcc", "").split(","), [], fillvalue='bcc'))):
        
        if not recipient[0]:
            continue
        
        timestamp, tz = resp["SubmittedAt"].rsplit("+", 1)
        tz_offset = int(tz.split(":", 1)[0])
        tz = timezone("Etc/GMT%s%d" % ("+" if tz_offset >= 0 else "-", tz_offset))
        submitted_at = tz.localize(datetime.strptime(timestamp[:26], POSTMARK_DATETIME_STRING)).astimezone(pytz.utc)
        
        
        emsg = EmailMessage(
            message_id=resp["MessageID"],
            submitted_at=submitted_at,
            status=resp["Message"],
            to=recipient[0],
            to_type=recipient[1],
            sender=msg["From"],
            reply_to=msg.get("ReplyTo", ""),
            subject=msg["Subject"],
            tag=msg.get("Tag", ""),
            text_body=msg["TextBody"],
            html_body=msg.get("HtmlBody", ""),
            headers=msg.get("Headers", ""),
            attachments=msg.get("Attachments", "")
        )
        emsg.save()