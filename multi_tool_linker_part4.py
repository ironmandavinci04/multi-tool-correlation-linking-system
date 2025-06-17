def run_analysis(self, target, suspect_names=None):
        """Run complete multi-tool analysis"""
        print(f"[+] Starting multi-tool analysis on {target}")
        print("[+] Output directory:", self.output_dir)
        
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
        print("[+] To visualize results:")
        print("    1. Open Maltego")
        print("    2. Import entities from:", os.path.join(self.output_dir, "maltego", "entities.mtgx"))
        print("    3. View correlation report:", os.path.join(self.output_dir, "correlation_report.txt"))

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
