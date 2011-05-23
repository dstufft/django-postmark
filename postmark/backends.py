from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
import httplib2

try:
    import json                     
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise Exception('Cannot use django-postmark without Python 2.6 or greater, or Python 2.4 or 2.5 and the "simplejson" library')

# Settings
POSTMARK_API_KEY = getattr(settings, "POSTMARK_API_KEY", None)
POSTMARK_SSL = getattr(settings, "POSTMARK_SSL", False)
POSTMARK_TEST_MODE = getattr(settings, "POSTMARK_TEST_MODE", False)

POSTMARK_API_URL = ("https" if POSTMARK_SSL else "http") + "://api.postmarkapp.com/email"
POSTMARK_BATCH_API_URL = ("https" if POSTMARK_SSL else "http") + "://api.postmarkapp.com/email/batch"

class PostmarkMessage(dict):
    """
    Creates a Dictionary representation of a Django EmailMessage that is suitable
    for submitting to Postmark's API. An Example Dicitionary would be:
    
        {
            "From" : "sender@example.com",
            "To" : "receiver@example.com",
            "Cc" : "copied@example.com",
            "Bcc": "blank-copied@example.com",
            "Subject" : "Test",
            "Tag" : "Invitation",
            "HtmlBody" : "<b>Hello</b>",
            "TextBody" : "Hello",
            "ReplyTo" : "reply@example.com",
            "Headers" : [{ "Name" : "CUSTOM-HEADER", "Value" : "value" }],
            "Attachments": [
                {
                    "Name": "readme.txt",
                    "Content": "dGVzdCBjb250ZW50",
                    "ContentType": "text/plain"
                },
                {
                    "Name": "report.pdf",
                    "Content": "dGVzdCBjb250ZW50",
                    "ContentType": "application/octet-stream"
                }
            ]
        }
    """
    
    def __init__(self, message, fail_silently=False):
        """
        Takes a Django EmailMessage and parses it into a usable object for
        sending to Postmark.
        """
        try:
            message_dict = {}
            
            message_dict["From"] = message.from_email
            message_dict["Subject"] = message.subject
            message_dict["TextBody"] = message.body
            
            message_dict["To"] = ",".join(message.to)
            
            if len(message.cc):
                message_dict["Cc"] = ",".join(message.cc)
            if len(message.bcc):
                message_dict["Bcc"] = ",".join(message.bcc)
            
            if isinstance(message, EmailMultiAlternatives):
                for alt in message.alternatives:
                    if alt[1] == "text/html":
                        message_dict["HtmlBody"] = alt[0]
            
            if message.extra_headers and isinstance(message.extra_headers, dict):
                if message.extra_headers.has_key("Reply-To"):
                    message_dict["ReplyTo"] = message.extra_headers.pop("Reply-To")
                    
                if message.extra_headers.has_key("Tag"):
                    message_dict["Tag"] = message.extra_headers.pop("Tag")
                    
                if len(message.extra_headers):
                    message_dict["Headers"] = [{"Name": x[0], "Value": x[1]} for x in message.extra_headers.items()]
            
            if message.attachments and isinstance(message.attachments, list):
                if len(message.attachments):
                    message_dict["Attachments"] = message.attachments
            
        except:
            if fail_silently:
                message_dict = {}
            else:
                raise
        
        super(PostmarkMessage, self).__init__(message_dict)

class PostmarkBackend(BaseEmailBackend):
    
    BATCH_SIZE = 500
    
    def __init__(self, api_key=None, api_url=None, api_batch_url=None, **kwargs):
        """
        Initialize the backend.
        """
        super(PostmarkBackend, self).__init__(**kwargs)
        
        self.api_key = api_key or POSTMARK_API_KEY
        self.api_url = api_url or POSTMARK_API_URL
        self.api_batch_url = api_batch_url or POSTMARK_BATCH_API_URL
        
        if self.api_key is None:
            raise ImproperlyConfigured("POSTMARK_API_KEY must be set in Django settings file or passed to backend constructor.")
    
    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        if not email_messages:
            return
        
        postmark_messages = filter(None, [PostmarkMessage(msg, self.fail_silently) for msg in email_messages])
        postmark_responses = []
        
        for batch in [postmark_messages[x:x+self.BATCH_SIZE] for x in range(0, len(postmark_messages), self.BATCH_SIZE)]:
            postmark_responses.extend(self._send(batch))
        
        return len(filter(lambda x: x["ErrorCode"] == 0 and x["HttpStatus"] == 200, postmark_responses))
    
    def _send(self, messages):
        http = httplib2.Http()
        
        responses = []
        for message in messages:
            if POSTMARK_TEST_MODE:
                print 'JSON message is:\n%s' % json.dumps(message)
                responses.append({"ErrorCode": 0, "HttpStatus": 200})
            else:
                print self.api_batch_url
                resp, content = http.request(self.api_batch_url,
                    body=json.dumps(message),
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "X-Postmark-Server-Token": self.api_key,
                    })
        return [{"ErrorCode": 0, "HttpStatus": 200}]