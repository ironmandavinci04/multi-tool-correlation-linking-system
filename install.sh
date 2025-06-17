#!/bin/bash

# Multi-Tool Correlation System Installer
# Installs dependencies and sets up the environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        print_info "Run as regular user - sudo will be used when needed"
        exit 1
    fi
}

check_kali() {
    if ! grep -q "Kali" /etc/os-release 2>/dev/null; then
        print_warning "This installer is optimized for Kali Linux"
        print_info "Some tools may need manual installation on other distributions"
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

install_apt_packages() {
    print_status "Installing APT packages..."
    
    local packages=(
        "nmap"
        "dnsrecon"
        "fierce"
        "whatweb"
        "dirb"
        "recon-ng"
        "theharvester"
        "spiderfoot"
        "amass"
        "python3-pip"
        "sqlite3"
        "curl"
        "wget"
        "git"
    )
    
    sudo apt update
    
    for package in "${packages[@]}"; do
        if dpkg -l | grep -q "^ii.*$package"; then
            print_info "$package already installed"
        else
            print_status "Installing $package..."
            sudo apt install -y "$package" || print_warning "Failed to install $package"
        fi
    done
}

install_go_tools() {
    print_status "Installing Go-based tools..."
    
    # Check if Go is installed
    if ! command -v go &> /dev/null; then
        print_status "Installing Go..."
        sudo apt install -y golang-go
    fi
    
    # Set Go path if not set
    if [ -z "$GOPATH" ]; then
        export GOPATH=$HOME/go
        export PATH=$PATH:$GOPATH/bin
        echo 'export GOPATH=$HOME/go' >> ~/.bashrc
        echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.bashrc
        echo 'export GOPATH=$HOME/go' >> ~/.zshrc
        echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.zshrc
    fi
    
    # Create Go directories
    mkdir -p $GOPATH/bin
    
    # Install Go tools
    local go_tools=(
        "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
        "github.com/projectdiscovery/httpx/cmd/httpx@latest"
        "github.com/tomnomnom/assetfinder@latest"
    )
    
    for tool in "${go_tools[@]}"; do
        print_status "Installing $(basename $tool)..."
        go install -v "$tool" || print_warning "Failed to install $tool"
    done
}

install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Install Python packages
    pip3 install --user requests beautifulsoup4 lxml || print_warning "Some Python packages failed to install"
}

setup_maltego() {
    print_status "Setting up Maltego..."
    
    if command -v maltego &> /dev/null; then
        print_info "Maltego already installed"
    else
        print_warning "Maltego not found in PATH"
        print_info "Please install Maltego manually from: https://www.maltego.com/"
        print_info "Or install from Kali repos: sudo apt install maltego"
    fi
}

setup_permissions() {
    print_status "Setting up file permissions..."
    
    chmod +x multi_tool_linker.py
    chmod +x enhanced_multi_tool.sh
    chmod +x install.sh
    
    print_info "Made scripts executable"
}

setup_directories() {
    print_status "Creating working directories..."
    
    mkdir -p results
    mkdir -p logs
    mkdir -p temp
    
    print_info "Created working directories"
}

run_tests() {
    print_status "Running basic tool tests..."
    
    local tools_to_test=("nmap" "dnsrecon" "python3")
    local failed_tests=()
    
    for tool in "${tools_to_test[@]}"; do
        if command -v "$tool" &> /dev/null; then
            print_info "✓ $tool found"
        else
            print_error "✗ $tool not found"
            failed_tests+=("$tool")
        fi
    done
    
    if [ ${#failed_tests[@]} -gt 0 ]; then
        print_warning "Some tools failed tests: ${failed_tests[*]}"
        print_info "Please install missing tools manually"
    else
        print_status "All basic tools test passed!"
    fi
}

show_usage() {
    print_status "Installation complete!"
    echo
    print_info "Quick start:"
    echo "  ./enhanced_multi_tool.sh example.com"
    echo "  python3 multi_tool_linker.py example.com -o ./results"
    echo
    print_info "Documentation:"
    echo "  cat README.md"
    echo
    print_info "Configuration:"
    echo "  nano config.json"
    echo
}

main() {
    print_status "Multi-Tool Correlation System Installer"
    print_info "This will install dependencies and set up the environment"
    echo
    
    check_root
    check_kali
    
    install_apt_packages
    install_go_tools
    install_python_deps
    setup_maltego
    setup_permissions
    setup_directories
    run_tests
    
    show_usage
}

# Run installer
main "$@"

