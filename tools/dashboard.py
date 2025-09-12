#!/usr/bin/env python3
"""
Dashboard avançado para gerenciamento do repositório DevOps-Lab-AWS
"""
import os
import subprocess
import webbrowser
import shutil
from datetime import datetime
from collections import Counter
import plotext as plt
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box
from rich.progress import track, Progress
from rich.tree import Tree

console = Console()
MAIN_BRANCH = "main"
PASTAS = ["app", "infra", "tests", "docs", ".github/workflows"]
REPO_URL = "https://github.com/mirelabsp/DevOps-Lab-AWS.git"

def run_cmd(cmd, capture_output=False, ignore_errors=False):
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=capture_output, text=True)
        return result
    except subprocess.CalledProcessError as e:
        if ignore_errors:
            # Retorna objeto com interface similar ao CompletedProcess
            class ErrorResult:
                def __init__(self, e):
                    self.returncode = e.returncode
                    self.stdout = e.stdout if hasattr(e, 'stdout') else ""
                    self.stderr = e.stderr if hasattr(e, 'stderr') else ""
            return ErrorResult(e)
        else:
            raise e

def get_status():
    changes = run_cmd("git status --porcelain", capture_output=True).stdout.strip()
    local_commits = run_cmd(f"git log origin/{MAIN_BRANCH}..HEAD --oneline", 
                           capture_output=True, ignore_errors=True).stdout.strip()
    remote_commits = run_cmd(f"git log HEAD..origin/{MAIN_BRANCH} --oneline", 
                            capture_output=True, ignore_errors=True).stdout.strip()
    local_branches = run_cmd("git branch --format='%(refname:short)'", 
                            capture_output=True).stdout.strip().splitlines()
    remote_branches = run_cmd("git branch -r", capture_output=True).stdout.strip().splitlines()
    last_commits = run_cmd("git log -5 --oneline --decorate", capture_output=True).stdout.strip()
    return {
        "changes": changes,
        "local_commits": local_commits.splitlines() if local_commits else [],
        "remote_commits": remote_commits.splitlines() if remote_commits else [],
        "local_branches": local_branches,
        "remote_branches": [b.strip() for b in remote_branches if '->' not in b],
        "last_commits": last_commits
    }

def draw_dashboard(status):
    table = Table(title="📊 STATUS DO REPOSITÓRIO", box=box.DOUBLE_EDGE)
    table.add_column("Item", style="cyan", no_wrap=True)
    table.add_column("Status", style="magenta")
    table.add_row("Alterações não commitadas", "[red]Sim[/red]" if status["changes"] else "[green]Não[/green]")
    table.add_row("Commits locais não enviados", str(len(status["local_commits"])))
    table.add_row("Commits remotos não aplicados", str(len(status["remote_commits"])))
    table.add_row("Branches locais", ", ".join(status["local_branches"][:5]) + 
                 ("..." if len(status["local_branches"]) > 5 else ""))
    table.add_row("Branches remotas", ", ".join(status["remote_branches"][:3]) + 
                 ("..." if len(status["remote_branches"]) > 3 else ""))
    panel_commits = Panel(f"[yellow]{status['last_commits']}[/yellow]", 
                         title="📝 Últimos 5 commits", style="blue")
    return table, panel_commits

def criar_pastas():
    for pasta in track(PASTAS, description="Criando/atualizando pastas..."):
        os.makedirs(pasta, exist_ok=True)
        gitkeep = os.path.join(pasta, ".gitkeep")
        if not os.path.exists(gitkeep):
            open(gitkeep, "w").close()
    console.print(Panel("📂 Estrutura de pastas criada/atualizada.", style="green"))

def organizar_estrutura():
    console.print(Panel("🔄 Organizando estrutura do projeto...", style="cyan"))
    
    duplicate_path = "DevOps-Lab-AWS/DevOps-Lab-AWS"
    if os.path.exists(duplicate_path) and os.path.isdir(duplicate_path):
        console.print("Removendo pasta duplicada...")
        try:
            shutil.rmtree(duplicate_path)
        except Exception as e:
            console.print(f"❌ Erro ao remover pasta duplicada: {e}", style="red")
    
    test_files = [f for f in os.listdir('.') if f.startswith('arquivo_teste') or f.startswith('teste')]
    for test_file in test_files:
        console.print(f"Movendo {test_file}...")
        os.makedirs("tests", exist_ok=True)
        try:
            shutil.move(test_file, "tests/")
        except Exception as e:
            console.print(f"❌ Erro ao mover {test_file}: {e}", style="red")
    
    console.print("Criando estrutura de diretórios...")
    for pasta in [".github/workflows", "docs", "app", "infra", "tests", "tools"]:
        gitkeep_path = os.path.join(pasta, ".gitkeep")
        os.makedirs(pasta, exist_ok=True)
        if not os.path.exists(gitkeep_path):
            try:
                open(gitkeep_path, "w").close()
            except Exception as e:
                console.print(f"❌ Erro ao criar {gitkeep_path}: {e}", style="red")
    
    console.print(Panel("✅ Estrutura organizada com sucesso!", style="green"))

