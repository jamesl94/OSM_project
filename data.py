#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import sys

import cerberus

import schema

#Set default encoding to utf8 to handle accented i
reload(sys)
sys.setdefaultencoding('utf8')

OSM_PATH = "medellin_colombia.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""
    """

    The final return value for a "node" element should look something like:

    {'node': {'id': 757860928,
              'user': 'uboot',
              'uid': 26299,
           'version': '2',
              'lat': 41.9747374,
              'lon': -87.6920102,
              'timestamp': '2010-07-22T16:16:51Z',
          'changeset': 5288876},
     'node_tags': [{'id': 757860928,
                    'key': 'amenity',
                    'value': 'fast_food',
                    'type': 'regular'},
                   {'id': 757860928,
                    'key': 'cuisine',
                    'value': 'sausage',
                    'type': 'regular'},
                   {'id': 757860928,
                    'key': 'name',
                    'value': "Shelly's Tasty Freeze",
                    'type': 'regular'}]}

    The final return value for a "way" element should look something like:

    {'way': {'id': 209809850,
             'user': 'chicago-buildings',
             'uid': 674454,
             'version': '1',
             'timestamp': '2013-03-13T15:58:04Z',
             'changeset': 15353317},
     'way_nodes': [{'id': 209809850, 'node_id': 2199822281, 'position': 0},
                   {'id': 209809850, 'node_id': 2199822390, 'position': 1},
                   {'id': 209809850, 'node_id': 2199822392, 'position': 2},
                   {'id': 209809850, 'node_id': 2199822369, 'position': 3},
                   {'id': 209809850, 'node_id': 2199822370, 'position': 4},
                   {'id': 209809850, 'node_id': 2199822284, 'position': 5},
                   {'id': 209809850, 'node_id': 2199822281, 'position': 6}],
     'way_tags': [{'id': 209809850,
                   'key': 'housenumber',
                   'type': 'addr',
                   'value': '1412'},
                  {'id': 209809850,
                   'key': 'street',
                   'type': 'addr',
                   'value': 'West Lexington St.'},
                  {'id': 209809850,
                   'key': 'street:name',
                   'type': 'addr',
                   'value': 'Lexington'},
                  {'id': '209809850',
                   'key': 'street:prefix',
                   'type': 'addr',
                   'value': 'West'},
                  {'id': 209809850,
                   'key': 'street:type',
                   'type': 'addr',
                   'value': 'Street'},
                  {'id': 209809850,
                   'key': 'building',
                   'type': 'regular',
                   'value': 'yes'},
                  {'id': 209809850,
                   'key': 'levels',
                   'type': 'building',
                   'value': '1'},
                  {'id': 209809850,
                   'key': 'building_id',
                   'type': 'chicago',
                   'value': '366409'}]}
    """


    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []

    if element.tag == 'node':
        node_id = element.attrib['id']
        for field in NODE_FIELDS:
            node_attribs[field] = element.attrib[field]
        for tag in element:
            tag_dict = {}
            if tag.tag == 'tag':
                for field in ['id', 'k', 'v']:
                    if field == 'k':
                        attrib = tag.attrib['k']
                        if re.search(PROBLEMCHARS, attrib):
                            pass
                        else:
                            if not re.match(LOWER_COLON, attrib):
                                tag_dict['key'] = attrib
                                tag_dict['type'] = 'regular'
                            else:
                                v_list = attrib.split(':', 1) #Only split first occurnace
                                tag_dict['key'] = v_list[1]
                                tag_dict['type'] = v_list[0]
                    elif field == 'v':
                        attrib = tag.attrib['v']
                        tag_dict['value'] = attrib
                    elif field == 'id':
                        tag_dict['id'] = node_id
                tags.append(tag_dict)
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        nd_index = 0
        way_id = element.attrib['id']
        for field in WAY_FIELDS:
            way_attribs[field] = element.attrib[field]
        for tag in element:
            tag_dict = {}
            if tag.tag == 'tag':
                for field in ['id', 'k', 'v']:
                    if field == 'k':
                        attrib = tag.attrib['k']
                        if re.search(PROBLEMCHARS, attrib):
                            pass
                        else:
                            if not re.match(LOWER_COLON, attrib):
                                tag_dict['key'] = attrib
                                tag_dict['type'] = 'regular'
                            else:
                                v_list = attrib.split(':', 1) #Only split first occurnace
                                tag_dict['key'] = v_list[1]
                                tag_dict['type'] = v_list[0]
                    elif field == 'v':
                        attrib = tag.attrib['v']
                        tag_dict['value'] = attrib
                    elif field == 'id':
                        tag_dict['id'] = way_id
                tags.append(tag_dict)
            elif tag.tag == 'nd':
                nd_dict = {}
                nd_dict['id'] = way_id
                nd_dict['node_id'] = tag.attrib['ref']
                nd_dict['position'] = nd_index
                nd_index += 1
                way_nodes.append(nd_dict)

        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        """Do not write row if 'value' is None"""
        for row in rows:
            try:
                if row['value'] == None:
                    continue
            except:
                pass
            self.writerow(row)

# ================================================== #
#               Cleaning Functions                   #
# ================================================== #
def clean_city(tag):
    city_name = tag['value']
    if city_name.lower().startswith('med'):
        return 'Medellín'
    if city_name.lower().startswith('la ceja'):
        return 'La Ceja del Tambo'
    if city_name.lower().startswith('el carmen'):
        return 'El Carmen de Viboral'
    else:
        return city_name

def clean_postcode(tag):
    postcode = tag['value']
    if postcode.startswith('05') and len(postcode) == 6:
        return postcode
    if postcode.startswith('5') and len(postcode) == 5:
        return postcode
    else:
        return None

def clean_street(tag):
    accepted_street_names = ['Carrera', 'Calle', 'Avenida', 'Circular',\
     'Diagonal', 'Transversal', 'Doble', 'Acceso', 'Salida', \
     'Autopista', 'Glorieta', 'Variante']
    street_name = (tag['value'].split())
    for i, word in enumerate(street_name):
        word = word.title()
        if word in accepted_street_names:
            pass
        elif word.startswith(u'V\xeda'):
            street_name[i] = 'Vía'
        elif word == 'Via': #Original was missing accent on the i
            street_name[i] = 'Vía'
        elif word == 'Cl': #Calle abbreviation
            street_name[i] = 'Calle'
        elif word == 'Cra': #Carrera abbreviation
            street_name[i] = 'Carrera'
        else:
            pass
    return " ".join(street_name)

def clean_element(shaped_element):
    for i, tag in enumerate(shaped_element['node_tags']):
        if tag['key'] == 'postcode':
            shaped_element['node_tags'][i]['value'] = clean_postcode(tag)
        if tag['key'] == 'city':
            shaped_element['node_tags'][i]['value'] = clean_city(tag)
        if tag['type'] == 'addr' and tag['key'] == 'street':
            tag['value'] = clean_street(tag)
        if tag['type'] == 'regular' and tag['key'] == 'amenity':
            tag['value'] = tag['value'].lower()
    return shaped_element

# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
        codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
        codecs.open(WAYS_PATH, 'w') as ways_file, \
        codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
        codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    el = clean_element(el)
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)
