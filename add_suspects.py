#!/usr/bin/env python3
"""
Add suspect names to the correlation database and update Maltego transforms
"""

import sqlite3
import os
import xml.etree.ElementTree as ET
from datetime import datetime

# Suspect names to add
SUSPECT_NAMES = [
    "lawrence haines",
    "oliver chi",
    "andrew do",
    "shigeru yamada",
    "mitsuru yamada"
]

def add_suspect_names(db_path):
    """Add suspect names as entities to the database"""
    print("[+] Adding suspect names to entities")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for name in SUSPECT_NAMES:
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

def find_correlations(db_path):
    """Find correlations between suspects and other entities"""
    print("[+] Finding correlations between entities")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Find entities that share common patterns
    cursor.execute('''
        SELECT e1.id, e1.name, e1.type, e2.id, e2.name, e2.type
        FROM entities e1, entities e2
        WHERE e1.id < e2.id
        AND (
            (e1.type = 'suspect' AND (e2.type = 'email' OR e2.type = 'domain' OR e2.type = 'host') 
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
            ''', (corr[0], corr[3], 'suspect_association', 'correlation_engine', 0.8))
            print(f"[+] Added correlation: {corr[1]} <-> {corr[4]}")
        except Exception as e:
            print(f"[-] Error storing correlation: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"[+] Found {len(correlations)} correlations")

def update_maltego_transforms(db_path, output_dir):
    """Update Maltego transform data to include suspects"""
    print("[+] Updating Maltego transforms")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all entities including suspects
    cursor.execute("SELECT name, type, source_tool, confidence FROM entities")
    entities = cursor.fetchall()
    
    # Create Maltego XML format
    maltego_xml = os.path.join(output_dir, "maltego", "entities.mtgx")
    os.makedirs(os.path.dirname(maltego_xml), exist_ok=True)
    
    root = ET.Element("MaltegoMessage")
    transform_response = ET.SubElement(root, "MaltegoTransformResponseMessage")
    entities_elem = ET.SubElement(transform_response, "Entities")
    
    for entity in entities:
        entity_elem = ET.SubElement(entities_elem, "Entity")
        entity_elem.set("Type", f"maltego.{entity[1].capitalize()}")
        
        value_elem = ET.SubElement(entity_elem, "Value")
        value_elem.text = entity[0]
        
        # Add additional fields
        additional_fields = ET.SubElement(entity_elem, "AdditionalFields")
        
        source_field = ET.SubElement(additional_fields, "Field")
        source_field.set("Name", "source_tool")
        source_field.text = entity[2]
        
        confidence_field = ET.SubElement(additional_fields, "Field")
        confidence_field.set("Name", "confidence")
        confidence_field.text = str(entity[3])
    
    # Write XML file
    tree = ET.ElementTree(root)
    tree.write(maltego_xml, encoding='utf-8', xml_declaration=True)
    
    conn.close()
    print(f"[+] Maltego transform data saved to {maltego_xml}")

def generate_report(db_path, output_dir):
    """Generate updated correlation report"""
    print("[+] Generating correlation report")
    
    conn = sqlite3.connect(db_path)
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
    
    report_file = os.path.join(output_dir, "correlation_report.txt")
    
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

def main():
    # Paths
    db_path = "./enhanced_results/python_correlation/correlations.db"
    output_dir = "./enhanced_results/python_correlation"
    
    # Add suspect names
    add_suspect_names(db_path)
    
    # Find new correlations
    find_correlations(db_path)
    
    # Update Maltego transforms
    update_maltego_transforms(db_path, output_dir)
    
    # Generate updated report
    generate_report(db_path, output_dir)
    
    print("[+] Suspect names added and correlations updated")
    print(f"[+] Results in {output_dir}")

            ''', (corr[0], corr[3], 'suspect_association', 'correlation_engine', 0.8))
            print(f"[+] Added correlation: {corr[1]} <-> {corr[4]}")
        except Exception as e:
            print(f"[-] Error storing correlation: {e}")
if __name__ == "__main__":
    main()
