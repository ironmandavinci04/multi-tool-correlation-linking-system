#!/usr/bin/env python3
"""
Add target address to the correlation database and update Maltego transforms
"""

import sqlite3
import os
import xml.etree.ElementTree as ET
from datetime import datetime

# Target information
TARGET_INFO = {
    "address": "17642 BEACH HB CA 92647",
    "type": "physical_address",
    "source": "user_input",
    "confidence": 1.0
}

def add_target(db_path):
    """Add target as entity to the database"""
    print("[+] Adding target to entities")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY,
                name TEXT,
                type TEXT,
                source_tool TEXT,
                confidence REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY,
                entity1_id INTEGER,
                entity2_id INTEGER,
                relationship_type TEXT,
                source_tool TEXT,
                confidence REAL
            )
        ''')
        
        cursor.execute('''
            INSERT OR IGNORE INTO entities (name, type, source_tool, confidence)
            VALUES (?, ?, ?, ?)
        ''', (TARGET_INFO["address"], TARGET_INFO["type"], TARGET_INFO["source"], TARGET_INFO["confidence"]))
        print(f"[+] Added target: {TARGET_INFO['address']}")
    except Exception as e:
        print(f"[-] Error storing target: {e}")
    
    conn.commit()
    conn.close()

def find_correlations(db_path):
    """Find correlations for the target"""
    print("[+] Finding correlations for target")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Find entities that might be related to the target
    cursor.execute('''
        SELECT e1.id, e1.name, e1.type, e2.id, e2.name, e2.type
        FROM entities e1, entities e2
        WHERE e1.id < e2.id
        AND (
            (e1.type = 'physical_address' AND e2.type != 'physical_address')
            OR (e2.type = 'physical_address' AND e1.type != 'physical_address')
        )
    ''')
    
    correlations = cursor.fetchall()
    
    for corr in correlations:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO relationships 
                (entity1_id, entity2_id, relationship_type, source_tool, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (corr[0], corr[3], 'location_association', 'correlation_engine', 0.8))
            print(f"[+] Added correlation: {corr[1]} <-> {corr[4]}")
        except Exception as e:
            print(f"[-] Error storing correlation: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"[+] Found {len(correlations)} correlations")

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
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write("Target Analysis Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated: {datetime.now()}\n\n")
        f.write(f"Target Address: {TARGET_INFO['address']}\n\n")
        
        f.write("Entities and Relationships:\n")
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
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Add target
    add_target(db_path)
    
    # Find correlations
    find_correlations(db_path)
    
    # Generate report
    generate_report(db_path, output_dir)
    
    print("[+] Target added and correlations updated")
    print(f"[+] Results in {output_dir}")

if __name__ == "__main__":
    main()
