#!/usr/bin/env python3
"""
SNMP MIB Coverage Analyzer

This script queries an SNMP endpoint for all OIDs, analyzes MIB files to find coverage,
and generates a report highlighting OIDs with and without MIB coverage.
"""

import os
import sys
import argparse
import json
from collections import defaultdict
import subprocess
import re
from pysnmp.hlapi import *
from pysmi.reader import FileReader
from pysmi.searcher import PyFileSearcher
from pysmi.writer import PyFileWriter
from pysmi.parser import SmiStarParser
from pysmi.codegen import PySnmpCodeGen
from pysmi.compiler import MibCompiler

class SNMPMIBAnalyzer:
    def __init__(self, host, port=161, community='public', mib_dir=None, output_format='text'):
        """
        Initialize the SNMP MIB Analyzer.
        
        Args:
            host (str): The SNMP agent hostname or IP
            port (int): The SNMP agent port (default: 161)
            community (str): SNMP community string (default: 'public')
            mib_dir (str): Directory containing MIB files (default: None)
            output_format (str): Output format ('text', 'json', or 'csv')
        """
        self.host = host
        self.port = port
        self.community = community
        self.mib_dir = mib_dir if mib_dir else './mibs'
        self.output_format = output_format
        self.mib_oids = {}  # {oid: {mibs: [mib1, mib2], name: "name"}}
        self.agent_oids = []
        
    def compile_mibs(self):
        """Compile MIB files using pysmi."""
        print(f"Compiling MIB files from {self.mib_dir}...")
        
        # Initialize MIB compiler
        mibCompiler = MibCompiler(
            SmiStarParser(),
            PySnmpCodeGen(),
            PyFileWriter(self.mib_dir + '/pysnmp')
        )
        
        # Configure MIB compiler
        mibCompiler.addSources(FileReader(self.mib_dir))
        mibCompiler.addSearchers(PyFileSearcher(self.mib_dir + '/pysnmp'))
        
        # Get list of MIB files in directory (excluding compiled Python files)
        mib_files = [f for f in os.listdir(self.mib_dir) 
                     if os.path.isfile(os.path.join(self.mib_dir, f)) 
                     and not f.endswith('.py') 
                     and not f.startswith('.')]
        
        # Compile MIBs
        results = mibCompiler.compile(*mib_files)
        print(f"Compiled {len(results)} MIB files")
        
    def extract_oids_from_mibs(self):
        """Extract OIDs from MIB files using snmptranslate."""
        print("Extracting OIDs from MIB files...")
        
        # Get list of MIB files
        mib_files = [f for f in os.listdir(self.mib_dir) 
                     if os.path.isfile(os.path.join(self.mib_dir, f)) 
                     and not f.endswith('.py') 
                     and not f.startswith('.')]
        
        for mib_file in mib_files:
            mib_name = os.path.splitext(mib_file)[0]
            print(f"Processing MIB: {mib_name}")
            
            try:
                # Use snmptranslate to get all OIDs in the MIB
                cmd = f"snmptranslate -m {os.path.join(self.mib_dir, mib_file)} -Tp"
                output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode('utf-8')
                
                # Extract OIDs and names
                oid_pattern = r'\+--([0-9\.]+) \((\w+)\)'
                for match in re.finditer(oid_pattern, output):
                    oid = match.group(1)
                    name = match.group(2)
                    
                    if oid not in self.mib_oids:
                        self.mib_oids[oid] = {'mibs': [mib_name], 'name': name}
                    else:
                        if mib_name not in self.mib_oids[oid]['mibs']:
                            self.mib_oids[oid]['mibs'].append(mib_name)
            except subprocess.CalledProcessError:
                print(f"Error processing MIB: {mib_name}")
                continue
                
        print(f"Extracted {len(self.mib_oids)} unique OIDs from {len(mib_files)} MIB files")
        
    def query_snmp_agent(self):
        """Query SNMP agent to get all OIDs."""
        print(f"Querying SNMP agent at {self.host}:{self.port}...")
        
        self.agent_oids = []
        
        # Walk the entire MIB tree (starting from .1)
        iterator = nextCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.host, self.port)),
            ContextData(),
            ObjectType(ObjectIdentity('1')),
            lexicographicMode=True
        )
        
        for errorIndication, errorStatus, errorIndex, varBinds in iterator:
            if errorIndication:
                print(f"SNMP error: {errorIndication}")
                break
            elif errorStatus:
                print(f"SNMP error: {errorStatus.prettyPrint()} at {varBinds[int(errorIndex)-1][0] if errorIndex else '?'}")
                break
            else:
                for varBind in varBinds:
                    oid = '.'.join([str(x) for x in varBind[0].getOid()])
                    value = varBind[1].prettyPrint()
                    self.agent_oids.append({
                        'oid': oid,
                        'value': value
                    })
        
        print(f"Retrieved {len(self.agent_oids)} OIDs from SNMP agent")
        
    def analyze_oid_coverage(self):
        """Analyze OID coverage by comparing agent OIDs with MIB OIDs."""
        print("Analyzing OID coverage...")
        
        results = {
            'covered': [],
            'uncovered': []
        }
        
        for agent_oid in self.agent_oids:
            oid = agent_oid['oid']
            is_covered = False
            
            # Check for exact match
            if oid in self.mib_oids:
                results['covered'].append({
                    'oid': oid,
                    'value': agent_oid['value'],
                    'mibs': self.mib_oids[oid]['mibs'],
                    'name': self.mib_oids[oid]['name']
                })
                is_covered = True
                continue
            
            # Check if the OID is a child of any MIB OID
            for mib_oid in self.mib_oids:
                if oid.startswith(mib_oid + '.'):
                    results['covered'].append({
                        'oid': oid,
                        'value': agent_oid['value'],
                        'mibs': self.mib_oids[mib_oid]['mibs'],
                        'name': f"{self.mib_oids[mib_oid]['name']}-instance"
                    })
                    is_covered = True
                    break
            
            if not is_covered:
                results['uncovered'].append({
                    'oid': oid,
                    'value': agent_oid['value']
                })
        
        return results
    
    def generate_report(self, results):
        """Generate a report of the analysis."""
        if self.output_format == 'json':
            return json.dumps(results, indent=2)
        elif self.output_format == 'csv':
            csv_lines = ['OID,Value,Coverage,MIBs,Name']
            
            for oid_info in results['covered']:
                mibs = '|'.join(oid_info['mibs'])
                csv_lines.append(f"{oid_info['oid']},{oid_info['value']},covered,{mibs},{oid_info['name']}")
            
            for oid_info in results['uncovered']:
                csv_lines.append(f"{oid_info['oid']},{oid_info['value']},uncovered,,")
            
            return '\n'.join(csv_lines)
        else:  # text format
            report = []
            report.append("=" * 80)
            report.append("SNMP MIB Coverage Analysis Report")
            report.append("=" * 80)
            report.append(f"SNMP Agent: {self.host}:{self.port}")
            report.append(f"Total OIDs retrieved: {len(self.agent_oids)}")
            report.append(f"OIDs with MIB coverage: {len(results['covered'])}")
            report.append(f"OIDs without MIB coverage: {len(results['uncovered'])}")
            report.append("=" * 80)
            
            report.append("\nOIDs with MIB coverage:")
            report.append("-" * 80)
            for oid_info in results['covered']:
                report.append(f"OID: {oid_info['oid']}")
                report.append(f"Value: {oid_info['value']}")
                report.append(f"Name: {oid_info['name']}")
                report.append(f"MIBs: {', '.join(oid_info['mibs'])}")
                report.append("-" * 40)
            
            report.append("\nOIDs without MIB coverage:")
            report.append("-" * 80)
            for oid_info in results['uncovered']:
                report.append(f"OID: {oid_info['oid']}")
                report.append(f"Value: {oid_info['value']}")
                report.append("-" * 40)
            
            return '\n'.join(report)
    
    def run(self):
        """Run the complete analysis."""
        try:
            self.extract_oids_from_mibs()
            self.query_snmp_agent()
            results = self.analyze_oid_coverage()
            report = self.generate_report(results)
            return report
        except Exception as e:
            return f"Error during analysis: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description='SNMP MIB Coverage Analyzer')
    parser.add_argument('--host', required=True, help='SNMP agent hostname or IP')
    parser.add_argument('--port', type=int, default=161, help='SNMP agent port (default: 161)')
    parser.add_argument('--community', default='public', help='SNMP community string (default: public)')
    parser.add_argument('--mib-dir', help='Directory containing MIB files')
    parser.add_argument('--format', choices=['text', 'json', 'csv'], default='text', help='Output format')
    parser.add_argument('--output', help='Output file (default: stdout)')
    
    args = parser.parse_args()
    
    analyzer = SNMPMIBAnalyzer(
        host=args.host,
        port=args.port,
        community=args.community,
        mib_dir=args.mib_dir,
        output_format=args.format
    )
    
    report = analyzer.run()
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()