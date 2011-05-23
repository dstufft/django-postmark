from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from datetime import datetime
from pytz import timezone
import pytz

from postmark.models import EmailMessage, EmailBounce

try:
    import json                     
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise Exception('Cannot use django-postmark without Python 2.6 or greater, or Python 2.4 or 2.5 and the "simplejson" library')

POSTMARK_DATETIME_STRING = "%Y-%m-%dT%H:%M:%S.%f"

@csrf_exempt
def bounce(request):
    """
    Accepts Incoming Bounces from Postmark. Example JSON Message:
    
        {
            "ID": 42,
            "Type": "HardBounce",
            "Name": "Hard bounce",
            "Tag": "Test",
            "MessageID": null,
            "Description": "Test bounce description",
            "TypeCode": 1,
            "Details": "Test bounce details",
            "Email": "john@example.com",
            "BouncedAt": "2011-05-23T11:16:00.3018994+01:00",
            "DumpAvailable": true,
            "Inactive": true,
            "CanActivate": true,
            "Content": null,
            "Subject": null
        }
    """
    if request.method in ["POST"]:
        bounce_dict = json.loads(request.read())
            
        timestamp, tz = bounce_dict["BouncedAt"].rsplit("+", 1)
        tz_offset = int(tz.split(":", 1)[0])
        tz = timezone("Etc/GMT%s%d" % ("+" if tz_offset >= 0 else "-", tz_offset))
        bounced_at = tz.localize(datetime.strptime(timestamp[:26], POSTMARK_DATETIME_STRING)).astimezone(pytz.utc)
            
        em = get_object_or_404(EmailMessage, message_id=bounce_dict["MessageID"], to=bounce_dict["Email"])
        eb, created = EmailBounce.objects.get_or_create(
            id=bounce_dict["ID"],
            default={
                "message": em,
                "type": bounce_dict["Type"],
                "description": bounce_dict["Description"],
                "details": bounce_dict["Details"],
                "inactive": bounce_dict["Inactive"],
                "can_activate": bounce_dict["CanActivate"],
                "bounced_at": bounced_at,
            }
        )
        
        return HttpResponse(json.dumps({"status": "ok"}))
    else:
        return HttpResponseNotAllowed(['POST'])
