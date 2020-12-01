import json
import xmltodict
import argparse
import os

# List of parsed reimbursements.
reimbursements_list = []

# List of parsed indications.
indications_list = []

ids = {}


def _par(data, key):
    """

    This method takes a dictionary and reads parameter (_par) identified using given key.
    If it is present, then value is returned, otherwise it returns an empty string.

    """
    if(key not in data.keys()):
        return ''
    else:
        return data[key]


def parse_indication(indication):
    """

    Takes an indication and puts it into indications_list.
    Requires also an id parameter which is the identifier of the reimbursement it's assigned to.

    """
    id = _par(indication, '@idWskazania')

    if not id in ids.keys():
        indications_list.append({'id': id,
                                 'ageFrom': _par(indication, '@wiekOd'),
                                 'ageTo': _par(indication, "@wiekDo"),
                                 'indication': _par(indication, "#text")})
        ids[id] = 1

    return id


def parse_indications(data):
    """

    Takes an indication or a list of them and puts into indications_list.
    Requires also an id parameter which is the identifier of the reimbursement they're assigned to.

    """

    ## WARNING - it is possible that some reimbursements have no indications ##
    if(data is None):
        return

    out = []
    indications = data['wskazanie']

    if(isinstance(indications, list)):
        for indication in indications:
            out.append(parse_indication(indication))
    else:
        out.append(parse_indication(indications))

    return out


def parse_reimbursement(reimbursement, ean):
    """

    Takes a reimbursement and puts it into reimbursements_list.
    Requires also an id parameter which is the identifier of the reimbursement it's assigned to.

    """

    # As the same indications may appear in many reimbursements, it is a many-to-many relation.
    # The relation is stored as a list of indication ids in reimbursement.
    indications_ids = parse_indications(reimbursement['wskazania'])

    reimbursements_list.append({'EANCode': ean,
                                'reimbursementSize': _par(reimbursement, 'poziomOdplatnosciEnum'),
                                'patientSurcharge': _par(reimbursement, 'doplataSwiadczeniobiorcy'),
                                'retailPrice': _par(reimbursement, 'cenaDetaliczna'),
                                'indication_ids': indications_ids})


def parse_reimbursements(reimbursements, ean):
    """

    Takes a reimbursements list or a single one and puts it into reimbursements_list.
    Requires also an ean parameter which is the EAN code of the packaging it's assigned to.

    """

    if(isinstance(reimbursements, list)):
        for reimbursement in reimbursements:
            parse_reimbursement(reimbursement, ean)
    else:
        parse_reimbursement(reimbursements, ean)


def parse_packaging(packaging):
    """

    Takes a packaging and parses it's reimbursements and indications.

    """
    parse_reimbursements(packaging['Refundacja'], packaging["EAN"])


def parse_packagings(data):
    """

    Takes a packagings list and parses it's reimbursements and indications.

    """
    if('OpakowanieLeku' not in data.keys()):
        return

    if(isinstance(data["OpakowanieLeku"], list)):
        for packaging in data["OpakowanieLeku"]:
            parse_packaging(packaging)
    else:
        parse_packaging(data["OpakowanieLeku"])


parser = argparse.ArgumentParser()

parser.add_argument("path", help="Input file path")
parser.add_argument("-n", "--number", action="store_true", help="Display number of parsed items")

args = parser.parse_args()

with open(args.path, "r") as solr_xml:
    data_dict = xmltodict.parse(solr_xml.read())

    solr_xml.close()

parse_packagings(data_dict['ListaRefundacyjna'])

out_dir = os.path.dirname(os.path.realpath(args.path)) + "/"

with open(out_dir + "reimbursements.json", "w") as reimbursements_json:
    json.dump(reimbursements_list, reimbursements_json, ensure_ascii=False)
    reimbursements_json.close()

with open(out_dir + "indications.json", "w") as indications_json:
    json.dump(indications_list, indications_json, ensure_ascii=False)
    indications_json.close()

if(args.number):
    print("Total number of parsed reimbursements:", len(reimbursements_list))
    print("Total number of parsed indications:", len(indications_list))
