import requests
import json
import time


#Delete  population
r = requests.delete('http://127.0.0.1:3000/evospace/pop')
print ("Delete population", r.text)
#{"result":[[null,1],[null,1],[null,1],[null,"OK"]]}


#Create population
r = requests.post('http://127.0.0.1:3000/evospace/pop/initialize', data = {'space':'test_pop'})
print ("Create population", r.text)
#{"result":[[null,1],[null,1],[null,1],[null,"OK"]]}

#Add Individuals
ind = {'id':3, 'name':"Mario", 'chromosome':[1,2,3,1,1,2,2,2],"fitness":{"s":1},"score":1 }
url = 'http://127.0.0.1:3000/evospace/pop/individual'
r = requests.post(url, data=ind)
print ("Insert individual with id", r.text)

# Add 100 Individuals
for i in range(20):
	ind = { 'name':"Mario", 'chromosome':[2,2,3,1,1,2,2,2],"fitness":{"s":i},"score":i }
	url = 'http://127.0.0.1:3000/evospace/pop/individual'
	r = requests.post(url, data=ind)
print ("Insert individual with out id", r.text)


