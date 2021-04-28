from django.shortcuts import render

from . import util
from markdown2 import Markdown

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    if title in util.list_entries():
        markdowner = Markdown()
        print(markdowner.convert(util.get_entry(title)))
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry": markdowner.convert(util.get_entry(title))
        })
    else:
        return render(request, "encyclopedia/entryerror.html", {
            "title": title
        })
