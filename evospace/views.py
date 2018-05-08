from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse

import json
import requests
import json
import time

# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def initialize(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        for i in range(20):
            ind = {'name': "Mario", 'chromosome': [2, 2, 3, 1, 1, 2, 2, 2], "fitness": {"s": i}, "score": i}
            url = 'http://127.0.0.1:3000/evospace/test_pop/individual'
            r = requests.post(url, data=ind)

        print ("Insert individual with out id", r.text)
        data = json.dumps({"result": "OK", "error": None, "id": 1})
        return HttpResponse(data, content_type='application/javascript')
    else:
        data = json.dumps({"result": "OK", "error": None, "id": 1})
        return HttpResponse(data, content_type='application/javascript')


def sample(request, population, size=3):
    if request.method == 'GET':
        # GET sample of N individuals
        url = 'http://127.0.0.1:3000/evospace/%s/sample/%d' % (population, size)
        r = requests.get(url)
        print("\n\n\nsample", r.text)
        sample = r.json()
        print('sample result', sample['result'])
        print('as JSON', json.dumps(sample['result']))

        return HttpResponse(json.dumps(sample['result']), content_type='application/javascript')

    elif request.method == 'PUT':
        json_data = json.loads(request.body)

        ind = {'sample': json_data['sample'], 'sample_id': json_data['sample_id']}
        print("sample:", ind, json.dumps(ind))
        url = 'http://127.0.0.1:3000/evospace/test_pop/sample'
        r = requests.post(url, json=ind)
        print('POST sample', r.text)

        data = json.dumps({"result": "OK", "error": None, "id": 1})
        return HttpResponse(data, content_type='application/javascript')

