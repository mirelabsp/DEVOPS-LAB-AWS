#!/usr/bin/env python3
"""
Script para visualizar informações do repositório DEVOPS-LAB-AWS
"""

import os
import json
from pathlib import Path

def get_repo_structure():
    """Obtém a estrutura do repositório"""
    repo_path = Path(__file__).parent.parent
    structure = {}
    
    for root, dirs, files in os.walk(repo_path):
        # Ignorar diretórios ocultos e venv
        if any(part.startswith('.') for part in Path(root).parts) or 'venv' in Path(root).parts:
            continue
            
        rel_path = os.path.relpath(root, repo_path)
        if rel_path == '.':
            rel_path = 'ROOT'
            
        structure[rel_path] = {
            'files': [f for f in files if not f.startswith('.')],
            'dirs': [d for d in dirs if not d.startswith('.') and d != 'venv']
        }
    
    return structure

def display_structure():
    """Exibe a estrutura do repositório de forma organizada"""
    structure = get_repo_structure()
    
    print("Estrutura do Repositório DEVOPS-LAB-AWS:")
    print("=" * 50)
    
    for path, content in structure.items():
        indent_level = path.count(os.sep) if path != 'ROOT' else 0
        indent = "  " * indent_level
        
        if path == 'ROOT':
            print("DEVOPS-LAB-AWS/")
        else:
            print(f"{indent}{os.path.basename(path)}/")
        
        # Listar arquivos
        for file in content['files']:
            print(f"{indent}  ├── {file}")
        
        # Listar diretórios
        for i, dir_name in enumerate(content['dirs']):
            prefix = "  └──" if i == len(content['dirs']) - 1 and not content['files'] else "  ├──"
            print(f"{indent}{prefix} {dir_name}/")

if __name__ == "__main__":
    display_structure()
