# Commit Analysis

This script analyzes commits in a GitHub repository and generates per-author statistics of added and deleted lines.

## Features

- Count added and deleted lines per author
- Skipping initial commit without parent and merge commits (non-original)
- Filter by date range (`--since` / `--until`) across all or specific branches
- Analyze a single commit by hash (`--commit`)
- Skip merge commits and initial commits
- Filter by file extensions (default: `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.svelte`, `.html`, `.css`; configurable in script)
- Support for private repositories via GitHub token in an adjacent `.env` file

## Requirements

- Python 3.6+
- GitPython

### Install dependency

```bash
pip install GitPython
```

## Setup

1. Clone or download this repository.
2. (Optional) Create a `.env` file in the project root and add your GitHub token:
   ```
   GITHUB_TOKEN=your_personal_access_token
   ```
3. Ensure the script is executable and run it with Python 3.

## Usage

### Analyze by date range (all branches)

```bash
python3 commit_analysis.py \
  --repo-url https://github.com/user/repo \
  --since 2025-05-01 \
  --until 2025-06-01
```

### Analyze by date range (specific branch)

```bash
python3 commit_analysis.py \
  --repo-url https://github.com/user/repo \
  --since 2025-05-01 \
  --until 2025-06-01 \
  --branch feature/my-branch
```

### Analyze a single commit

```bash
python3 commit_analysis.py \
  --repo-url https://github.com/user/repo \
  --commit e5c97cbc1318297461f7286bb53d873fa5752b54
```

## Customizing File Extensions

Modify the `ALLOWED_EXTENSIONS` set in `commit_analysis.py` to include or exclude file types as needed.

## License

This project is licensed under the MIT License. 
