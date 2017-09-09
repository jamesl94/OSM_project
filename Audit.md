
For the audit the osm document is scanned to look at these tags of interest.

- Street names
- Postcodes
- City names
- Amenities
- Cuisine


```python
import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow
from collections import Counter

OSM_FILE = "medellin_colombia.osm"  

"""HELPER FUNCTIONS"""

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def count_list(list_in):
    #Creates dictionary of occurance: count from list of occurances
    cnt = Counter()
    for n in list_in:
        cnt[n] += 1
    del cnt[None] #Remove None
    return cnt

def search_element_tags(element, key):
    for e in element:
        if e.tag == 'tag' and e.attrib['k'] == key:
            return e.attrib['v']
```


```python
postcodes = []
cities = []
street_names = []
tourism = []
amenities = []
cuisine = []


k = 1 # Write every kth top level element
for i, element in enumerate(get_element(OSM_FILE)):
    if i % k == 0:
        postcodes.append(search_element_tags(element, 'addr:postcode'))
        cities.append(search_element_tags(element, 'addr:city'))
        #For street names only want the first word of name
        street_name = search_element_tags(element, 'addr:street')
        street_name = street_name.split(" ")[0] if street_name is not None else None
        street_names.append(street_name)
        amenities.append(search_element_tags(element, 'amenity'))
        cuisine.append(search_element_tags(element, 'cuisine'))
```


```python
postcodes_count = count_list(postcodes)

#Only looking for incorrect postcodes
for postcode in postcodes_count.keys():
    if postcode.startswith('05') and len(postcode) == 6:
        del postcodes_count[postcode]
```


```python
print(postcodes_count)
```

    Counter({'57': 4, '50026': 2, '00050032': 1, '570': 1, '057': 1, '053080002': 1, '50022': 1, '50021': 1, '00000': 1, '00501': 1, 'tel: 3197200': 1, '+57': 1, '05001000': 1, '05001': 1, '3549090': 1})


The postcodes clearly contain some country codes for telephone numbers (57, +57). Also seems to contain some telephone numbers, and possible zip codes that are missing characters.


```python
cities_count = count_list(cities)
print cities_count
```

    Counter({'Medellin': 290, u'Medell\xedn': 263, 'Envigado': 30, 'medellin': 18, 'La Ceja': 14, 'Rionegro': 14, 'La Ceja del Tambo': 12, 'Bello': 9, 'Girardota': 9, 'El Carmen de Viboral': 7, u'Itag\xfc\xed': 5, 'Copacabana': 4, 'MEDELLIN': 4, 'Comuna 8': 4, u'El Poblado, Medell\xedn': 3, u'Eb\xe9jico': 3, u'Itag\xfci': 3, 'El Carmen De Viboral': 3, u'Medell\xedn - Comuna 8': 2, u'Medell\xecn': 2, 'Sabaneta': 2, '4,8': 2, u'Medel\xedn': 2, 'La Estrella': 2, 'medellim': 2, 'Marinilla': 2, 'Santa Fe de Antioquia': 1, 'Rionegro, Antioquia': 1, 'Angelopolis': 1, 'Donmatias': 1, 'San Vicente': 1, u'MEDELL\xcdN': 1, 'El Carmen De Vibora': 1, 'el carmen de Viboral': 1, 'Sabaneta, Antioquia': 1, 'El Retiro': 1, 'Sabaneta Antioquia': 1, 'Medellin Antioquia': 1, 'Medelin': 1, 'El poblado': 1, u'medell\xedn': 1, u'itag\xfc\xed': 1, u'Medell\xedn, Colombia': 1})


The city address column contains unsuprisingly a lot of "Medellin" entries. It also contains many "Medell\xedn" entries, this is because the city is spelled Medellín and the í is in utf. Additionally there are some mispelled Medellin entries like "Medel\xedn" and inconsistant capitalization. Some cities besides Medellin are in the list and some cities are abreivated "La Ceja del Tambo" -> "La Ceja" 


```python
street_count = count_list(street_names)
accepted_names = ['Carrera', 'Calle', 'Avenida', 'Circular', 'Diagonal', 'Transversal', \
                  'Doble', 'Acceso', 'Salida']
```


```python
#Only looking for incorrect cities
for street in street_count.keys():
    if street in accepted_names:
        del street_count[street]
```


```python
print street_count
```

    Counter({'calle': 12, 'carrera': 9, u'Autopista': 5, u'V\xeda': 5, u'v\xeda': 3, 'CL': 3, 'CALLE': 2, 'Glorieta': 2, 'CARRERA': 2, '54': 2, '51': 2, 'via': 1, 'san': 1, u'La': 1, '61': 1, 'cr48#15sur160': 1, '#': 1, '53c': 1, 'Centro': 1, '46': 1, 'Ayacucho': 1, 'Variante': 1, 'Palenque': 1, 'Circular2': 1, 'Las': 1, 'Loma': 1, 'Tenerife': 1, 'N': 1, 'Mall': 1, '74': 1, '55g': 1, '36A': 1, '97': 1, '39': 1, u'Via': 1, 'Cl': 1, '55': 1, 'Kilometro': 1, '17B': 1, 'Carrera34': 1, 'Cra': 1, '32-118': 1, 'cll31#46': 1, 'Carabobo': 1})


