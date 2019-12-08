# Post-processing of regression output to generate JUnit XML for Jenkins
import xml.etree.ElementTree as ET
from xml.dom import minidom
import argparse

__author__ = 'Richard Berger'
__email__ = "richard.berger@temple.edu"

def main():
    # parse CLI arguments
    parser = argparse.ArgumentParser(description='Parses regression logfile and generates JUnit XML for Jenkins')
    parser.add_argument('--test-dir', default='/var/lib/jenkins/jobs/', help='root directory of tests')
    parser.add_argument('--log-file', default='test.out', help='log file to parse')
    parser.add_argument('--out-file', default='regression.xml', help='output filename')
    args = parser.parse_args()
    
    # extend ElementTree with CDATA
    ET._original_serialize_xml = ET._serialize_xml
    
    def CDATA(text):
        element = ET.Element('![CDATA[')
        element.text = text
        return element
    
    def _serialize_xml(write, elem, qnames, namespaces,short_empty_elements,**kwargs):
        if elem.tag == '![CDATA[':
            write("<%s%s]]>" % (elem.tag, elem.text))
            if elem.tail:
                write(elem.tail)
        else:
            return ET._original_serialize_xml(write, elem, qnames, namespaces, short_empty_elements, **kwargs)
    
    ET._serialize_xml = ET._serialize['xml'] = _serialize_xml
    
    
    def pretty_xml(elem):
        """pretty printing of XML """
        txt = ET.tostring(elem, 'utf-8')
        parsed = minidom.parseString(txt)
        return parsed.toprettyxml(indent='    ')
    
    
    # parse logfile
    in_block = False
    name_offset = len(args.test_dir)
    tests = []
    contents = []
    failures = 0
    
    with open(args.log_file) as f:
        for line in f:
            if line.startswith('~~~~'):
                in_block = not in_block
                if not in_block:
                    contents = []
                continue
    
            if in_block:
                contents.append(line)
                if line.startswith('dir = '):
                    path = line.split('=')[1].strip()[name_offset:]
                elif line.startswith('test = '):
                    test = line.split('=')[1].strip()
                elif line.startswith('*** test') or line.startswith('!!! test'):
                    passed = line.split()[3].strip() == 'passed'
                elif line.startswith('elapsed time = '):
                    elapsed = float(line.split('=')[1].strip().split()[0])
                    stdout = ''.join(contents)
                    tests.append((path, test, passed, elapsed, stdout))
                    if not passed:
                        failures += 1
    
    # generate JUnit XML
    testsuites = ET.Element('testsuites')
    testsuite = ET.SubElement(testsuites, 'testsuite', {'failures' : str(failures),
                                                        'errors' : "0",
                                                        'name' : 'regression tests',
                                                        'tests': str(len(tests))})
    
    for t in tests:
        classname = t[0].replace('/', '.')
        testname = t[1]
        passed = t[2]
        elapsed = t[3]
    
        testcase = ET.SubElement(testsuite, 'testcase', {'classname' : classname,
                                                         'name' : testname,
                                                         'time' : str(elapsed)})
    
        sysout = ET.SubElement(testcase, 'system-out')
        sysout.append(CDATA(''.join(t[4])))
    
        if not passed:
            failure = ET.SubElement(testcase, 'failure', {'type' : 'failure', 'message' : 'test ' + testname + ' FAILED'})
    
    
    with open(args.out_file, 'w') as out:
        out.write(pretty_xml(testsuites))

if __name__ == "__main__":
    main()
