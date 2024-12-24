import os
import sys
import shutil
import subprocess
import re
from pathlib import Path
from typing import Optional
import venv
import stat

# Configuration
TEMPLATE_REPO = "https://github.com/bobbyhiddn/Flask2Fly.git"

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'

def print_status(message: str) -> None:
    print(f"{Colors.YELLOW}>>> {message}{Colors.NC}")

def print_success(message: str) -> None:
    print(f"{Colors.GREEN}✓ {message}{Colors.NC}")

def print_error(message: str) -> None:
    print(f"{Colors.RED}✗ {message}{Colors.NC}", file=sys.stderr)
    sys.exit(1)

def validate_inputs(project_name: str) -> None:
    if not project_name:
        print("Usage: setup.py <new_project_name> [target_directory]")
        print("Example: setup.py MyNewProject ./projects")
        sys.exit(1)

    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', project_name):
        print_error("Project name must start with a letter and contain only letters, numbers, hyphens, and underscores")

def setup_project_directory(project_dir: Path, project_name: str) -> Path:
    project_path = project_dir / project_name
    if project_path.exists():
        print_error(f"Directory {project_path} already exists")
    
    project_dir.mkdir(parents=True, exist_ok=True)
    return project_path

def rename_project_files(project_path: Path, project_name: str) -> None:
    """Rename the app_name directory and update references in files."""
    src_dir = project_path / "src"
    app_dir = src_dir / "app_name"

    if not src_dir.exists():
        print_error(f"Source directory not found at {src_dir}")

    if not app_dir.exists():
        print_error(f"App directory not found at {app_dir}")

    # Rename the app directory
    new_app_dir = src_dir / project_name
    if new_app_dir.exists():
        shutil.rmtree(new_app_dir)
    app_dir.rename(new_app_dir)