Besides capitaization errors and abbreviated street names, there are some street names that also contain housenumbers and some all together incorrect entries


```python
amenities_count = count_list(amenities)
```


```python
print(amenities_count)
```

    Counter({'school': 265, 'place_of_worship': 234, 'restaurant': 214, 'parking': 187, 'fuel': 141, 'hospital': 134, 'fast_food': 89, 'pharmacy': 74, 'bank': 69, 'telephone': 66, 'library': 66, 'cafe': 66, 'bar': 62, 'college': 58, 'police': 55, 'atm': 55, 'community_centre': 49, 'bench': 40, 'university': 35, 'public_building': 32, 'clinic': 27, 'arts_centre': 26, 'theatre': 25, 'kindergarten': 23, 'bus_station': 21, 'swimming_pool': 19, 'fountain': 18, 'veterinary': 17, 'bicycle_parking': 15, 'taxi': 14, 'doctors': 12, 'nightclub': 12, 'cinema': 11, 'parking_space': 11, 'marketplace': 10, 'fire_station': 10, 'toilets': 9, 'townhall': 9, 'pub': 9, 'casino': 9, 'car_wash': 8, 'drinking_water': 7, 'social_facility': 7, 'parking_entrance': 7, 'bicycle_rental': 6, 'waste_basket': 6, 'prison': 4, 'courthouse': 4, 'public_bookcase': 4, 'post_office': 3, 'food_court': 3, 'recycling': 2, 'studio': 2, 'grave_yard': 2, 'vending_machine': 2, 'toy_library': 1, 'clock': 1, 'Caballerizas': 1, 'shelter': 1, 'monastery': 1, 'car_rental': 1, 'country_club': 1, 'bbq': 1, 'post_box': 1, 'gym': 1, 'dentist': 1, 'Colegio': 1, 'motorcycle_parking': 1, 'ice_cream': 1, 'presbytery': 1, 'nursing_home': 1, 'childcare': 1, 'waste_disposal': 1})


This looks correct, the only thing to change would be removing capitalization from a few entries.


```python
cuisine_count = count_list(cuisine)
print(cuisine_count)
```

    Counter({'regional': 26, 'burger': 18, 'pizza': 17, 'coffee_shop': 9, 'vegetarian': 6, 'chinese': 5, 'sandwich': 4, 'steak_house': 4, 'mexican': 3, 'local': 3, 'ice_cream': 3, 'seafood': 3, 'peruvian': 2, 'sushi': 2, 'vegetarian;vegan': 2, 'barbecue': 2, 'chicken': 2, 'burger;hotdog': 2, 'international': 2, 'grill;local': 2, 'Colombiana': 2, 'Pollo asado': 2, u'caf\xe9s y pasteler\xeda': 1, 'pizza;italian_pizza': 1, 'vegetarian;vegan;regional': 1, 'steak_house;coffee_shop;breakfast;burger;grill;hotdog': 1, u'Fusi\xf3n': 1, u'caf\xe9': 1, 'Parrilla_y_Bar': 1, 'cake;breakfast;french;coffee_shop': 1, 'Sanduche_cubano': 1, 'Tradicional Colombiana': 1, 'sandwich;tea;sausage;cake;local;coffee_shop;pizza;chicken;italian_pizza': 1, 'greek': 1, 'chicken;steak_house;friture': 1, 'vegetarian;regional': 1, 'american': 1, u'panader\xeda': 1, 'Fusion': 1, 'indian': 1, 'japanese;peruvian': 1, u'Cocina_gourmet,_saludable,_todas_las_prote\xednas_y_productos_org\xe1nicos.': 1, 'Sanduches_cubanos': 1, 'bbq': 1, 'friture;burger;ice_cream;hotdog;fish;sausage;sandwich': 1, 'chicken;burger': 1, 'burger;steak_house;breakfast;barbecue;friture;local': 1, 'steak_house;argentinian': 1, 'american;donut;breakfast;diner;tea;friture;coffee_shop': 1, 'burger;steak_house;breakfast;grill': 1, 'breakfast': 1, 'Tailandesa_Vegetariana': 1, 'burger_Fruit_Salad_And More': 1, 'burger;german;chicken': 1, 'arab': 1, 'Delikatessen': 1, 'sausage;pizza': 1, 'coffee_shop;breakfast;cake;bagel': 1, 'Arepas_rellenas_a_su_gusta,_hamburguesas,_perros_calientes,_jugos': 1, 'Peruana_y_Criolla': 1, 'german;pizza': 1, 'fish_and_chips': 1, u'Caf\xe9': 1, 'frutas,salchipapas': 1, 'comida_china': 1, 'american;chicken': 1})


It looks like the cuisine value often contains different food types separated by a ";" Also inconsistent capitalization.
