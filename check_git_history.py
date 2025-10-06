#!/usr/bin/env python
import subprocess
import sys

def run_git_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd='e:/Divy/Projects/GitHub/ycsmp')
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

print("=== Git Commit History ===")
print(run_git_command('git log --oneline -10'))

print("\n=== Finding 'Rejection email' commit ===")
rejection_commit = run_git_command('git log --oneline --grep="Rejection email"')
print(rejection_commit)

if rejection_commit:
    commit_hash = rejection_commit.split()[0]
    print(f"\n=== Changes in commit {commit_hash} ===")
    print(run_git_command(f'git show {commit_hash} --name-only'))
    
    print(f"\n=== Detailed changes in commit {commit_hash} ===")
    print(run_git_command(f'git show {commit_hash}'))
else:
    print("No commit found with 'Rejection email' message")