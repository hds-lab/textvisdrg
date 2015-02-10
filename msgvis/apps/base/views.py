from django.views import generic


class HomeView(generic.TemplateView):
    """The homepage view for the website."""

    template_name = 'home.html'


class ExplorerView(generic.TemplateView):
    """The view for the visualization tool."""

    template_name = 'explorer.html'
