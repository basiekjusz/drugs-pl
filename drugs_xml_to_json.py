import json
import xmltodict
import argparse
import os

# List of parsed drugs.
drugs_list = []

# List of parsed packagings.
packagings_list = []


def _par(data, key):
    """

    This method takes a dictionary and reads parameter (_par) identified using given key.
    If it is present, then value is returned, otherwise it returns an empty string.

    """

    if(key not in data.keys()):
        return ''
    else:
        return data[key]


def parse_packaging(packaging, id):
    """

    Takes a packaging and puts it into packagings_list.
    Requires also id parameter which is the identifier of the drug.

    """

    packagings_list.append({'id': id,
                            'size': _par(packaging, '@wielkosc'),
                            'sizeUnit': _par(packaging, '@jednostkaWielkosci'),
                            'EANCode': _par(packaging, '@kodEAN'),
                            'accessCategory': _par(packaging, '@kategoriaDostepnosci')})


def parse_packagings(data, id):
    """

    Parses a list of packagings or a single one and puts them into packagings_list.
    Given data parameter can be empty (equal to None). 
    Requires also id parameter which is the identifier of the drug.

    """

    ## WARNING - it is possible that some drugs have no packagings ##
    if(data is None):
        return

    packagings = data["opakowanie"]

    if(isinstance(packagings, list)):
        for packaging in packagings:
            parse_packaging(packaging, id)
    else:
        parse_packaging(packagings, id)


def parse_active_ingredients(data):
    """

    Parses a list of active ingredients or a single one and returns them.
    Given data parameter can be empty (equal to None). 

    """

    ## WARNING - it is possible that some drugs have no active ingredients ##
    if(data is None):
        return

    out = []
    active_ingredients = data['substancjaCzynna']

    if(isinstance(active_ingredients, list)):
        out = active_ingredients
    else:
        out.append(active_ingredients)

    return out


def parse_drug(drug):
    """

    Takes a drug and puts it and it's packagings into suitable lists (drugs_list and packagings_list).

    """

    active_ingredients = parse_active_ingredients(drug["substancjeCzynne"])

    drugs_list.append({'id': _par(drug, '@id'),
                       'name': _par(drug, '@nazwaProduktu'),
                       'activeIngredients': active_ingredients,
                       'MAH': _par(drug, "@podmiotOdpowiedzialny"),
                       'dosage': _par(drug, "@moc"),
                       'form': _par(drug, '@postac'),
                       'ATCCode': _par(drug, "@kodATC")})

    parse_packagings(drug['opakowania'], drug['@id'])


def parse_drugs(data):
    """

    Parses a list of drugs or a single one and puts it and it's packagings into
    suitable lists (drugs_list and packagings_list).

    """

    if('produktLeczniczy' not in data.keys()):
        return

    drugs = data['produktLeczniczy']

    if(isinstance(drugs, list)):
        for drug in drugs:
            parse_drug(drug)
    else:
        parse_drug(drugs)


parser = argparse.ArgumentParser()

parser.add_argument("path", help="Input file path")
parser.add_argument("-n", "--number", action="store_true", help="Display number of parsed items")

args = parser.parse_args()

with open(args.path, "r") as drugs_xml:
    data_dict = xmltodict.parse(drugs_xml.read())

    drugs_xml.close()

parse_drugs(data_dict['produktyLecznicze'])

out_dir = os.path.dirname(os.path.realpath(args.path)) + "/"

with open(out_dir + "drugs.json", "w") as drugs_json:
    json.dump(drugs_list, drugs_json, ensure_ascii=False)
    drugs_json.close()

with open(out_dir + "packagings.json", "w") as packagings_json:
    json.dump(packagings_list, packagings_json, ensure_ascii=False)
    packagings_json.close()

if(args.number):
    print("Total number of parsed drugs:", len(drugs_list))
    print("Total number of parsed packagings:", len(packagings_list))
