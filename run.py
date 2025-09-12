#!/usr/bin/env python3
"""
Script para executar a aplicação
"""
from app.main import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
