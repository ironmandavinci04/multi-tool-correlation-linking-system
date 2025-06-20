# Multi-Tool Data Correlation and Linking System

A comprehensive system that integrates multiple Kali Linux tools with Maltego for advanced data correlation and entity linking.

## Features

- **Multi-Tool Integration**: Combines TheHarvester, Recon-ng, SpiderFoot, Nmap, Amass, Subfinder, and more
- **Parallel Processing**: Runs multiple tools simultaneously for faster analysis
- **Data Correlation**: Automatically finds relationships between discovered entities
- **Maltego Integration**: Creates importable data for Maltego visualization
- **SQLite Database**: Stores entities and relationships for analysis
- **Comprehensive Reporting**: Generates detailed reports with correlation data

## Files Overview

### Core Scripts
- `multi_tool_linker.py` - Python-based correlation engine with database storage
- `enhanced_multi_tool.sh` - Shell script for parallel tool execution
- `config.json` - Configuration file for customizing tool behavior

### Output Structure
```
results/
├── maltego/
│   ├── entities.csv         # CSV import file for Maltego
│   └── entities.mtgx        # XML transform data
├── correlation/
│   ├── summary.txt          # Analysis summary
│   ├── all_domains_ips.txt  # Discovered domains/IPs
│   └── all_emails.txt       # Discovered email addresses
├── harvester/
├── recon-ng/
├── spiderfoot/
├── nmap/
├── amass/
├── subfinder/
└── python_correlation/
    └── correlations.db      # SQLite database
```

## Quick Start

### 1. Run Basic Analysis
```bash
# Simple domain analysis
./enhanced_multi_tool.sh example.com

# Specify output directory
./enhanced_multi_tool.sh example.com ./my_results
```

### 2. Run Python Correlation Engine
```bash
# Advanced correlation with database storage
python3 multi_tool_linker.py example.com -o ./results
```

### 3. Import into Maltego
1. Open Maltego
2. Create new graph
3. Import entities from `results/maltego/entities.csv`
4. Use transform data from `results/maltego/entities.mtgx`

## Tool Requirements

### Installed Reconnaissance Tools

#### 1. nmap (v7.80)
Network mapper and security scanner
```bash
# Basic scan
nmap -sV -p- example.com

# Aggressive scan with OS detection
nmap -A example.com

# Quick scan
nmap -T4 -F example.com
```

#### 2. dnsrecon (v0.9.0)
DNS enumeration and recon tool
```bash
# Standard scan
dnsrecon -d example.com -t std

# Zone transfer
dnsrecon -d example.com -t axfr

# Brute force subdomains
dnsrecon -d example.com -t brt -D /path/to/wordlist.txt
```

#### 3. subfinder (v2.7.1)
Modern subdomain discovery tool
```bash
# Basic subdomain enumeration
subfinder -d example.com

# Silent output with only subdomains
subfinder -d example.com -silent

# Use custom resolvers
subfinder -d example.com -r resolvers.txt
```

#### 4. assetfinder
Find domains and subdomains related to a domain
```bash
# Basic usage
assetfinder example.com

# Save results to file
assetfinder example.com > domains.txt
```

#### 5. spiderfoot
OSINT automation tool
```bash
# Start the web interface
python3 /usr/share/spiderfoot/sf.py -l 127.0.0.1:5001

# Access web interface at http://127.0.0.1:5001
```

#### 6. recon-ng
Web reconnaissance framework
```bash
# Start recon-ng
/usr/share/recon-ng/recon-ng

# Inside recon-ng:
workspaces create example
modules search
modules load recon/domains-hosts/google_site_web
```

### Tool Verification
To verify all tools are properly installed:
```bash
echo "Testing tools:" && \
echo -n "nmap: " && nmap -V | head -n1 && \
echo -n "dnsrecon: " && dnsrecon -v | head -n1 && \
echo -n "subfinder: " && subfinder -version && \
echo -n "assetfinder: " && which assetfinder && \
echo -n "spiderfoot: " && ls /usr/share/spiderfoot/sf.py && \
echo -n "recon-ng: " && ls /usr/share/recon-ng/recon-ng
```

## Configuration

Edit `config.json` to customize:

### Tool Settings
```json
{
    "tools": {
        "theharvester": {
            "enabled": true,
            "sources": "all",
            "timeout": 300
        }
    }
}
```

### Correlation Parameters
```json
{
    "correlation": {
        "confidence_threshold": 0.6,
        "relationship_types": [
            "domain_association",
            "email_domain"
        ]
    }
}
```

## Advanced Usage

### Custom Analysis Workflow
```bash
# 1. Run reconnaissance phase
./enhanced_multi_tool.sh target.com ./results

# 2. Run correlation analysis
python3 multi_tool_linker.py target.com -o ./results/correlation

# 3. Launch Maltego for visualization
maltego &
```

### Database Queries
```python
import sqlite3

# Connect to correlation database
conn = sqlite3.connect('./results/correlations.db')
cursor = conn.cursor()

# Query entities by confidence
cursor.execute("""
    SELECT name, type, confidence 
    FROM entities 
    WHERE confidence > 0.8 
    ORDER BY confidence DESC
""")

results = cursor.fetchall()
for entity in results:
    print(f"{entity[0]} ({entity[1]}) - {entity[2]}")
```

### Custom Maltego Transforms

The system creates XML transform data that can be imported into Maltego:

1. Open Maltego Transform Manager
2. Import transform set from `results/maltego/entities.mtgx`
3. Configure transform properties as needed

## Correlation Engine

The Python correlation engine finds relationships such as:

- **Email-Domain**: Links email addresses to their domains
- **Subdomain-Parent**: Connects subdomains to parent domains
- **IP-Domain**: Associates IP addresses with domains
- **Cross-Tool**: Correlates findings across different tools

### Confidence Scoring
- **0.8+**: High confidence (multiple tool confirmation)
- **0.6-0.7**: Medium confidence (single tool, good pattern)
- **0.4-0.5**: Low confidence (weak pattern match)

## Output Analysis

### Summary Report
Check `results/correlation/summary.txt` for:
- Total entities discovered
- Entity breakdown by type
- Top domains/IPs
- Email addresses found

### Database Analysis
Use SQLite browser or custom queries on `correlations.db` for:
- Entity relationships
- Confidence analysis
- Source tool comparison

## Troubleshooting

### Common Issues

1. **Tool not found errors**
   ```bash
   # Check tool installation
   which theharvester
   # Install if missing
   sudo apt install theharvester
   ```

2. **Permission errors**
   ```bash
   # Make scripts executable
   chmod +x enhanced_multi_tool.sh multi_tool_linker.py
   ```

3. **Timeout issues**
   - Increase timeout values in `config.json`
   - Run tools individually for debugging

4. **Maltego import issues**
   - Verify CSV format in `results/maltego/entities.csv`
   - Check entity type mappings in config

### Debug Mode
```bash
# Run with verbose output
bash -x enhanced_multi_tool.sh target.com

# Python debug
python3 -v multi_tool_linker.py target.com
```

## Security Notes

- Only use on domains you own or have permission to test
- Some tools may trigger security alerts
- Consider rate limiting for large-scale analysis
- Review tool configurations before running

## Contributing

To add new tools or correlation methods:

1. Add tool configuration to `config.json`
2. Implement tool runner in Python script
3. Add parsing method for tool output
4. Update correlation logic if needed

## License

This tool is for educational and authorized testing purposes only. Users are responsible for compliance with applicable laws and regulations.

