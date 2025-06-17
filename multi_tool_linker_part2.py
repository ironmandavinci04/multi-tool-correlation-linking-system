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
