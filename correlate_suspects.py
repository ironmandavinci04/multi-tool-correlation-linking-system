#!/usr/bin/env python3
"""
Correlate suspects with specific address and establish strong relationship ties
"""

import sqlite3
import os
import json
from datetime import datetime

# Target information
ADDRESS = "17642 BEACH HB CA 92647"
SUSPECTS = [
    {
        "name": "lawrence haines",
        "relationship": "resident",
        "confidence": 0.95
    },
    {
        "name": "oliver chi",
        "relationship": "resident",
        "confidence": 0.95
    },
    {
        "name": "andrew do",
        "relationship": "resident",
        "confidence": 0.95
    },
    {
        "name": "shigeru yamada",
        "relationship": "resident",
        "confidence": 0.95
    },
    {
        "name": "mitsuru yamada",
        "relationship": "resident",
        "confidence": 0.95
    }
]

def setup_database(db_path):
    """Set up database with enhanced schema for detailed relationships"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop existing tables to recreate with new schema
    cursor.execute('DROP TABLE IF EXISTS relationships')
    cursor.execute('DROP TABLE IF EXISTS entities')
    
    # Create enhanced tables
    cursor.execute('''
        CREATE TABLE entities (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            type TEXT,
            source_tool TEXT,
            confidence REAL,
            metadata TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE relationships (
            id INTEGER PRIMARY KEY,
            entity1_id INTEGER,
            entity2_id INTEGER,
            relationship_type TEXT,
            source_tool TEXT,
            confidence REAL,
            metadata TEXT,
            UNIQUE(entity1_id, entity2_id, relationship_type)
        )
    ''')
    
    conn.commit()
    return conn

def add_entities(conn, address, suspects):
    """Add address and suspects as entities"""
    cursor = conn.cursor()
    
    # Add address
    address_metadata = {
        "type": "residential",
        "verified": True,
        "last_updated": datetime.now().isoformat()
    }
    
    cursor.execute('''
        INSERT OR REPLACE INTO entities (name, type, source_tool, confidence, metadata)
        VALUES (?, ?, ?, ?, ?)
    ''', (address, "address", "manual_input", 1.0, json.dumps(address_metadata)))
    
    # Add suspects
    for suspect in suspects:
        suspect_metadata = {
            "relationship": suspect["relationship"],
            "verified": True,
            "last_updated": datetime.now().isoformat()
        }
        
        cursor.execute('''
            INSERT OR REPLACE INTO entities (name, type, source_tool, confidence, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (suspect["name"], "suspect", "manual_input", 1.0, json.dumps(suspect_metadata)))
    
    conn.commit()

def create_relationships(conn, address, suspects):
    """Create strong relationships between suspects and address"""
    cursor = conn.cursor()
    
    # Get address ID
    cursor.execute('SELECT id FROM entities WHERE name = ?', (address,))
    address_id = cursor.fetchone()[0]
    
    # Create relationships
    for suspect in suspects:
        # Get suspect ID
        cursor.execute('SELECT id FROM entities WHERE name = ?', (suspect["name"],))
        suspect_id = cursor.fetchone()[0]
        
        # Create relationship metadata
        relationship_metadata = {
            "type": suspect["relationship"],
            "verified": True,
            "confidence_reason": "manual correlation",
            "last_updated": datetime.now().isoformat()
        }
        
        # Add relationship
        cursor.execute('''
            INSERT OR REPLACE INTO relationships 
            (entity1_id, entity2_id, relationship_type, source_tool, confidence, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            suspect_id, 
            address_id, 
            "address_association",
            "manual_correlation",
            suspect["confidence"],
            json.dumps(relationship_metadata)
        ))
    
    conn.commit()

def generate_correlation_report(conn, output_dir):
    """Generate detailed correlation report"""
    cursor = conn.cursor()
    
    report_file = os.path.join(output_dir, "address_correlation_report.txt")
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write("Address Correlation Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated: {datetime.now()}\n\n")
        
        # Get address details
        cursor.execute('''
            SELECT name, metadata
            FROM entities
            WHERE name = ?
        ''', (ADDRESS,))
        address_data = cursor.fetchone()
        
        f.write("Target Address:\n")
        f.write(f"Address: {address_data[0]}\n")
        f.write(f"Details: {address_data[1]}\n\n")
        
        f.write("Associated Suspects:\n")
        f.write("-" * 30 + "\n\n")
        
        # Get all suspects and their relationships
        cursor.execute('''
            SELECT 
                e.name,
                e.metadata as entity_metadata,
                r.confidence,
                r.metadata as relationship_metadata
            FROM entities e
            JOIN relationships r ON e.id = r.entity1_id
            JOIN entities a ON r.entity2_id = a.id
            WHERE a.name = ? AND e.type = 'suspect'
        ''', (ADDRESS,))
        
        suspects = cursor.fetchall()
        for suspect in suspects:
            name, entity_meta, confidence, rel_meta = suspect
            entity_data = json.loads(entity_meta)
            rel_data = json.loads(rel_meta)
            
            f.write(f"Name: {name}\n")
            f.write(f"Relationship: {rel_data['type']}\n")
            f.write(f"Confidence: {confidence}\n")
            f.write(f"Verification Status: {rel_data['verified']}\n")
            f.write(f"Last Updated: {rel_data['last_updated']}\n")
            f.write("-" * 20 + "\n")
    
    print(f"[+] Correlation report saved to {report_file}")

def main():
    # Paths
    db_path = "./enhanced_results/python_correlation/correlations.db"
    output_dir = "./enhanced_results/python_correlation"
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Setup database
    print("[+] Setting up database...")
    conn = setup_database(db_path)
    
    # Add entities and create relationships
    print("[+] Adding entities and creating relationships...")
    add_entities(conn, ADDRESS, SUSPECTS)
    create_relationships(conn, ADDRESS, SUSPECTS)
    
    # Generate report
    print("[+] Generating correlation report...")
    generate_correlation_report(conn, output_dir)
    
    conn.close()
    print(f"[+] Correlation complete. Results in {output_dir}")

if __name__ == "__main__":
    main()
