#!/usr/bin/env python3
"""
Script para mostrar informações básicas do repositório
"""

import os
import subprocess
from datetime import datetime

def get_git_info():
    """Obtém informações do Git"""
    try:
        branch = subprocess.check_output("git branch --show-current", shell=True, text=True).strip()
        commit = subprocess.check_output("git log -1 --oneline", shell=True, text=True).strip()
        return branch, commit
    except:
        return "N/A", "N/A"

def get_repo_size():
    """Calcula o tamanho do repositório"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk('.'):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def main():
    """Função principal"""
    branch, last_commit = get_git_info()
    repo_size = get_repo_size()
    
    print("📊 Informações do Repositório")
    print("=" * 40)
    print(f"📁 Diretório: {os.path.basename(os.getcwd())}")
    print(f"🌿 Branch: {branch}")
    print(f"🔨 Último commit: {last_commit}")
    print(f"📦 Tamanho: {repo_size / 1024:.1f} KB")
    print(f"🕐 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

if __name__ == "__main__":
    main()
