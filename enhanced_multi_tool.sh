#!/bin/bash

# Enhanced Multi-Tool Data Correlation and Linking Script
# Integrates multiple Kali tools with Maltego for comprehensive analysis

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_error() {
    echo -e "${RED}[-]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# Function to check if a tool is installed
check_tool() {
    if ! command -v "$1" &> /dev/null; then
        print_error "Tool $1 is not installed or not in PATH"
        return 1
    fi
    return 0
}

# Function to run multiple tools in parallel
run_parallel_tools() {
    local target="$1"
    local output_dir="$2"
    
    print_status "Running tools in parallel for faster analysis..."
    
    # Create output directories
    mkdir -p "$output_dir"/{nmap,dnsrecon,fierce,amass,subfinder,assetfinder,httpx}
    
    # Run tools in background
    {
        print_info "Running Nmap..."
        nmap -sS -O -A -T4 "$target" > "$output_dir/nmap/nmap_$target.txt" 2>&1
        print_status "Nmap completed"
    } &
    
    {
        print_info "Running DNSRecon..."
        dnsrecon -d "$target" -t std,rvl,srv,axfr > "$output_dir/dnsrecon/dnsrecon_$target.txt" 2>&1
        print_status "DNSRecon completed"
    } &
    
    {
        print_info "Running Fierce..."
        fierce --domain "$target" > "$output_dir/fierce/fierce_$target.txt" 2>&1
        print_status "Fierce completed"
    } &
    
    {
        print_info "Running Amass..."
        amass enum -d "$target" -o "$output_dir/amass/amass_$target.txt" 2>&1
        print_status "Amass completed"
    } &
    
    {
        print_info "Running Subfinder..."
        subfinder -d "$target" -o "$output_dir/subfinder/subfinder_$target.txt" 2>&1
        print_status "Subfinder completed"
    } &
    
    {
        print_info "Running Assetfinder..."
        assetfinder "$target" > "$output_dir/assetfinder/assetfinder_$target.txt" 2>&1
        print_status "Assetfinder completed"
    } &
    
    # Wait for all background jobs to complete
    wait
    
    print_status "All parallel tools completed"
}

# Function to run additional reconnaissance
run_additional_recon() {
    local target="$1"
    local output_dir="$2"
    
    print_status "Running additional reconnaissance..."
    
    # Check for subdomains with httpx
    if [ -f "$output_dir/subfinder/subfinder_$target.txt" ]; then
        print_info "Checking subdomain HTTP status..."
        cat "$output_dir/subfinder/subfinder_$target.txt" | httpx -silent -status-code -title > "$output_dir/httpx/httpx_$target.txt" 2>&1
    fi
    
    # Run whatweb for web technology detection
    if command -v whatweb &> /dev/null; then
        print_info "Running WhatWeb..."
        whatweb "$target" > "$output_dir/whatweb_$target.txt" 2>&1
    fi
    
    # Run dirb for directory discovery
    if command -v dirb &> /dev/null; then
        print_info "Running Dirb..."
        dirb "http://$target" > "$output_dir/dirb_$target.txt" 2>&1
    fi
}

# Function to correlate data from multiple sources
correlate_data() {
    local target="$1"
    local output_dir="$2"
    
    print_status "Correlating data from multiple sources..."
    
    # Create correlation directory
    mkdir -p "$output_dir/correlation"
    
    # Extract unique domains/IPs from all sources
    {
        # From nmap
        [ -f "$output_dir/nmap/nmap_$target.txt" ] && grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' "$output_dir/nmap/nmap_$target.txt" || true
        
        # From subfinder
        [ -f "$output_dir/subfinder/subfinder_$target.txt" ] && cat "$output_dir/subfinder/subfinder_$target.txt" || true
        
        # From amass
        [ -f "$output_dir/amass/amass_$target.txt" ] && cat "$output_dir/amass/amass_$target.txt" || true
        
        # From assetfinder
        [ -f "$output_dir/assetfinder/assetfinder_$target.txt" ] && cat "$output_dir/assetfinder/assetfinder_$target.txt" || true
        
    } | sort -u > "$output_dir/correlation/all_domains_ips.txt"
    
    # Extract emails from all sources
    {
        find "$output_dir" -name "*.txt" -exec grep -hoE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' {} \; 2>/dev/null || true
    } | sort -u > "$output_dir/correlation/all_emails.txt"
    
    # Create summary report
    cat > "$output_dir/correlation/summary.txt" << EOF
Multi-Tool Analysis Summary for $target
======================================
Generated: $(date)

Domains/IPs found: $(wc -l < "$output_dir/correlation/all_domains_ips.txt")
Emails found: $(wc -l < "$output_dir/correlation/all_emails.txt")

Top Domains/IPs:
$(head -20 "$output_dir/correlation/all_domains_ips.txt")

Emails found:
$(cat "$output_dir/correlation/all_emails.txt")

Tool Results:
$(find "$output_dir" -name "*.txt" -exec basename {} \; | sort)
EOF
    
    print_status "Correlation completed. Summary saved to $output_dir/correlation/summary.txt"
}

# Function to create Maltego input files
create_maltego_files() {
    local target="$1"
    local output_dir="$2"
    
    print_status "Creating Maltego import files..."
    
    mkdir -p "$output_dir/maltego"
    
    # Create CSV for Maltego import
    {
        echo "Entity,Type,Source"
        
        # Add domains
        while IFS= read -r domain; do
            echo "$domain,Domain,MultiTool"
        done < "$output_dir/correlation/all_domains_ips.txt"
        
        # Add emails
        while IFS= read -r email; do
            echo "$email,Email,MultiTool"
        done < "$output_dir/correlation/all_emails.txt"
        
    } > "$output_dir/maltego/entities.csv"
    
    print_status "Maltego import file created: $output_dir/maltego/entities.csv"
}

# Function to launch Maltego with prepared data
launch_maltego() {
    local output_dir="$1"
    
    print_status "Launching Maltego..."
    
    if command -v maltego &> /dev/null; then
        print_info "Starting Maltego. Import the CSV file: $output_dir/maltego/entities.csv"
        maltego &
    else
        print_error "Maltego not found. Please install it first."
    fi
}

# Function to run the Python correlation script
run_python_correlator() {
    local target="$1"
    local output_dir="$2"
    
    print_status "Running Python correlation script..."
    
    if [ -f "./multi_tool_linker.py" ]; then
        python3 ./multi_tool_linker.py "$target" -o "$output_dir/python_correlation"
    else
        print_warning "Python correlation script not found. Skipping..."
    fi
}

# Main function
main() {
    local target="$1"
    local output_dir="${2:-./enhanced_results}"
    
    if [ -z "$target" ]; then
        echo "Usage: $0 <target_domain> [output_directory]"
        echo "Example: $0 example.com ./results"
        exit 1
    fi
    
    print_status "Starting enhanced multi-tool analysis for $target"
    print_info "Output directory: $output_dir"
    
    # Check required tools
    local required_tools=("nmap" "dnsrecon" "fierce" "amass" "subfinder" "assetfinder" "httpx")
    local missing_tools=()
    
    for tool in "${required_tools[@]}"; do
        if ! check_tool "$tool"; then
            missing_tools+=("$tool")
        fi
    done
    
    if [ ${#missing_tools[@]} -gt 0 ]; then
        print_warning "Some tools are missing: ${missing_tools[*]}"
        print_info "Install missing tools with: sudo apt install ${missing_tools[*]}"
    fi
    
    # Create output directory
    mkdir -p "$output_dir"
    
    # Run analysis phases
    run_parallel_tools "$target" "$output_dir"
    run_additional_recon "$target" "$output_dir"
    correlate_data "$target" "$output_dir"
    create_maltego_files "$target" "$output_dir"
    run_python_correlator "$target" "$output_dir"
    
    print_status "Analysis complete!"
    print_info "Results saved to: $output_dir"
    print_info "Summary report: $output_dir/correlation/summary.txt"
    print_info "Maltego import file: $output_dir/maltego/entities.csv"
    
    # Ask if user wants to launch Maltego
    read -p "Launch Maltego now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        launch_maltego "$output_dir"
    fi
}

# Run main function with all arguments
main "$@"

