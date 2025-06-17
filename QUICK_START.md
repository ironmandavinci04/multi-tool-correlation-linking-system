# Multi-Tool Correlation System - Quick Start

## 📦 Installation from ZIP

### 1. Extract the package
```bash
unzip multi_tool_correlation_system_v1.0.0.zip
cd multi_tool_correlation_system
```

### 2. Run the installer
```bash
./install.sh
```

### 3. Test the installation
```bash
./examples.sh
```

## 🚀 Quick Usage

### Basic Analysis
```bash
# Analyze a domain
./enhanced_multi_tool.sh example.com

# Advanced correlation
python3 multi_tool_linker.py example.com -o ./results
```

### Import into Maltego
1. Run analysis: `./enhanced_multi_tool.sh target.com`
2. Open Maltego
3. Import CSV: `results/maltego/entities.csv`
4. Use transforms: `results/maltego/entities.mtgx`

## 📁 Package Contents

- **Core Scripts**:
  - `multi_tool_linker.py` - Python correlation engine
  - `enhanced_multi_tool.sh` - Multi-tool shell script
  - `config.json` - Configuration file

- **Setup & Documentation**:
  - `install.sh` - Automated installer
  - `README.md` - Complete documentation
  - `examples.sh` - Usage examples
  - `requirements.txt` - Python dependencies
  - `LICENSE` - License information
  - `VERSION` - Version details

## 🛠️ System Requirements

- **OS**: Kali Linux 2023+ (recommended)
- **Python**: 3.8+
- **Tools**: Nmap, TheHarvester, Recon-ng, SpiderFoot, Amass, Subfinder
- **Optional**: Maltego CE/XL for visualization

## ⚡ Features

- ✅ Multi-tool OSINT integration
- ✅ Parallel processing for speed
- ✅ SQLite database correlation
- ✅ Maltego visualization ready
- ✅ Automated reporting
- ✅ Configurable workflows

## 🔧 Troubleshooting

**Missing tools?**
```bash
sudo apt update && sudo apt install nmap dnsrecon theharvester recon-ng spiderfoot amass
```

**Permission errors?**
```bash
chmod +x *.sh *.py
```

**Python dependencies?**
```bash
pip3 install -r requirements.txt
```

For detailed documentation, see `README.md`

---
**⚠️ Ethical Use Only**: This tool is for authorized testing and educational purposes only.

