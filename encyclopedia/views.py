from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect

from . import util
from markdown2 import Markdown
from random import choice

class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title")
    markdown = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}), label="")

class EditEntryForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.initial_markdown = kwargs.pop('initial_markdown', "")
        super(EditEntryForm, self).__init__(*args, **kwargs)
        self.fields["markdown"] = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":20}), initial=self.initial_markdown, label="")

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    if request.method == "POST":
        return render(request, "encyclopedia/edit.html", {
            "title" : title,
            "form" : EditEntryForm(initial_markdown=util.get_entry(title))
        })
    else:
        if title in util.list_entries():
            markdowner = Markdown()
            return render(request, "encyclopedia/entry.html", {
                "title": title,
                "entry": markdowner.convert(util.get_entry(title))
            })
        else:
            return render(request, "encyclopedia/entryerror.html", {
                "title": title
            })

def edit(request, title):
    if request.method == "POST":
                        
        form = EditEntryForm(request.POST)

        if form.is_valid():

            # Isolate the markdown from the 'cleaned' version of form data
            markdown = form.cleaned_data["markdown"]

            # Add the new title and markdown to our list of entries
            util.save_entry(title, markdown)

            # Redirect user to list of entries
            return HttpResponseRedirect("/wiki/" + title)

        else:

            return render(request, "encyclopedia/new.html", {
                "form" : form
            })

        # Redirect user to list of entries
        return HttpResponseRedirect("/")
    else:
        return render(request, "encyclopedia/edit.html", {
            "title" : title,
            "form" : EditEntryForm(initial_markdown=util.get_entry(title))
        })

def random(request):
    title = choice(util.list_entries())
    return entry(request, title)

def new(request):

    if request.method == "POST":

        form = NewEntryForm(request.POST)

        if form.is_valid():

            # Isolate the title and markdown from the 'cleaned' version of form data
            title = form.cleaned_data["title"]
            markdown = form.cleaned_data["markdown"]

            # Check if the title already exists
            if title in util.list_entries():
                return render(request, "encyclopedia/new.html", {
                    "form" : NewEntryForm()
                })                

            # Add the new title and markdown to our list of entries
            util.save_entry(title, markdown)

            # Redirect user to list of entries
            return HttpResponseRedirect("/")

        else:

            return render(request, "encyclopedia/new.html", {
                "form" : form
            })
    else:

        return render(request, "encyclopedia/new.html", {
            "form" : NewEntryForm()
        })