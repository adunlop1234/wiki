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

def search(request):
    '''
    Allow the user to type a query into the search box in the sidebar to search for an encyclopedia entry.
    If the query matches the name of an encyclopedia entry, the user should be redirected to that entry’s page.
    If the query does not match the name of an encyclopedia entry, the user should instead be taken to a search results page that displays a list of all encyclopedia entries that have the query as a substring. For example, if the search query were Py, then Python should appear in the search results.
    Clicking on any of the entry names on the search results page should take the user to that entry’s page.
    '''
    # Get the query
    query = request.GET.get('q')

    # Check if exact match do .lower() on string to match and if it does then do redirect
    # Would make these sets in reality for speed
    valid_entries = []
    for entry in util.list_entries():
        if query.lower() == entry.lower():
            return HttpResponseRedirect("wiki/" + entry)
        elif query.lower() in entry.lower():
            valid_entries.append(entry)

    # If there is a substring match then return the list of available pages otherwise redirect home
    if valid_entries:
        return render(request, "encyclopedia/search.html", {
            "entries": valid_entries,
            "query": query
        })
    else:
        return render(request, "encyclopedia/searcherror.html", {
            "query": query
        })