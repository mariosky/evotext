__author__ = 'mario'


import redis, json, os
from django.conf import settings
os.environ['DJANGO_SETTINGS_MODULE'] = "evotext.settings"

r = redis.Redis.from_url(settings.REDIS_URL)

class Individual:
    def __init__(self, **kwargs):
        ## Se puede inicializar desde un diccionario
        self.id = kwargs['id']
        self.fitness = kwargs.get('fitness',{})
        self.chromosome = kwargs.get('chromosome',[])
        self.__dict__.update(kwargs)

    def put(self, population):
        pipe = r.pipeline()
        if pipe.sadd( population, self.id ):
            pipe.set( self.id , self.__dict__ )
            pipe.execute()
            return True
        else:
            return False

    def get(self, as_dict = False):
            #Se evalua el diccionario almacenado en Redis
            #Esto crea el tipo de dato correspondiente en python
            #normalmente fitness es un diccionario y chromosome una lista
        if r.get(self.id):
            dict = eval(r.get(self.id))
            self.__dict__.update(dict)
        else:
            raise LookupError("Key Not Found")

        if as_dict:
            return self.__dict__
        else:
            return self

    def __repr__(self):
        return self.id +":"+ str(self.fitness) +":" + str( self.chromosome)

    def as_dict(self):
        return self.__dict__


class Population:
    def __init__(self, name = "pop" ):
        self.name = name
        self.sample_counter = self.name+':sample_count'
        self.individual_counter = self.name+':individual_count'
        self.sample_queue = self.name+":sample_queue"
        self.returned_counter = self.name+":returned_count"
        self.log_queue = self.name+":log_queue"
        #Esta es una propiedad del EvoSpaceServer NO de la poblacion
        self.is_active = False

    def deactivate(self):
        self.is_active = False

    def get_returned_counter(self):
        return int( r.get(self.returned_counter))

    def individual_next_key(self):
        key = r.incr(self.individual_counter)
        return self.name+":individual:%s" % key

    def size(self):
        return r.scard(self.name)

    def initialize(self):
        # Delete all keys with pattern
        #r.flushall()

        for key in  r.keys(self.name+':*'):
            r.delete(key)
        r.delete(self.name)
        r.setnx(self.sample_counter,0)
        r.setnx(self.individual_counter,0)
        r.setnx(self.returned_counter,0)

        ##NOOO Aqui
        self.is_active = True

    def take_sample(self, size):
        sample_id = r.incr(self.sample_counter)

        #Get keys
        sample = [r.spop(self.name) for i in range(size)]
        #If there is a None
        if None in sample:
            sample = [s for s in sample if s]
            if not sample:
                return None
        r.sadd(self.name+":sample:%s" % sample_id, *sample)
        r.rpush(self.sample_queue, self.name+":sample:%s" % sample_id)
        try:
            result =  {'sample_id': self.name+":sample:%s" % sample_id ,
                   'sample':   [Individual(id=key).get(as_dict=True) for key in sample ]}
        except:
            return None
        return result

    def get_sample(self, size):
        sample_id = r.incr(self.sample_counter)

        sample = r.srandmember(self.name, size)
        if None in sample:
            sample = [s for s in sample if s]
            if not sample:
                return None
        try:
            result =  {'sample_id': self.name+":sample:%s" % sample_id ,
                   'sample':   [Individual(id=key).get(as_dict=True) for key in sample ]}
        except:
            return None
        return result

    def get_all(self):
        sample = r.smembers(self.name)
        if None in sample:
            sample = [s for s in sample if s]
            if not sample:
                return None
        try:
            result =  {'sample_id': 0 ,
                       'sample':   [Individual(id=key).get(as_dict=True) for key in sample ]}
        except:
            return None
        return result


    def read_sample_queue(self):
        result = r.lrange(self.sample_queue,0,-1)
        return result

    def read_sample_queue_len(self):
        return r.llen(self.sample_queue)


    def read_pop_keys(self):
        sample = r.smembers(self.name)
        sample = list(sample)
        result =  { 'sample': sample }
        return result

    def read_sample(self):
        sample = r.smembers(self.name)
        result =  { 'sample':   [Individual(id=key).get(as_dict=True) for key in sample]}
        return result

    def put_individual(self, **kwargs ):
        if kwargs['id'] is None:
            kwargs['id'] = self.name+":individual:%s" % r.incr(self.individual_counter)
        ind = Individual(**kwargs)
        ind.put(self.name)

    def putback_sample(self,sample, **kwargs ):
        if not isinstance(sample,dict):
            sample = json.loads(sample)
        r.incr(self.returned_counter)
        for member in sample['sample']:
            if member['id'] is None:
                member['id'] = self.name+":individual:%s" % r.incr(self.individual_counter)
            self.put_individual(**member)
        r.delete(sample['sample_id'])
        r.lrem(self.sample_queue,sample['sample_id'])

    def put_sample(self,sample, **kwargs ):
        if not isinstance(sample,dict):
            sample = json.loads(sample)

        for member in sample['sample']:
            if member['id'] is None:
                member['id'] = self.name+":individual:%s" % r.incr(self.individual_counter)
            self.put_individual(**member)
        r.delete(sample['sample_id'])

    def respawn_sample(self, sample):
        if r.exists(sample):
            members = r.smembers(sample)
            r.sadd(self.name, *members)
            r.delete(sample)
            r.lrem(self.sample_queue,sample,1)

    def respawn_ratio(self, ratio = .2):
        until_sample  = int(r.llen(self.sample_queue)*ratio)
        for i in range(until_sample):
            self.respawn_sample( r.lpop(self.sample_queue))


    def respawn(self, n = 1):
        current_size = r.llen(self.sample_queue)
        if n > current_size:
            for i in range(current_size):
                self.respawn_sample( r.lpop(self.sample_queue))
        else:
            for i in range(n):
                self.respawn_sample( r.lpop(self.sample_queue))


if __name__ == "__main__":
    population = Population('pop2')
    population.initialize()

