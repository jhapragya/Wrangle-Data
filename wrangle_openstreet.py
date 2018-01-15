
# coding: utf-8

# In[1]:


# load libraries
import os
import xml.etree.cElementTree as cET
from collections import defaultdict
import pprint
import re
import codecs
import json
import string
from pymongo import MongoClient


# In[2]:



# set up map file path
filename = "austin_texas.osm" # osm filename
path = "C:\Users\Pragya\Desktop\Udacity\wrangle_openstreet" # directory contain the osm file
austinOSM = os.path.join(path, filename)
# creating a dictionary for correcting street names
mapping = { "Ct": "Court",
            "St": "Street",
            "st": "Street",
            "St.": "Street",
            "St,": "Street",
            "ST": "Street",
            "street": "Street",
            "Street.": "Street",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "ave": "Avenue",
            "Rd.": "Road",   
            "rd.": "Road",
            "Rd": "Road",    
            "Hwy": "Highway",
            "HIghway": "Highway",
            "Pkwy": "Parkway",
            "Pl": "Place",      
            "place": "Place"
            }

# function that corrects incorrect street names
def update_name(name, mapping):    
    for key in mapping:
        if key in name:
            name = string.replace(name,key,mapping[key])
    return names.path.join(path, filename)

# some regular expression 
lower = re.compile(r'^([a-z]|_)*$') 
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)



# In[3]:


def audit_street_type(street_types, street_name):
    # add unexpected street name to a list
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
            
def is_street_name(elem):
    # determine whether a element is a street name
    return (elem.attrib['k'] == "addr:street")

def audit_street(osmfile):
    # iter through all street name tag under node or way and audit the street name value
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in cET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    return street_types

st_types = audit_street(austinOSM)
# print out unexpected street names
pprint.pprint(dict(st_types))


# In[12]:


# creating a dictionary for correcting street names
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Bend", "Chase", "Circle", "Cove", "Crossing", "Hill",
            "Hollow", "Loop", "Park", "Pass", "Overlook", "Path", "Plaza", "Point", "Ridge", "Row",
            "Run", "Terrace", "Walk", "Way", "Trace", "View", "Vista"]

mapping= { "St": "Street",
            "St.": "Street",
            "Aceneu": "Avenue",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "Blvd": "Boulevard",
            "Blvd.": "Boulevard",
            "Bouevard": "Boulevard",
            "Cir": "Circle",
            "Ct": "Court",
            "Dr": "Drive",
            "Dr.": "Drive",
            "HWY": "Highway",
          "Hwy": "Highway",
            "Ln": "Lane",
            "Pkwy": "Parkway",
            "Pl": "Plaza",
            "RD": "Road",
            "Rd": "Road",
            "Rd.": "Road",
            "Tr": "Trace",
            "Ter": "Terrace",
            "avenue": "Avenue",
            "blvd": "Boulevard",
            "road": "Road",
            "street": "Street",
            "court": "Court",
            "cove": "Cove",
            "lane": "Lane",
            "pass": "Pass"
            }           

# function that corrects incorrect street names
def update_name(name, mapping):    
    for key in mapping:
        if key in name:
            name = string.replace(name,key,mapping[key])
    return name



for street_type, ways in st_types.iteritems():
    for name in ways:
        better_name = update_name(name, mapping)
        print (name, "=>", better_name)


# In[13]:


def audit_zipcodes(osmfile):
    # iter through all zip codes, collect all the zip codes that does not start with 78
    osm_file = open(osmfile, "r")
    zip_codes = {}
    for event, elem in cET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if tag.attrib['k'] == "addr:postcode" and not tag.attrib['v'].startswith('78'):
                    if tag.attrib['v'] not in zip_codes:
                        zip_codes[tag.attrib['v']] = 1
                    else:
                        zip_codes[tag.attrib['v']] += 1
    return zip_codes

zipcodes = audit_zipcodes(austinOSM)
for zipcode in zipcodes:
    print zipcode, zipcodes[zipcode]


# In[4]:


CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

def shape_element(element):
    node = {}
    node["created"]={}
    node["address"]={}
    node["pos"]=[]
    refs=[]
    
    # we only process the node and way tags
    if element.tag == "node" or element.tag == "way" :
        if "id" in element.attrib:
            node["id"]=element.attrib["id"]
        node["type"]=element.tag

        if "visible" in element.attrib.keys():
            node["visible"]=element.attrib["visible"]
      
        # the key-value pairs with attributes in the CREATED list are added under key "created"
        for elem in CREATED:
            if elem in element.attrib:
                node["created"][elem]=element.attrib[elem]
                
        # attributes for latitude and longitude are added to a "pos" array
        # include latitude value        
        if "lat" in element.attrib:
            node["pos"].append(float(element.attrib["lat"]))
        # include longitude value    
        if "lon" in element.attrib:
            node["pos"].append(float(element.attrib["lon"]))

        
        for tag in element.iter("tag"):
            if not(problemchars.search(tag.attrib['k'])):
                if tag.attrib['k'] == "addr:housenumber":
                    node["address"]["housenumber"]=tag.attrib['v']
                    
                if tag.attrib['k'] == "addr:postcode":
                    node["address"]["postcode"]=tag.attrib['v']
                
                # handling the street attribute, update incorrect names using the strategy developed before   
                if tag.attrib['k'] == "addr:street":
                    node["address"]["street"]=tag.attrib['v']
                    node["address"]["street"] = update_name(node["address"]["street"], mapping)

                if tag.attrib['k'].find("addr")==-1:
                    node[tag.attrib['k']]=tag.attrib['v']
                    
        for nd in element.iter("nd"):
             refs.append(nd.attrib["ref"])
                
        if node["address"] =={}:
            node.pop("address", None)

        if refs != []:
           node["node_refs"]=refs
            
        return node
    else:
        return None

