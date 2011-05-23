from setuptools import setup

setup(
    name = "django-postmark",
    version = __import__("postmark").__version__,
    author = "Donald Stufft",
    author_email = "donald@e.vilgeni.us",
    description = "A Django reusable app to send email with postmark, as well as models and views to handle bounce integration.",
    long_description = open("README").read(),
    url = "http://github.com/dstufft/django-postmark/",
    license = "BSD",
    packages = [
        "postmark",
    ],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Utilities",
        "Framework :: Django",
    ]
)