def atualizar_readme():
    conteudo = f"""# DevOps Lab AWS
Projeto laboratorial integrando GitHub, Docker, Terraform, Jenkins e Postman.

### Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
- Estrutura de pastas organizada automaticamente ✅
- Dashboard de gerenciamento integrado ✅
"""
    try:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(conteudo)
        console.print(Panel("📝 README.md atualizado.", style="green"))
    except Exception as e:
        console.print(f"❌ Erro ao atualizar README: {e}", style="red")

def atualizar_gitignore():
    conteudo = """__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
node_modules/
*.tfstate
.terraform/
.DS_Store
Thumbs.db
.vscode/
.idea/
*.log
.env
"""
    try:
        with open(".gitignore", "w", encoding="utf-8") as f:
            f.write(conteudo)
        console.print(Panel("⚙️ .gitignore atualizado.", style="green"))
    except Exception as e:
        console.print(f"❌ Erro ao atualizar .gitignore: {e}", style="red")

def sync_repo():
    try:
        run_cmd(f"git checkout {MAIN_BRANCH}")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Erro ao fazer checkout: {e}", style="red")
        return
    
    changes = run_cmd("git status --porcelain", capture_output=True).stdout.strip()
    stash_created = False
    
    if changes:
        if Prompt.ask("Existem alterações não commitadas. Criar stash?", choices=["s","n"], default="s") == "s":
            stash_result = run_cmd("git stash", capture_output=True, ignore_errors=True)
            if "No local changes to save" not in stash_result.stdout:
                stash_created = True
                console.print("📦 Alterações guardadas no stash.", style="yellow")
    
    try:
        run_cmd(f"git pull origin {MAIN_BRANCH} --rebase")
        console.print("✅ Pull concluído.", style="green")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Conflito detectado! Resolva manualmente: {e}", style="red")
        return
    
    if stash_created:
        if Prompt.ask("Aplicar stash de volta?", choices=["s","n"], default="s") == "s":
            stash_result = run_cmd("git stash pop", capture_output=True, ignore_errors=True)
            if stash_result.returncode == 0:
                console.print("📦 Stash aplicado.", style="yellow")
            else:
                console.print("❌ Erro ao aplicar stash.", style="red")

def commit_changes():
    changes = run_cmd("git status --porcelain", capture_output=True).stdout.strip()
    if changes:
        msg = Prompt.ask("Digite a mensagem do commit")
        try:
            run_cmd("git add .")
            run_cmd(f'git commit -m "{msg}"')
            console.print("✅ Commit realizado!", style="green")
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Erro ao fazer commit: {e}", style="red")
    else:
        console.print("✅ Nenhuma alteração para commitar.", style="green")

def criar_branch_e_pr():
    changes = run_cmd("git status --porcelain", capture_output=True).stdout.strip()
    local_commits = run_cmd(f"git log origin/{MAIN_BRANCH}..HEAD --oneline", 
                           capture_output=True, ignore_errors=True).stdout.strip()
    if changes or local_commits:
        console.print("❌ Não é seguro criar branch/PR. Commit e push primeiro.", style="red")
        return
    
    branch_name = f"feature/auto-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    try:
        run_cmd(f"git checkout -b {branch_name}")
        run_cmd("git add .")
        run_cmd(f'git commit -m "chore: atualização automática em {branch_name}"')
        run_cmd(f"git push origin {branch_name}")
        
        user_repo = REPO_URL.replace("https://github.com/", "").replace(".git", "")
        pr_url = f"https://github.com/{user_repo}/compare/{MAIN_BRANCH}...{branch_name}?expand=1"
        console.print(Panel(f"🔗 PR disponível: {pr_url}", style="cyan"))
        webbrowser.open(pr_url)
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Erro ao criar branch/PR: {e}", style="red")

def sync_commits():
    status = get_status()
    success = True
    
    if status["local_commits"]:
        console.print(f"📤 Enviando {len(status['local_commits'])} commit(s) local(is)...", style="yellow")
        for commit in status["local_commits"]:
            console.print(f"  - {commit}", style="yellow")
        
        try:
            run_cmd(f"git push origin {MAIN_BRANCH}")
            console.print("✅ Commits locais enviados com sucesso!", style="green")
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Erro ao enviar commits locais: {e}", style="red")
            success = False
    
    if status["remote_commits"]:
        console.print(f"📥 Aplicando {len(status['remote_commits'])} commit(s) remoto(s)...", style="yellow")
        for commit in status["remote_commits"]:
            console.print(f"  - {commit}", style="yellow")
        
        try:
            run_cmd(f"git pull origin {MAIN_BRANCH} --rebase")
            console.print("✅ Commits remotos aplicados com sucesso!", style="green")
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Erro ao aplicar commits remotos: {e}", style="red")
            success = False
    
    return success

