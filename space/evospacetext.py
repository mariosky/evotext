
from random import randint
import os
import redis


from space.space import Population, Individual



r = redis.Redis.from_url(os.environ['REDIS_URL'])


def one_like(individual_id, user, timestamp):
    pipe = r.pipeline()
    if pipe.zadd(individual_id+':likes', user, timestamp):
        pipe.incr(individual_id+':views' )
        pipe.execute()
        return True
    else:
        return False


def one_view(individual_id,):
    r.incr( individual_id+':views' )


def get_sample(population, size):
    evospace = Population(population)
    r = evospace.get_sample(size)
    return r


def put_sample(json_data, population, size):
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



def initialize_population(population_name = 'pop', template = None ):
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

    for i in range(9):
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


if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = "evotext.settings"
    initialize_population()