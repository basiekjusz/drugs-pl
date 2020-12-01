# drugs-pl

Collection of Polish authorised drugs and reimbursements dictionaries parsed to JSON. Includes parsers. The files has been originally obtained and parsed
from files from [CSIOZ medical products register (updated every day)](https://rejestrymedyczne.csioz.gov.pl/registry/rpl) and [SOLR tool (updated every month)](https://ezdrowie.gov.pl/portal/home/dla-podmiotow-leczniczych/narzedzie-pomagajace-okreslic-poziom-refundacji).

## Parsers usage

Both parsers require `python3` and `xmltodict` which you can install using following command:

```
apt-get install python3
pip install xmltodict
```

When running any of two parsers you must specify input file path. For example:

```
python3 drugs_xml_to_json.py drugs_source.xml
```

You can also display number of parsed elements using `-n` or `--number` flag.

```
python3 drugs_xml_to_json.py drugs_source.xml -n
```
