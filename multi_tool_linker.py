#!/usr/bin/env python3
"""
Multi-Tool Data Correlation and Linking System
Integrates Maltego, TheHarvester, Recon-ng, SpiderFoot, and other tools
"""

import subprocess
import json
import csv
import xml.etree.ElementTree as ET
import argparse
import os
import sys
from datetime import datetime
import sqlite3
import re

class MultiToolLinker:
    def __init__(self, output_dir="./results"):
        self.output_dir = output_dir
        self.db_path = os.path.join(output_dir, "correlations.db")
        self.setup_directories()
        self.setup_database()
        
    def setup_directories(self):
        """Create output directories"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "maltego"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "harvester"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "recon-ng"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "spiderfoot"), exist_ok=True)
        
    def setup_database(self):
        """Setup SQLite database for correlations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables for different data types
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                type TEXT,
                source_tool TEXT,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY,
                entity1_id INTEGER,
                entity2_id INTEGER,
                relationship_type TEXT,
                source_tool TEXT,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entity1_id) REFERENCES entities (id),
                FOREIGN KEY (entity2_id) REFERENCES entities (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def run_theharvester(self, domain):
        """Run TheHarvester for email and subdomain enumeration"""
        print(f"[+] Running TheHarvester on {domain}")
        output_file = os.path.join(self.output_dir, "harvester", f"{domain}_harvester.json")
        
        cmd = [
            "theHarvester",
            "-d", domain,
            "-b", "all",
            "-f", output_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print(f"[+] TheHarvester completed. Results saved to {output_file}")
                return self.parse_harvester_results(output_file)
            else:
                print(f"[-] TheHarvester failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("[-] TheHarvester timed out")
        except Exception as e:
            print(f"[-] Error running TheHarvester: {e}")
        
        return []
    
    def parse_harvester_results(self, output_file):
        """Parse TheHarvester JSON output"""
        entities = []
        try:
            with open(output_file, 'r') as f:
                data = json.load(f)
                
            # Extract emails
            if 'emails' in data:
                for email in data['emails']:
                    entities.append({
                        'name': email,
                        'type': 'email',
                        'source_tool': 'theharvester',
                        'confidence': 0.8
                    })
            
            # Extract hosts/subdomains
            if 'hosts' in data:
                for host in data['hosts']:
                    entities.append({
                        'name': host,
                        'type': 'domain',
                        'source_tool': 'theharvester',
                        'confidence': 0.8
                    })
                    
        except Exception as e:
            print(f"[-] Error parsing TheHarvester results: {e}")
            
        return entities
    
    def run_recon_ng(self, domain):
        """Run Recon-ng modules"""
        print(f"[+] Running Recon-ng on {domain}")
        
        # Create recon-ng resource file
        resource_file = os.path.join(self.output_dir, "recon-ng", f"{domain}_recon.rc")
        
        commands = [
            f"workspaces create {domain}_workspace",
            f"db insert domains {domain}",
            "modules load recon/domains-hosts/hackertarget",
            "run",
            "modules load recon/domains-hosts/threatcrowd",
            "run",
            "modules load recon/hosts-hosts/resolve",
            "run",
            "show hosts",
            "export csv hosts /tmp/recon_hosts.csv",
            "exit"
        ]
        
        with open(resource_file, 'w') as f:
            f.write('\n'.join(commands))
        
        try:
            cmd = ["recon-ng", "-r", resource_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"[+] Recon-ng completed")
                return self.parse_recon_results()
            else:
                print(f"[-] Recon-ng failed: {result.stderr}")
        except Exception as e:
            print(f"[-] Error running Recon-ng: {e}")
            
        return []
    
    def parse_recon_results(self):
        """Parse Recon-ng CSV output"""
        entities = []
        try:
            if os.path.exists("/tmp/recon_hosts.csv"):
                with open("/tmp/recon_hosts.csv", 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'host' in row:
                            entities.append({
                                'name': row['host'],
                                'type': 'host',
                                'source_tool': 'recon-ng',
                                'confidence': 0.7
                            })
        except Exception as e:
            print(f"[-] Error parsing Recon-ng results: {e}")
            
        return entities
    
    def run_spiderfoot(self, target):
        """Run SpiderFoot scan"""
        print(f"[+] Running SpiderFoot on {target}")
        
        scan_name = f"{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Start SpiderFoot scan
            cmd = [
                "python3", "/usr/share/spiderfoot/sf.py",
                "-s", target,
                "-t", "TLD",
                "-o", "csv"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print(f"[+] SpiderFoot completed")
                return self.parse_spiderfoot_results(result.stdout)
            else:
                print(f"[-] SpiderFoot failed: {result.stderr}")
        except Exception as e:
            print(f"[-] Error running SpiderFoot: {e}")
            
        return []
    
    def parse_spiderfoot_results(self, output):
        """Parse SpiderFoot output"""
        entities = []
        lines = output.split('\n')
        
        for line in lines:
            if ',' in line and not line.startswith('#'):
                parts = line.split(',')
                if len(parts) >= 3:
                    entities.append({
                        'name': parts[1].strip(),
                        'type': parts[0].strip().lower(),
                        'source_tool': 'spiderfoot',
                        'confidence': 0.6
                    })
                    
        return entities
    
    def create_maltego_transforms(self, entities):
        """Create Maltego transform data"""
        print("[+] Creating Maltego transforms")
        
        # Create Maltego XML format
        maltego_xml = os.path.join(self.output_dir, "maltego", "entities.mtgx")
        
        root = ET.Element("MaltegoMessage")
        transform_response = ET.SubElement(root, "MaltegoTransformResponseMessage")
        entities_elem = ET.SubElement(transform_response, "Entities")
        
        for entity in entities:
            entity_elem = ET.SubElement(entities_elem, "Entity")
            # Use Person type for suspects, otherwise capitalize the existing type
            entity_type = "Person" if entity['type'] == 'suspect' else entity['type'].capitalize()
            entity_elem.set("Type", f"maltego.{entity_type}")
            
            value_elem = ET.SubElement(entity_elem, "Value")
            value_elem.text = entity['name']
            
            # Add additional fields
            additional_fields = ET.SubElement(entity_elem, "AdditionalFields")
            
            source_field = ET.SubElement(additional_fields, "Field")
            source_field.set("Name", "source_tool")
            source_field.text = entity['source_tool']
            
            confidence_field = ET.SubElement(additional_fields, "Field")
            confidence_field.set("Name", "confidence")
            confidence_field.text = str(entity['confidence'])
        
        # Write XML file
        tree = ET.ElementTree(root)
        tree.write(maltego_xml, encoding='utf-8', xml_declaration=True)
        
        print(f"[+] Maltego transform data saved to {maltego_xml}")
        
    def add_suspect_names(self, suspect_names):
        """Add suspect names as entities"""
        print("[+] Adding suspect names to entities")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for name in suspect_names:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO entities (name, type, source_tool, confidence)
                    VALUES (?, ?, ?, ?)
                ''', (name, 'suspect', 'user_input', 1.0))
                print(f"[+] Added suspect: {name}")
            except Exception as e:
                print(f"[-] Error storing suspect name {name}: {e}")
        
        conn.commit()
        conn.close()
        
    def store_entities(self, entities):
        """Store entities in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for entity in entities:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO entities (name, type, source_tool, confidence)
                    VALUES (?, ?, ?, ?)
                ''', (entity['name'], entity['type'], entity['source_tool'], entity['confidence']))
            except Exception as e:
                print(f"[-] Error storing entity {entity['name']}: {e}")
        
        conn.commit()
        conn.close()
        
    def find_correlations(self):
        """Find correlations between entities"""
        print("[+] Finding correlations between entities")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find entities that share common patterns
        cursor.execute('''
            SELECT e1.id, e1.name, e1.type, e2.id, e2.name, e2.type
            FROM entities e1, entities e2
            WHERE e1.id < e2.id
            AND (
                (e1.type = 'email' AND e2.type = 'domain' AND e1.name LIKE '%' || e2.name || '%')
                OR (e1.type = 'domain' AND e2.type = 'host' AND e2.name LIKE '%' || e1.name || '%')
                OR (e1.type = 'host' AND e2.type = 'domain' AND e1.name LIKE '%' || e2.name || '%')
                OR (e1.type = 'suspect' AND (e2.type = 'email' OR e2.type = 'domain' OR e2.type = 'host') 
                    AND (e1.name LIKE '%' || e2.name || '%' OR e2.name LIKE '%' || e1.name || '%'))
            )
        ''')
        
        correlations = cursor.fetchall()
        
        for corr in correlations:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO relationships 
                    (entity1_id, entity2_id, relationship_type, source_tool, confidence)
                    VALUES (?, ?, ?, ?, ?)
                ''', (corr[0], corr[3], 'domain_association', 'correlation_engine', 0.8))
            except Exception as e:
                print(f"[-] Error storing correlation: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"[+] Found {len(correlations)} correlations")
        
    def generate_report(self):
        """Generate correlation report"""
        print("[+] Generating correlation report")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all entities with their relationships
        cursor.execute('''
            SELECT e.name, e.type, e.source_tool, e.confidence,
                   COUNT(r.id) as relationship_count
            FROM entities e
            LEFT JOIN relationships r ON (e.id = r.entity1_id OR e.id = r.entity2_id)
            GROUP BY e.id
            ORDER BY relationship_count DESC, e.confidence DESC
        ''')
        
        entities = cursor.fetchall()
        
        report_file = os.path.join(self.output_dir, "correlation_report.txt")
        
        with open(report_file, 'w') as f:
            f.write("Multi-Tool Correlation Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now()}\n\n")
            
            f.write("Entities by Relationship Count:\n")
            f.write("-" * 30 + "\n")
            
            for entity in entities:
                f.write(f"Name: {entity[0]}\n")
                f.write(f"Type: {entity[1]}\n")
                f.write(f"Source: {entity[2]}\n")
                f.write(f"Confidence: {entity[3]}\n")
                f.write(f"Relationships: {entity[4]}\n")
                f.write("-" * 20 + "\n")
        
        conn.close()
        
        print(f"[+] Report saved to {report_file}")
        
    def run_analysis(self, target, suspect_names=None):
        """Run complete multi-tool analysis"""
        print(f"[+] Starting multi-tool analysis on {target}")
        
        all_entities = []
        
        # Run each tool
        all_entities.extend(self.run_theharvester(target))
        all_entities.extend(self.run_recon_ng(target))
        all_entities.extend(self.run_spiderfoot(target))
        
        # Store entities in database
        self.store_entities(all_entities)
        
        # Add suspect names if provided
        if suspect_names:
            print(f"[+] Adding {len(suspect_names)} suspect names")
            self.add_suspect_names(suspect_names)
        
        # Find correlations
        self.find_correlations()
        
        # Create Maltego transforms
        # Query all entities including suspects for transform generation
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, type, source_tool, confidence FROM entities")
        all_entities = [
            {'name': row[0], 'type': row[1], 'source_tool': row[2], 'confidence': row[3]}
            for row in cursor.fetchall()
        ]
        conn.close()
        
        self.create_maltego_transforms(all_entities)
        
        # Generate report
        self.generate_report()
        
        print(f"[+] Analysis complete. Results in {self.output_dir}")

def main():
    parser = argparse.ArgumentParser(
        description="Multi-Tool Data Correlation and Linking System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run analysis on a domain
  %(prog)s example.com
  
  # Run analysis with suspect names
  %(prog)s example.com -s "John Doe" "Jane Smith"
  
  # Specify output directory
  %(prog)s example.com -o ./my_results -s "John Doe"
"""
    )
    parser.add_argument("target", help="Target domain or entity to analyze")
    parser.add_argument("-o", "--output", default="./results", help="Output directory")
    parser.add_argument("-s", "--suspects", nargs='+', help="List of suspect names to add")
    
    args = parser.parse_args()
    
    try:
        # Create linker instance
        linker = MultiToolLinker(args.output)
        
        # Run analysis with optional suspect names
        linker.run_analysis(args.target, suspect_names=args.suspects)
        
    except KeyboardInterrupt:
        print("\n[-] Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Error during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

