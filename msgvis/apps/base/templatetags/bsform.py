from django import template

register = template.Library()

@register.inclusion_tag('_layouts/form_base.html')
def bsform(form):
	return {'form': form}



