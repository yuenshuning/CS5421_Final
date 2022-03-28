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
        xml = etree.parse('test/library.xml')
        xml_data = xml.xpath(xpath)

        json_data = list(map(
            lambda x: json.dumps(xmltodict.parse(etree.tostring(x, encoding='utf-8').decode('utf-8'), encoding='utf-8')),
            xml_data
        ))

        return json_data

    def test01(self):
        expr = "/child::{}/child::{}/child::songs/child::song/child::title".format(COLLECTION, COLLECTION_ITEM)
        expected = self.expect_output(expr)
        # actual_output = 
        # self.assertEqual(expected, actual_output)
        print(expected)
    
    def test02(self):
        expr = "/child::{}/child::{}/child::songs/child::*".format(COLLECTION, COLLECTION_ITEM)
        expected = self.expect_output(expr)
        print(expected)

    def test03(self):
        expr = "/child::{}/child::{}[child::artists/child::artist/child::name='Kris Dayanti']/child::year".format(COLLECTION, COLLECTION_ITEM)
        expected = self.expect_output(expr)
        print(expected)
    
    def test04(self):
        expr = "/child::{}/child::{}[child::year>=1990 and child::year <=1995]/child::title".format(COLLECTION, COLLECTION_ITEM)
        expected = self.expect_output(expr)
        print(expected)

    def test05(self):
        expr = "/child::{}/child::{}[child::year>=1990 and child::year <=1995]/descendant::title".format(COLLECTION, COLLECTION_ITEM)
        expected = self.expect_output(expr)
        print(expected)

    def test06(self):
        expr = "/child::{}/child::{}[child::year>=1990 and child::year <=1995]/child::songs/following-sibling::*".format(COLLECTION, COLLECTION_ITEM)
        expected = self.expect_output(expr)
        print(expected)



if __name__ == '__main__':
    FILE = 'test/library.json'
    URI = 'mongodb://localhost:27017/'
    DATABASE = 'cs5421'
    # COLLECTION = os.path.basename(FILE).split('.')[0]
    COLLECTION = 'library'
    COLLECTION_ITEM = 'album'

    suite = unittest.TestSuite(unittest.makeSuite(TestJson))
    unittest.TextTestRunner(verbosity=2).run(suite)

    # XML_PATH = 'test/library.xml'
    # JSON_PATH = 'test/library_test.json'
    # convert_xml = ConvertXmlToJson(XML_PATH, JSON_PATH)
    # convert_xml.convert_file()