#!/usr/bin/env python3
"""
Multi-Tool Data Correlation and Linking System
Integrates Maltego, TheHarvester, Recon-ng, SpiderFoot, and other tools
"""

import subprocess
import json
import csv
import xml.etree.ElementTree as ET
import argparse
import os
import sys
from datetime import datetime
import sqlite3
import re

class MultiToolLinker:
    def __init__(self, output_dir="./results"):
        self.output_dir = output_dir
        self.db_path = os.path.join(output_dir, "correlations.db")
        self.setup_directories()
        self.setup_database()
        
    def setup_directories(self):
        """Create output directories"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "maltego"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "harvester"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "recon-ng"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "spiderfoot"), exist_ok=True)
