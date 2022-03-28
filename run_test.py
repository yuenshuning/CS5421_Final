import unittest
import json
import xmltodict
import os
from pymongo import MongoClient
from lxml import etree

class ImportJsonToMongo:

    def __init__(self, uri, database, file, collection):
        self.client = MongoClient(uri)
        self.database = database
        self.file = file
        self.collection = collection

    def read_json(self):
        with open(self.file, "r", encoding="utf-8") as f:
            records = json.load(f)
        dicts = list(records)
        return dicts

    def import_file(self):
        dicts = self.read_json()
        mycol = self.client.get_database(self.database).get_collection(self.collection)
        mycol.drop()
        mycol.insert_many(dicts)

class ConvertXmlToJson:
    
    def __init__(self, input, output):
        self.input = input
        self.output = output

    def convert_file(self):
        '''
            TODO:
                the mapping between str and num
                "1987" -> 1987
        '''
        xml_file = open(self.input, 'r', encoding="utf-8")
        xml_str = xml_file.read()
        # !  *  '  (   )  ;  :  @   &   =   +   $  ,  /   ?  #   [    ]
        xml_str = xml_str.replace(r"&|*|'|(|)|;|:|@|&|=|+|$|,|/|?|#|[|]", " ")
        json_data = xmltodict.parse(xml_str, encoding='utf-8')
        json_data = json_data[COLLECTION][COLLECTION_ITEM]
        json_info = json.dumps(json_data, indent=2)
        with open(self.output,'w',encoding='utf-8') as json_file:
            json_file.write(json_info)
        

class TestJson(unittest.TestCase):
    XML_FILE = ''

    @classmethod
    def setUpClass(cls):
        print("starting...")
        import_json = ImportJsonToMongo(URI, DATABASE, FILE, COLLECTION)
        import_json.import_file()
        
    @classmethod
    def tearDownClass(cls):
        print("closing...")

    @staticmethod
    def expect_output(xpath):
        xml = etree.parse(TestJson.XML_FILE)
        xml_data = xml.xpath(xpath)

        json_data = list(map(
            lambda x: json.dumps(xmltodict.parse(etree.tostring(x, encoding='utf-8').decode('utf-8'), encoding='utf-8')),
            xml_data
        ))

        return json_data

    @staticmethod
    def wrapper_test(expr, solver=None):
        def func(self: unittest.TestCase):
            expr_s = expr.format(COLLECTION, COLLECTION_ITEM)
            expected = self.expect_output(expr_s)
            if solver is not None:
                solved = solver(expr_s)
                self.assertEqual(expected, solved)
            else:
                print(expected)
        return func


if __name__ == '__main__':
    import argparse
    args = argparse.ArgumentParser()
    args.add_argument('-c', '--config', default='./test/config.json')
    args = args.parse_args()

    config_path = args.config
    with open(config_path, 'r') as f:
        config = json.load(f)

    solver = None
    if config["solver"] == 'compiler':
        import compiler
        solver = compiler.Solver(config).solve
    else:
        pass

    FILE = config['FILE']
    URI = config['URI']
    DATABASE = config['DATABASE']
    # COLLECTION = os.path.basename(FILE).split('.')[0]
    COLLECTION = config['COLLECTION']
    COLLECTION_ITEM = config['COLLECTION_ITEM']

    TestJson.XML_FILE = config['XML_FILE']
    # bind method
    for i, test_case in enumerate(config['test']):
        setattr(TestJson, f'test{i + 1:02d}', TestJson.wrapper_test(test_case['expr'], solver=solver))

    suite = unittest.TestSuite(unittest.makeSuite(TestJson))
    unittest.TextTestRunner(verbosity=2).run(suite)

    # XML_PATH = 'test/library.xml'
    # JSON_PATH = 'test/library_test.json'
    # convert_xml = ConvertXmlToJson(XML_PATH, JSON_PATH)
    # convert_xml.convert_file()
