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
                relationship_type = 'domain_association'
                if 'suspect' in (corr[2], corr[5]):
                    relationship_type = 'suspect_association'
                
                cursor.execute('''
                    INSERT OR IGNORE INTO relationships 
                    (entity1_id, entity2_id, relationship_type, source_tool, confidence)
                    VALUES (?, ?, ?, ?, ?)
                ''', (corr[0], corr[3], relationship_type, 'correlation_engine', 0.8))
                
                print(f"[+] Found correlation: {corr[1]} ({corr[2]}) -> {corr[4]} ({corr[5]})")
            except Exception as e:
                print(f"[-] Error storing correlation: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"[+] Found {len(correlations)} correlations")
        
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