def plot_commits():
    try:
        branches = run_cmd("git branch --format='%(refname:short)'", 
                          capture_output=True).stdout.strip().splitlines()
        commits_count = []
        for b in branches:
            result = run_cmd(f"git rev-list --count {b}", 
                           capture_output=True, ignore_errors=True)
            count = result.stdout.strip()
            commits_count.append(int(count) if count.isdigit() else 0)
        
        plt.clear_data()
        plt.bar(branches, commits_count, color="cyan")
        plt.title("📊 Commits por Branch")
        plt.show()
    except Exception as e:
        console.print(f"❌ Erro ao gerar gráfico: {e}", style="red")
    input("Pressione Enter para voltar ao menu...")

def plot_commits_weekday():
    try:
        result = run_cmd("git log --pretty=%cd --date=format:'%a'", 
                       capture_output=True, ignore_errors=True)
        logs = result.stdout.strip().splitlines()
        counter = Counter(logs)
        dias = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        counts = [counter.get(d, 0) for d in dias]
        
        plt.clear_data()
        plt.bar(dias, counts, color="magenta")
        plt.title("📈 Commits por Dia da Semana")
        plt.show()
    except Exception as e:
        console.print(f"❌ Erro ao gerar gráfico: {e}", style="red")
    input("Pressione Enter para voltar ao menu...")

def plot_changes_per_folder():
    try:
        result = run_cmd("git status --porcelain", capture_output=True)
        status_lines = result.stdout.strip().splitlines()
        folders = []
        for line in status_lines:
            if len(line) > 3:
                path = line[3:]
                if "/" in path:
                    folders.append(path.split("/")[0])
                else:
                    folders.append(path)
        
        counter = Counter(folders)
        if counter:
            plt.clear_data()
            plt.bar(list(counter.keys()), list(counter.values()), color="yellow")
            plt.title("📂 Alterações por Pasta")
            plt.show()
        else:
            console.print("✅ Nenhuma alteração pendente.", style="green")
    except Exception as e:
        console.print(f"❌ Erro ao gerar gráfico: {e}", style="red")
    input("Pressione Enter para voltar ao menu...")

