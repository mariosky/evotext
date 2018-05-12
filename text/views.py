from django.shortcuts import render
import json


# Create your views here.

from django.http import HttpResponse
from django.template import Template, Context
from django.views.decorators.http import require_http_methods
from space import evospacetext

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


@require_http_methods(["GET", "POST"])
def evolve(request):
    if request.method == 'POST':
        print (request.POST)
        if 'selection_list' in request.POST:
            update_fitness(request.POST['selection_list'])

    # Get sample from the population
    # TODO: Multiple populations
    sample = evospacetext.get_sample('pop', 3)
    # Get the population's template
    template = evospacetext.get_template('pop')
    content_list = get_content_list(sample, template)
    context = {'content_list':content_list, 'sample': json.dumps(sample)}
    print(context)
    return render(request, 'evolve.html', context)


def get_content_list(sample, template):
    return [ get_content(individual, template) for individual in sample['sample']]

def update_fitness(selection_list):
    # selection_list format:
    # [ pop:individual:id:like:timestamp:username,  pop:individual:id,  pop:individual:id]
    # if liked: pop:individual:id:like:timestamp:username
    # if not selected pop:individual:id
    print(selection_list.split(','))
    for individual_list in [item.split(':') for item in selection_list.split(',')]:
        # if selected update like_ordered_set
        print(individual_list)
        if 'like' in individual_list:
            evospacetext.one_like(':'.join(individual_list[:3]), individual_list[5], individual_list[4])
        # if not, increment views
        else:
            evospacetext.one_view(':'.join(individual_list[:3]))

def get_content(individual, template):
    django_template = Template(template['template'])
    type = int(individual['chromosome'][0])
    title = template['titles'][int(individual['chromosome'][1])]
    image = template['images'][int(individual['chromosome'][2])]

    context = Context({"salutation": template['options'][0][int(individual['chromosome'][3])],
                       "name": template['options'][1][int(individual['chromosome'][4])],
                       "action": template['options'][2][int(individual['chromosome'][5])]})
    text = django_template.render(context)

    return {'title': title, 'type': type, 'text': text, 'image': image, 'id': individual['id']}

