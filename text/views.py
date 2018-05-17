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
def evolve(request, pop):
    if request.method == 'POST':
        print (request.POST)
        if 'selection_list' in request.POST:
            update_fitness(request.POST['selection_list'])

    # Get sample from the population
    sample = evospacetext.get_sample(pop, 3)
    # Get the population's template
    template = evospacetext.get_template(pop)
    content_list = get_content_list(sample, template)
    context = {'content_list':content_list, 'sample': json.dumps(sample), 'population':pop}
    print(context)
    return render(request, 'evolve.html', context)

@require_http_methods(["GET"])
def dashboard(request, pop):
    sample = evospacetext.get_all_info_list(pop)
    context = {'content_list': sample, 'population': pop}
    return render(request, 'dashboard.html', context)

@require_http_methods(["GET"])
def details(request, individual):

    template = evospacetext.get_template(individual.split(':')[0])

    ind = evospacetext.get_individual(individual)
    content = get_content(ind, template)
    likes = evospacetext.get_likes(individual)
    views = evospacetext.get_views(individual)
    chromosome = ", ".join( list(map(str, ind["chromosome"])))


    context = {'content': content, 'template':template, 'likes':likes, 'views':views, 'ind':ind, 'chromosome':"["+chromosome+"]"}
    if 'parent1' in ind:
        p1 = evospacetext.get_individual(ind['parent1'])
        context['parent1'] = get_content(p1, template)
    if 'parent2' in ind:
        p2 = evospacetext.get_individual(ind['parent2'])
        context['parent2'] = get_content(p2, template)
    return render(request, 'content.html', context)




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

