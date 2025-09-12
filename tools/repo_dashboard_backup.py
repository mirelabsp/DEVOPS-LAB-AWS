#!/usr/bin/env python3
"""
Dashboard para visualizar a estrutura do repositório
"""

import os
from pathlib import Path

def display_structure():
    """Exibe a estrutura do repositório de forma organizada"""
    repo_path = Path(__file__).parent.parent
    
    print("Estrutura do Repositório DEVOPS-LAB-AWS:")
    print("=" * 50)
    print("DEVOPS-LAB-AWS/")
    
    for root, dirs, files in os.walk(repo_path):
        # Ignorar diretórios ocultos e venv
        if any(part.startswith('.') for part in Path(root).parts) or 'venv' in Path(root).parts:
            continue
            
        rel_path = os.path.relpath(root, repo_path)
        if rel_path == '.':
            continue
            
        indent_level = rel_path.count(os.sep)
        indent = "  " * indent_level
        
        print(f"{indent}{os.path.basename(root)}/")
        
        # Listar arquivos
        for file in files:
            if not file.startswith('.'):
                print(f"{indent}  ├── {file}")
        
        # Listar diretórios
        for dir_name in dirs:
            if not dir_name.startswith('.'):
                print(f"{indent}  └── {dir_name}/")

if __name__ == "__main__":
    display_structure()