def update_configuration_files(project_path: Path, project_name: str) -> None:
    # Update fly.toml
    fly_toml = project_path / "fly.toml"
    if fly_toml.exists():
        try:
            with open(fly_toml, 'r', encoding='utf-8') as f:
                content = f.read()
            content = re.sub(r'^app = .*$', f"app = '{project_name}'", content, flags=re.MULTILINE)
            with open(fly_toml, 'w', encoding='utf-8') as f:
                f.write(content)
        except UnicodeDecodeError:
            print_status(f"Warning: Could not update {fly_toml} due to encoding issues")

    # Update docker-compose.yml
    docker_compose = project_path / "docker-compose.yml"
    if docker_compose.exists():
        try:
            with open(docker_compose, 'r', encoding='utf-8') as f:
                content = f.read()
            content = re.sub(r'^  [a-zA-Z0-9_-]*:', f"  {project_name}:", content, flags=re.MULTILINE)
            with open(docker_compose, 'w', encoding='utf-8') as f:
                f.write(content)
        except UnicodeDecodeError:
            print_status(f"Warning: Could not update {docker_compose} due to encoding issues")

    # Update workflow files
    workflows_dir = project_path / ".github" / "workflows"
    if workflows_dir.exists():
        for workflow in workflows_dir.glob("*.yml"):
            try:
                with open(workflow, 'r', encoding='utf-8') as f:
                    content = f.read()
                content = content.replace(
                    "flyctl deploy --remote-only",
                    f"flyctl deploy --remote-only --app {project_name}"
                )
                content = content.replace(
                    "flyctl secrets set",
                    f"flyctl secrets set --app {project_name} "
                )
                if "branches: [main]" not in content:
                    content = content.replace(
                        f"--app {project_name}",
                        f"--app dev-{project_name}"
                    )
                with open(workflow, 'w', encoding='utf-8') as f:
                    f.write(content)
            except UnicodeDecodeError:
                print_status(f"Warning: Could not update {workflow} due to encoding issues")

    # Update README.md
    readme = project_path / "README.md"
    if readme.exists():
        try:
            with open(readme, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace("Flask2Fly", project_name)
            with open(readme, 'w', encoding='utf-8') as f:
                f.write(content)
        except UnicodeDecodeError:
            print_status(f"Warning: Could not update {readme} due to encoding issues")

    # Update Dockerfile
    dockerfile = project_path / "Dockerfile"
    if dockerfile.exists():
        try:
            with open(dockerfile, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace(
                "src/app_name/static",
                f"src/{project_name}/static"
            )
            with open(dockerfile, 'w', encoding='utf-8') as f:
                f.write(content)
        except UnicodeDecodeError:
            print_status(f"Warning: Could not update {dockerfile} due to encoding issues")

    # Update templates
    template_dir = project_path / "src" / project_name / "templates"
    if template_dir.exists():
        for template in template_dir.glob("*.html"):
            try:
                with open(template, 'r', encoding='utf-8') as f:
                    content = f.read()
                content = content.replace("Flask2Fly", project_name)
                content = content.replace("flask2fly logo", f"{project_name} logo")
                if template.name == "index.html":
                    content = content.replace(
                        "Welcome to Flask2Fly",
                        f"Welcome to {project_name}"
                    )
                    content = content.replace(
                        "https://github.com/bobbyhiddn/Flask2Fly",
                        f"https://github.com/yourusername/{project_name}"
                    )
                with open(template, 'w', encoding='utf-8') as f:
                    f.write(content)
            except UnicodeDecodeError:
                print_status(f"Warning: Could not update {template} due to encoding issues")

    # Update core.py
    core_file = project_path / "src" / project_name / "core.py"
    if core_file.exists():
        try:
            with open(core_file, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace(
                "'site_name': 'Flask2Fly'",
                f"'site_name': '{project_name}'"
            )
            content = content.replace(
                'title="Welcome to Flask2Fly"',
                f'title="Welcome to {project_name}"'
            )
            content = content.replace(
                "- Flask2Fly",
                f"- {project_name}"
            )
            with open(core_file, 'w', encoding='utf-8') as f:
                f.write(content)
        except UnicodeDecodeError:
            print_status(f"Warning: Could not update {core_file} due to encoding issues")

    # Update fly_deploy.sh
    deploy_script = project_path / "utils" / "fly_deploy.sh"
    if deploy_script.exists():
        try:
            with open(deploy_script, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace(
                'grep -q "Flask2Fly"',
                f'grep -q "{project_name}"'
            )
            content = content.replace(
                'APP_URL="flask2fly.fly.dev"',
                f'APP_URL="{project_name}.fly.dev"'
            )
            content = content.replace("Flask2Fly", project_name)
            with open(deploy_script, 'w', encoding='utf-8') as f:
                f.write(content)
        except UnicodeDecodeError:
            print_status(f"Warning: Could not update {deploy_script} due to encoding issues")

def initialize_modules(project_path: Path) -> None:
    modules_dir = project_path / "src" / "modules"
    modules_dir.mkdir(parents=True, exist_ok=True)

    pages_dir = modules_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    # Initialize pages as a local Git repository
    subprocess.run(["git", "init"], cwd=pages_dir, check=True)
    
    # Create README.md
    readme_content = f"""# Pages Module

This module contains the pages and documentation for {project_path.name}.
It is initialized as a local Git repository that can be synchronized with a remote repository if desired.

## Directory Structure

```
pages/
├── docs/       # Project documentation
├── articles/   # Content articles
└── templates/  # Page templates
```

## Remote Repository Setup (Optional)

To synchronize with a remote repository:

1. Create a new repository on your preferred Git hosting service
2. Add the remote to this repository:
   ```bash
   cd src/modules/pages
   git remote add origin <your-repository-url>
   ```
3. Push your changes:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push -u origin main
   ```
"""
    (pages_dir / "README.md").write_text(readme_content, encoding='utf-8')

    # Create basic structure
    (pages_dir / "docs").mkdir(exist_ok=True)
    (pages_dir / "articles").mkdir(exist_ok=True)
    (pages_dir / "templates").mkdir(exist_ok=True)

    # Create .gitignore
    gitignore_content = """__pycache__/
*.py[cod]
*$py.class
.env
.venv
env/
venv/
.idea/
.vscode/
"""
    (pages_dir / ".gitignore").write_text(gitignore_content, encoding='utf-8')

    # Initial commit
    subprocess.run(["git", "add", "."], cwd=pages_dir, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial pages module setup"],
        cwd=pages_dir,
        env={**os.environ, 'GIT_AUTHOR_NAME': 'Setup Script', 'GIT_AUTHOR_EMAIL': 'setup@local'},
        check=True
    )

def setup_virtual_environment(project_path: Path) -> None:
    venv_path = project_path / "venv"
    venv.create(venv_path, with_pip=True)
    
    pip_path = venv_path / "bin" / "pip" if os.name != 'nt' else venv_path / "Scripts" / "pip"
    requirements_path = project_path / "src" / "requirements.txt"
    
    subprocess.run(
        [str(pip_path), "install", "-r", str(requirements_path)],
        check=True
    )

def setup_git_hooks(project_path: Path) -> None:
    hooks_dir = project_path / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    
    shutil.copy2(
        project_path / "utils" / "pre-push",
        hooks_dir / "pre-push"
    )
    (hooks_dir / "pre-push").chmod(0o755)

def initialize_project(project_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=project_path, check=True)
    
    env_file = project_path / ".env"
    env_file.touch()

    subprocess.run(
        ["python", "utils/flask_keygen.py"],
        cwd=project_path,
        check=True
    )

    setup_virtual_environment(project_path)
    setup_git_hooks(project_path)

def safe_remove_git_dir(path: Path) -> None:
    """Safely remove a git directory on Windows by first removing read-only attributes."""
    if not path.exists():
        return

    def on_rm_error(func, path, exc_info):
        # Make the directory/file writable and try again
        try:
            os.chmod(path, stat.S_IWRITE)
            os.unlink(path)
        except Exception:
            pass

    try:
        # First try to clean the git repo to remove locks
        try:
            subprocess.run(["git", "clean", "-fd"], cwd=path, check=False, capture_output=True)
            subprocess.run(["git", "gc"], cwd=path, check=False, capture_output=True)
        except Exception:
            pass

        # Try to remove the directory with error handler
        shutil.rmtree(path, onerror=on_rm_error)
        
        # If directory still exists, try force removal
        if path.exists():
            import stat
            for p in path.rglob('*'):
                try:
                    p.chmod(stat.S_IWRITE)
                except Exception:
                    pass
            shutil.rmtree(path, ignore_errors=True)
            
        # Final check and cleanup
        if path.exists():
            # If all else fails, try using system commands
            try:
                if os.name == 'nt':  # Windows
                    subprocess.run(['rmdir', '/S', '/Q', str(path)], check=False, capture_output=True)
                else:  # Unix-like
                    subprocess.run(['rm', '-rf', str(path)], check=False, capture_output=True)
            except Exception:
                pass

        if path.exists():
            print_status(f"Warning: Could not remove temporary directory {path}. You may want to remove it manually.")
    except Exception as e:
        print_status(f"Warning: Could not remove temporary directory {path}. You may want to remove it manually.")

def main() -> None:
    if len(sys.argv) < 2:
        print_error("Project name is required")
    
    project_name = sys.argv[1]
    project_dir = Path(sys.argv[2] if len(sys.argv) > 2 else ".")
    
    print_status(f"Starting project setup for {project_name}")
    
    validate_inputs(project_name)
    project_path = setup_project_directory(project_dir, project_name)
    
    print_status("Cloning Flask2Fly template...")
    
    # Create temporary directory for cloning
    temp_clone_path = project_dir / "temp_clone"
    subprocess.run(["git", "clone", TEMPLATE_REPO, str(temp_clone_path)], check=True)
    
    # Move contents to actual project directory
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Copy everything except .git
    for item in temp_clone_path.iterdir():
        if item.name != '.git':
            if item.is_dir():
                shutil.copytree(str(item), str(project_path / item.name), dirs_exist_ok=True)
            else:
                shutil.copy2(str(item), str(project_path))
    
    # Clean up temporary directory
    safe_remove_git_dir(temp_clone_path)
    
    # Change to project directory for remaining operations
    os.chdir(project_path)
    
    # Perform all updates
    rename_project_files(project_path, project_name)
    update_configuration_files(project_path, project_name)
    initialize_modules(project_path)
    initialize_project(project_path)
    
    print_success(f"Project '{project_name}' has been successfully created!")
    print_status("Next steps:")
    print_status("1. Review and update the .env file with your configuration")
    print_status("2. Review the generated fly.toml configuration")
    print_status("3. Run 'fly launch' to initialize your Fly.io application")
    print_status("4. Update the README.md with your project-specific information")

if __name__ == "__main__":
    main()