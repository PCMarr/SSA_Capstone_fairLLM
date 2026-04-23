import sys
import subprocess
import importlib.metadata
from neo4j import GraphDatabase

#pip install neo4j if not already installed
try:
    importlib.metadata.version("neo4j")
    print("Package is installed") 
except importlib.metadata.PackageNotFoundError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'neo4j'])
    print("Package is not installed. Installing now...")

URI = "neo4j://localhost"
AUTH = ("admin", "password")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()

Username:
32cae82c
Password:
Ek04smctzAu7qCS-Aaa5EPNjei6TiG72Yh7ApNn9Bm0