def gerenciador_arquivos():
    current_dir = os.getcwd()
    
    while True:
        console.clear()
        console.print(Panel(f"📁 Gerenciador de Arquivos - Diretório atual: {current_dir}", style="cyan"))
        
        try:
            tree = Tree("📦 Estrutura de Pastas")
            for root, dirs, files in os.walk(current_dir):
                if '.git' in root.split(os.sep):
                    continue
                    
                current_node = tree
                rel_path = os.path.relpath(root, current_dir)
                if rel_path == '.':
                    current_node = tree
                else:
                    parts = rel_path.split(os.sep)
                    for part in parts:
                        found = False
                        for child in current_node.children:
                            if str(child.label) == part:
                                current_node = child
                                found = True
                                break
                        if not found:
                            new_node = current_node.add(part)
                            current_node = new_node
                
                for file in files:
                    if not file.startswith('.'):
                        current_node.add(f"📄 {file}")
            
            console.print(tree)
        except Exception as e:
            console.print(f"❌ Erro ao gerar árvore: {e}", style="red")
        
        console.print("\nOpções:")
        console.print("[1] Navegar para pasta")
        console.print("[2] Voltar para pasta anterior")
        console.print("[3] Mover arquivo")
        console.print("[4] Copiar arquivo")
        console.print("[5] Deletar arquivo/pasta")
        console.print("[6] Criar pasta")
        console.print("[0] Voltar ao menu principal")
        
        escolha = Prompt.ask("Escolha a ação", choices=["1", "2", "3", "4", "5", "6", "0"], default="0")
        
        if escolha == "1":
            pasta = Prompt.ask("Digite o nome da pasta para navegar")
            new_path = os.path.join(current_dir, pasta)
            if os.path.isdir(new_path):
                current_dir = new_path
            else:
                console.print("❌ Pasta não encontrada!", style="red")
                input("Pressione Enter para continuar...")
                
        elif escolha == "2":
            parent_dir = os.path.dirname(current_dir)
            if parent_dir != current_dir:
                current_dir = parent_dir
            else:
                console.print("ℹ️  Já está no diretório raiz.", style="yellow")
                input("Pressione Enter para continuar...")
                
        elif escolha == "3":
            origem = Prompt.ask("Digite o nome do arquivo/pasta de origem")
            destino = Prompt.ask("Digite o caminho de destino")
            
            origem_path = os.path.join(current_dir, origem)
            destino_path = os.path.join(current_dir, destino)
            
            if os.path.exists(origem_path):
                try:
                    shutil.move(origem_path, destino_path)
                    console.print("✅ Arquivo/pasta movido com sucesso!", style="green")
                except Exception as e:
                    console.print(f"❌ Erro ao mover: {e}", style="red")
            else:
                console.print("❌ Arquivo/pasta de origem não encontrado!", style="red")
            input("Pressione Enter para continuar...")
            
        elif escolha == "4":
            origem = Prompt.ask("Digite o nome do arquivo/pasta de origem")
            destino = Prompt.ask("Digite o caminho de destino")
            
            origem_path = os.path.join(current_dir, origem)
            destino_path = os.path.join(current_dir, destino)
            
            if os.path.exists(origem_path):
                try:
                    if os.path.isdir(origem_path):
                        shutil.copytree(origem_path, destino_path)
                    else:
                        shutil.copy2(origem_path, destino_path)
                    console.print("✅ Arquivo/pasta copiado com sucesso!", style="green")
                except Exception as e:
                    console.print(f"❌ Erro ao copiar: {e}", style="red")
            else:
                console.print("❌ Arquivo/pasta de origem não encontrado!", style="red")
            input("Pressione Enter para continuar...")
            
        elif escolha == "5":
            alvo = Prompt.ask("Digite o nome do arquivo/pasta para deletar")
            alvo_path = os.path.join(current_dir, alvo)
            
            if os.path.exists(alvo_path):
                if Prompt.ask(f"Tem certeza que deseja deletar {alvo}?", choices=["s", "n"], default="n") == "s":
                    try:
                        if os.path.isdir(alvo_path):
                            shutil.rmtree(alvo_path)
                        else:
                            os.remove(alvo_path)
                        console.print("✅ Arquivo/pasta deletado com sucesso!", style="green")
                    except Exception as e:
                        console.print(f"❌ Erro ao deletar: {e}", style="red")
            else:
                console.print("❌ Arquivo/pasta não encontrado!", style="red")
            input("Pressione Enter para continuar...")
            
        elif escolha == "6":
            nome_pasta = Prompt.ask("Digite o nome da nova pasta")
            nova_pasta_path = os.path.join(current_dir, nome_pasta)
            
            try:
                os.makedirs(nova_pasta_path, exist_ok=True)
                console.print("✅ Pasta criada com sucesso!", style="green")
            except Exception as e:
                console.print(f"❌ Erro ao criar pasta: {e}", style="red")
            input("Pressione Enter para continuar...")
            
        elif escolha == "0":
            break

def mega_dashboard():
    while True:
        console.clear()
        try:
            status = get_status()
            table, panel_commits = draw_dashboard(status)
            console.print(table)
            console.print(panel_commits)
        except Exception as e:
            console.print(f"❌ Erro ao carregar status: {e}", style="red")
        
        console.print("\nMenu:")
        console.print("[1] Sincronizar repositório")
        console.print("[2] Criar/Atualizar pastas")
        console.print("[3] Organizar estrutura do projeto")
        console.print("[4] Atualizar README.md")
        console.print("[5] Atualizar .gitignore")
        console.print("[6] Commit alterações")
        console.print("[7] Criar branch + PR")
        console.print("[8] Sincronizar commits (push/pull)")
        console.print("[9] Gráfico: commits por branch")
        console.print("[10] Gráfico: commits por dia da semana")
        console.print("[11] Gráfico: alterações por pasta")
        console.print("[12] Gerenciador de arquivos")
        console.print("[0] Sair")
        
        try:
            escolha = Prompt.ask("Escolha a ação", 
                               choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "0"], 
                               default="0")
        except KeyboardInterrupt:
            console.print("\n👋 Saindo...", style="yellow")
            break
            
        if escolha == "1": 
            sync_repo()
        elif escolha == "2": 
            criar_pastas()
        elif escolha == "3": 
            organizar_estrutura()
        elif escolha == "4": 
            atualizar_readme()
        elif escolha == "5": 
            atualizar_gitignore()
        elif escolha == "6": 
            commit_changes()
        elif escolha == "7": 
            criar_branch_e_pr()
        elif escolha == "8": 
            sync_commits()
        elif escolha == "9": 
            plot_commits()
        elif escolha == "10": 
            plot_commits_weekday()
        elif escolha == "11": 
            plot_changes_per_folder()
        elif escolha == "12": 
            gerenciador_arquivos()
        elif escolha == "0":
            console.print("👋 Saindo...", style="yellow")
            break
        
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    try:
        mega_dashboard()
    except KeyboardInterrupt:
        console.print("\n👋 Programa interrompido pelo usuário", style="yellow")
    except Exception as e:
        console.print(f"❌ Erro fatal: {e}", style="red")
