import argparse
import tempfile
import os
from datetime import datetime
from git import Repo
from collections import defaultdict

ALLOWED_EXTENSIONS = {'.py', '.js', '.ts', '.jsx', '.tsx', 'svelte', '.html', '.css'}

# ALLOWED_EXTENSIONS = {
#     ".py", ".js", ".ts", ".jsx", ".tsx", ".svelte", ".java", ".cpp", ".h", ".hpp", ".cs", ".go",
#     ".rs", ".swift", ".kt", ".kts", ".scala", ".php", ".pl", ".pm",
#     ".sh", ".bash", ".ps1", ".r", ".tsv", ".lua", ".sql", ".html", ".css",
#     ".scss", ".xml", ".tex", ".Rmd", ".jl", ".m", ".mat", ".f", ".f90",
#     ".pas", ".pp", ".inc", ".asm", ".s", ".cob", ".cbl", ".vue", ".haml", ".slim",
#     ".j2", ".jinja", ".jinja2", ".tmpl", ".tpl", ".twig", ".liquid", ".hbs", ".pug",
# }

def is_target_file(file_path):
    return any(file_path.endswith(ext) for ext in ALLOWED_EXTENSIONS)

def analyze_commits_by_author(repo_url, since=None, until=None, commit_hash=None, branch=None):
    with tempfile.TemporaryDirectory() as temp_dir:
        # Load GitHub token from .env for private repo access
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if not line.strip() or line.startswith('#'): continue
                    key, _, value = line.strip().partition('=')
                    os.environ.setdefault(key, value)
        token = os.getenv('GITHUB_TOKEN')
        # Prepare clone URL (include token for private repos)
        clone_url = repo_url
        if token and repo_url.startswith('https://'):
            clone_url = repo_url.replace('https://', f'https://{token}@')
        print(f'📥 Cloning a repository in {temp_dir}...')
        repo = Repo.clone_from(clone_url, temp_dir)
        stats_by_author = defaultdict(lambda: {'add': 0, 'del': 0})

        commits = []
        if commit_hash:
            commits = [repo.commit(commit_hash)]
        else:
            # Use remote branch reference for specified branch
            rev = f'origin/{branch}' if branch else '--all'
            commits = list(repo.iter_commits(rev, since=since, until=until))

        for commit in commits:
            author = commit.author.name
            parents = commit.parents
            # Skipping initial commit without parent and merge commits (non-original)
            if len(parents) != 1:
                continue
            parent = parents[0]
            diff_index = parent.diff(commit, create_patch=True)

            for diff in diff_index:
                file_path = diff.b_path or diff.a_path
                if file_path and is_target_file(file_path):
                    try:
                        diff_text = diff.diff.decode('utf-8', errors='ignore')
                        for line in diff_text.splitlines():
                            if line.startswith('+') and not line.startswith('+++'):
                                stats_by_author[author]['add'] += 1
                            elif line.startswith('-') and not line.startswith('---'):
                                stats_by_author[author]['del'] += 1
                    except Exception as e:
                        print(f"⚠️ Error while parsing {file_path}: {e}")

        print("\n📊 Statistics by Authors:")
        print(f"{'User':20} | {'Add':>6} | {'Delete':>6} | {'Total':>6}")
        print("-" * 50)
        for author, stats in stats_by_author.items():
            total = stats['add'] + stats['del']
            print(f"{author:20} | {stats['add']:>6} | {stats['del']:>6} | {total:>6}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitHub Commit Analysis by Author")
    parser.add_argument('--repo-url', type=str, required=True, help='URL GitHub repository')
    parser.add_argument('--since', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--until', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--branch', type=str, help='Branch name for analysis (default: all branches)')
    parser.add_argument('--commit', type=str, help='Commit hash for analysis')

    args = parser.parse_args()

    if not args.commit and not (args.since and args.until):
        print("❌ Specify either --commit or both --since and --until")
    else:
        analyze_commits_by_author(
            repo_url=args.repo_url,
            since=args.since,
            until=args.until,
            commit_hash=args.commit,
            branch=args.branch
        )
