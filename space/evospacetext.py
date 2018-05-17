
from random import randint
import os, json
import redis

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = "evotext.settings"
    from evospace import Population, Individual

else:
    from space.evospace import Population, Individual


r = redis.Redis.from_url(os.environ['REDIS_URL'])

def get_individual(key, as_dict=True):
    return Individual(id=key).get(as_dict=as_dict)

def one_like(individual_id, user, timestamp, multiple=True):
    if multiple:
        user = user + ':' + str(timestamp)
    pipe = r.pipeline()
    if pipe.zadd(individual_id+':likes', user, timestamp):
        pipe.incr(individual_id+':views' )
        pipe.execute()
        return True
    else:
        return False


def get_likes(individual_id):
    return r.zcard(individual_id+':likes')


def get_views(individual_id):
    views = r.get(individual_id+':views')
    views = views or 0
    return int(views)


def one_view(individual_id,):
    r.incr( individual_id+':views' )


def get_sample(population, size):
    evospace = Population(population)
    r = evospace.get_sample(size)
    return r


def take_sample(population, size):
    evospace = Population(population)
    r = evospace.take_sample(size)
    return r


def putback_sample(json_data, population):
    sample = None
    evospace = Population(population)
    if not isinstance(json_data, dict):
        sample = json.loads(json_data)
    else:
        sample = {'sample': json_data['sample'], 'sample_id': json_data['sample_id']}

    evospace.putback_sample(sample)



def put_sample(json_data, population):
    sample = {'sample': json_data['sample'], 'sample_id': json_data['sample_id']}
    evospace = Population(population)
    evospace.put_sample(sample)


def get_template(population):
    return {'template': "{{ salutation }}, my name is {{ name }} {{ action }}.",
            'options' : [
                ["Hey you", "Watup", "Hi", "How you doing?"],
                ["Juan", "Paco", "John", "Rick", "Zoe", "Anna"],
                ["I want to meet you", "I live in Mexico", "and I am lonely, can we talk?", "How can help you", "whats yours?"]
                ],

            'titles': ["A title", "Another title", "Yet another title"],
            'images': ["https://s3.amazonaws.com/mariogarcia/images/book-1659717_1280.jpg",
                       "https://s3.amazonaws.com/mariogarcia/images/computer-1209641_960_720.jpg",
                       "https://s3.amazonaws.com/mariogarcia/images/hacker-1569744_640.jpg",
                       "https://s3.amazonaws.com/mariogarcia/images/math-1547018_1280.jpg"
                       ],
            'number_of_styles': 3,
            'names': ['salutation', 'name', 'action']
            }


def get_info_dict(sample):
    info = {}
    for individual in sample['sample']:
        likes = get_likes(individual['id'])
        views = get_views(individual['id'])
        info[individual['id']] = {'likes':likes, 'views': views}
    return info

def get_info_list(sample):
    info = []
    for individual in sample['sample']:
        likes = get_likes(individual['id'])
        views = get_views(individual['id'])
        info.append({'id':individual['id'],'likes':likes, 'views': views})
    return info

def get_all_info_dict(population):
    evospace = Population(population)
    all = evospace.get_all()
    return get_info_dict(all)


def get_all_info_list(population):
    evospace = Population(population)
    all = evospace.get_all()
    return get_info_list(all)


def initialize_population(population_name = 'pop', size = 10, template = None ):
    evospace = Population(population_name)
    #Delete  population
    evospace.initialize()

    # Add 100 Individuals
    # Chromosome  Size determined by template

    # GENE      TYPE
    #   0       number of styles
    #   1       title
    #   2       image
    #   3       option 0
    #   N       option N

    # TODO: Generate individual chromosomes from template

    for i in range(size):
        individual = { 'chromosome':[
            randint(0,2),   # number of styles
            randint(0, 2),  # titles
            randint(0, 3),  # images
            randint(0, 2),  # salutation
            randint(0, 5),  # name
            randint(0, 4),  # action
            ],
            "fitness": {"DefaultContext": 0.0},
            "score": 0,
           "id": None}

        evospace.put_individual(**individual)


def crossover_single_point(parent1, parent2):
    """ Does the crossover migration. """

    size = min(len(parent1), len(parent2))
    cut = randint(0, size) + size % 2
    chromosome1 = parent1['chromosome'][:cut] + parent2['chromosome'][cut:]
    chromosome2 = parent2['chromosome'][:cut] + parent1['chromosome'][cut:]

    child1 = {'id': None, 'fitness': {"DefaultContext": 0.0},
              'score':0,
              'chromosome': chromosome1,
              'parent1': parent1["id"], 'parent2': parent2["id"],
              'crossover': "single_point"}

    child2 = {'id': None,
              'fitness': {"DefaultContext": 0.0},
              'score':0,
              'chromosome': chromosome2,
              'parent1': parent1["id"],
              'parent2': parent2["id"],
              'crossover': "single_point"}

    return [child1, child2]

def calc_fitness(pop):
    for ind in pop["sample"]:
        likes = get_likes(ind['id'])
        views = get_views(ind['id'])
        ind['likes']= likes
        ind['views'] = views
        ind['score'] = likes
        print(ind)



def evolve_Tournament(pop,sample_size=8, mutation_rate=0.5, min_views = 5, tournament_size = 4 ):
    #get two samples from evospace
    _sample = take_sample(pop, sample_size)
    #if None evospace is probably empty, just return
    if not _sample:
        return
    # Tournament must be a pair
    if tournament_size % 2:
        return

    calc_fitness(_sample)
    # They must have a minimum of 5 views to breed

    # At least the tournament_size
    if len([i for i in _sample['sample'] if i['views']>=min_views]) < tournament_size:
        #If not, put back sample unchanged
        putback_sample(_sample, pop)
        return
    print("Good to Go",_sample )

    # sort
    # TODO: A better way to score, for now is only the one with more likes
    _sample['sample'].sort(key=lambda i: i['score'], reverse=True)
    print("Good to Go", _sample['sample'])

    newChilds = []
    for i in range(0,tournament_size//4,2):
        children = crossover_single_point(_sample['sample'][i], _sample['sample'][i+1])
        print(children)
        newChilds.extend(children)


    for i in range(len(newChilds)):
        _sample['sample'].pop()
    _sample['sample'].extend(newChilds)
    print([a['score'] for a in _sample['sample']])

    putback_sample(_sample, pop)









if __name__ == "__main__":
    #initialize_population('pop', 8)
    evolve_Tournament('pop')
    #print(get_all_info('pop3'))
    #one_like("pop:individual:3", "mario", 1234224)