# process the xml openstreetmap file, write a json out file and return a list of dictionaries
def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in cET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


# In[7]:


# process the file
data = process_map(austinOSM, True)


# In[9]:


client = MongoClient()
db = client.AustinOSM
collection = db.austinMAP
collection.insert(data)


# In[5]:


os.path.getsize(austinOSM)/1024/1024


# In[6]:


os.path.getsize(os.path.join(path, "austin_texas.osm.json"))/1024/1024


# In[9]:


collection.find().count()


# In[10]:


# Number of unique users
len(collection.group(["created.uid"], {}, {"count":0}, "function(o, p){p.count++}"))


# In[11]:


# Number of nodes
collection.find({"type":"node"}).count()


# In[12]:


# Number of ways
collection.find({"type":"way"}).count()


# In[14]:


#The Number of Methods Used to Create Data Entry
pipeline = [{"$group":{"_id": "$created_by",
                       "count": {"$sum": 1}}}]
result = collection.aggregate(pipeline)
print(len(list(result)))


# In[15]:


#Top three users with most contributions
pipeline = [{"$group":{"_id": "$created.user",
                       "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 3}]
result = collection.aggregate(pipeline)
for doc in result:
    print(doc)


# In[16]:


#Proportion of the top user contributions
pipeline = [{"$group":{"_id": "$created.user",
                       "count": {"$sum": 1}}},
            {"$project": {"proportion": {"$divide" :["$count",collection.find().count()]}}},
            {"$sort": {"proportion": -1}},
            {"$limit": 3}]
result = collection.aggregate(pipeline)
for doc in result:
    print(doc)


# In[17]:


# Most popular cuisines
pipeline = [{"$match":{"amenity":{"$exists":1}, "amenity":"restaurant", "cuisine":{"$exists":1}}}, 
            {"$group":{"_id":"$cuisine", "count":{"$sum":1}}},        
            {"$sort":{"count":-1}}, 
            {"$limit":10}]
result = collection.aggregate(pipeline)
for doc in result:
    print(doc)


# In[24]:


#Universities
pipeline = [{"$match":{"amenity":{"$exists":1}, "amenity": "university", "name":{"$exists":1}}},
            {"$group":{"_id":"$name", "count":{"$sum":1}}},
            {"$sort":{"count":-1}}]
result = collection.aggregate(pipeline)
for doc in result:
    print(doc)


# In[26]:


client = MongoClient()
db = client.AustinOSM
collection = db.austinMAP

pipeline = [{"$match":{"amenity":{"$exists":1}, "amenity": "place_of_worship", "name":{"$exists":1}}},
    {"$group":{"_id": "$religion",
                       "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}]
result = collection.aggregate(pipeline)
for doc in result:
    print(doc)
    
    
    


# In[27]:


pipeline = [{"$match":{"amenity":{"$exists":1}, "name":{"$exists":1}}},
    {"$group":{"_id": "$amenity",
                       "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}]
result = collection.aggregate(pipeline)
for doc in result:
    print(doc)
    
    
    


# In[28]:


pipeline = [{"$match":{"building":{"$exists":1}, "name":{"$exists":1}}},
    {"$group":{"_id": "$building",
                       "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}]
result = collection.aggregate(pipeline)
for doc in result:
    print(doc)
    
    
    


# In[29]:


pipeline = [{"$match":{"amenity":{"$exists":1}, "amenity":"restaurant", "name":{"$exists":1}}}, 
            {"$group":{"_id":"$name", "count":{"$sum":1}}},        
            {"$sort":{"count":-1}}, 
            {"$limit":10}]
result = collection.aggregate(pipeline)
for doc in result:
    print(doc)


# In[40]:


pipeline = [{"$match":{"amenity":{"$exists":1}, "amenity":"fast_food", "name":{"$exists":1}}}, 
            {"$group":{"_id":"$name", "count":{"$sum":1}}},        
            {"$sort":{"count":-1}}, 
            {"$limit":10}]
result = collection.aggregate(pipeline)
for doc in result:
    print(doc)

