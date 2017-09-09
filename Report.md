
# Wrangle Open Street Maps Data


### Introduction

This project start with Open Street Map data downloaded <a href="https://mapzen.com/data/metro-extracts/metro/medellin_colombia/">here</a> for Medellín, Colombia. Elements of the raw XML file were audited, cleaned, converted to .csv, then imported into a sqlite3 database. Queries were then run on the database for an overview of the city data and possible further improvements to the OSM map.

___

### Problems Encountered in Audit
___
A Jupyter notebook was used to parse through the raw XML Open Street Map data. Doing this allowed for an examination of tag values based on certain keywords. An in depth audit can be found in <a href='audit.ipynb'>Audit.ipynb</a>. When looking at the groupings of values I noticed problems in these areas.

##### Street Names
- Abbreviated names ("Carrera" -> "Cra")
- Over/under capatlized names
- UTF characters in some names ("Vía" -> "V\xeda")
- Clearly incorrect names or numbers

##### Postcodes
- Contains telephone numbers
- Incorrect length of zip code

##### City Names
- UTF characters in some names ("Medellín" -> "Medell\xedn")
- Abbreviated names ("La Ceja del Tambo" -> "La Ceja")
- Incorrect capatilization and spelling

___
### Data Cleaning
___
Before the data was being copied into csv files it was cleaned based on information from the audit. The reason for the csv files was to have a step in-between the raw data and a sql database. 

Running the data.py file, elements of the osm file are shaped into dictionaries and then searched for any attributes that were identified in the audit.

#### City Names
City names were capatalized differently so they were converted to lowercase before being searched for starting characters. By identifying data that started with 'med' or 'la ceja' it was possible to correct spelling errors. When putting the data in cleaned csv files it was chosen to use the unicode í for Medellín because that is the correct spelling and the unicode characters work in the sql database. However, this character doesn't show up correctly in the osm file.

```python
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
```

#### Postcodes
The correct postcodes found in the audit were different lengths because some data was entered with a leading 0 and some data was not. All postcodes in the Medellín area start with 5 so that and postcode length is what was searched for to ensure correct values. The schema for the sql database specifies the postcode column to be an integer, this will remove any leading zeros. It should be noted that the correct format for postcodes in Colombia is with the leading zero.

```python
def clean_postcode(tag):
    postcode = tag['value']
    if postcode.startswith('05') and len(postcode) == 6:
        return postcode
    if postcode.startswith('5') and len(postcode) == 5:
        return postcode
    else:
        return None
```

#### Street Names

Before cleaning street names a list of acceptable street names in Colombia was created. If the street names in the osm file were in the acceptable list they were added to the database. Some names were abbreviated and those were expanded before being entered into the database. For the street name Vía some entries were using the unicode hex code \xed, it was chosen to convert these to the unicode í before database entry.

```python
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
```

___
### Data Overview
___

#### File Sizes
```
medellin_colombia.osm ......... 81.9 MB
osm_project.db ................ 51.7 MB
nodes_tags.csv ................ 1.2 MB
nodes.csv ..................... 32.3 MB
ways_nodes.csv ................ 11.1 MB
ways_tags.csv ................. 2.9 MB
ways.csv ...................... 2.5 MB
```
#### Number of Nodes
```sql
SELECT COUNT(*) FROM node;

391733
```
#### Number of Node Tags
```sql
SELECT COUNT(*) FROM node_tags;

28942
```
#### Number of Users
```sql
SELECT COUNT(DISTINCT(u.uid)) FROM (SELECT uid FROM node UNION ALL SELECT uid FROM way) u;

926
```
#### Top Users
```sql
SELECT u.user, COUNT(*) as users FROM (select user from node union all select user from way) u GROUP BY u.user ORDER BY users DESC LIMIT 10;

carciofo|139333
JLOSM|28483
Argos|24999
harrierco|24362
Kleper|18022
JosClag|13779
cris_1994|11322
humano|9534
Antares_alf|9512
mono11|7612
```

___
### Data Exploration
___
#### Most Popular Cusine
```sql
SELECT value, COUNT(*) AS num FROM node_tags WHERE key = 'cuisine' GROUP BY value ORDER BY num DESC LIMIT 10;

regional|18
burger|17
pizza|15
coffee_shop|8
vegetarian|6
sandwich|4
steak_house|4
ice_cream|3
local|3
mexican|3
```


#### Most Popular Amenities
```sqlite3
SELECT value, COUNT(*)
AS num FROM node_tags 
WHERE key = 'amenity' 
GROUP BY value 
ORDER BY num DESC 
LIMIT 10;

restaurant|192
place_of_worship|124
fuel|120
school|93
fast_food|82
hospital|79
pharmacy|73
telephone|66
bank|62
bar|57
```


#### Most Common Postcodes
```sql
SELECT value, COUNT(*) AS num FROM node_tags WHERE key = 'postcode' GROUP BY value ORDER BY num DESC; 

050021|5
050022|5
055010|5
055420|5
050023|4
050020|3
050031|3
055422|2
050012|1
050026|1
050034|1
050035|1
051037|1
055413|1
50026|1
```

#### Most Common Cities
```sql
SELECT value, COUNT(*) AS num FROM node_tags WHERE key = 'city' GROUP BY value ORDER BY num DESC;

Medellín|278
Envigado|14
El Carmen de Viboral|7
La Ceja del Tambo|5
Comuna 8|4
Bello|3
Ebéjico|3
Girardota|3
Copacabana|2
El Poblado, Medellín|2
Marinilla|2
Rionegro|2
El Retiro|1
Itagüi|1
Itagüí|1
La Estrella|1
Santa Fe de Antioquia|1
```

___
### Additional Ideas about Dataset
___
It can be seen from the queries above that this dataset is not as complete as it could be. The OSM community could put stricter rules about what different cuisines or amenities can be named. Having the map data combine local and reginal cuisine would make for a more consise dataset. This lack of convention in certain values is clearer in values with lower counts

```sql
SELECT value, COUNT(*) AS num FROM node_tags WHERE key = 'cuisine' GROUP BY value ORDER BY num ASC LIMIT 10;

Arepas_rellenas_a_su_gusta,_hamburguesas,_perros_calientes,_jugos|1
Café|1
Cocina_gourmet,_saludable,_todas_las_proteínas_y_productos_orgánicos.|1
Delikatessen|1
Fusion|1
Fusión|1
Parrilla_y_Bar|1
Peruana_y_Criolla|1
Sanduche_cubano|1
Sanduches_cubanos|1
```

Implementing stricter rules for value names could introduce additional problems. Having many different users inputing data will complicate things if only certain values are allowed. Values that are inputed through GPS data or other data online would need to first be verified against the various rules that restrict what values are allowed in the osm map.
