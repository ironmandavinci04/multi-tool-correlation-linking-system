#!/bin/bash

# Example usage scripts for Multi-Tool Correlation System

echo "Multi-Tool Correlation System - Example Usage"
echo "============================================"
echo

echo "1. Basic domain analysis:"
echo "   ./enhanced_multi_tool.sh example.com"
echo

echo "2. Analysis with custom output directory:"
echo "   ./enhanced_multi_tool.sh target.com ./my_results"
echo

echo "3. Python correlation engine:"
echo "   python3 multi_tool_linker.py target.com -o ./results"
echo

echo "4. Run only specific phase:"
echo "   # Just reconnaissance"
echo "   nmap -sS -A target.com"
echo "   amass enum -d target.com"
echo "   subfinder -d target.com"
echo

echo "5. Database queries:"
echo "   sqlite3 results/correlations.db 'SELECT * FROM entities;'"
echo

echo "6. Custom configuration:"
echo "   # Edit config.json first"
echo "   nano config.json"
echo "   ./enhanced_multi_tool.sh target.com"
echo

echo "7. Debug mode:"
echo "   bash -x enhanced_multi_tool.sh target.com"
echo

echo "8. Maltego workflow:"
echo "   # 1. Run analysis"
echo "   ./enhanced_multi_tool.sh target.com"
echo "   # 2. Open Maltego"
echo "   maltego &"
echo "   # 3. Import results/maltego/entities.csv"
echo

echo "For more examples, see README.md"
echo

