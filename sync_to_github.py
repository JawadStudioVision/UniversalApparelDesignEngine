import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_NAME = "UniversalApparelDesignEngine"
ORG_OR_USER = "JawadStudioVision"

def run_cmd(cmd, check=True):
    print(f"Running: {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    if res.stdout.strip():
        print(res.stdout.strip())
    if res.stderr.strip():
        print(res.stderr.strip())
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed with code {res.returncode}: {' '.join(cmd)}")
    return res

def sync_to_github(commit_message: str = "feat: initial open-source release of Universal Apparel Design Engine"):
    print(f"=== Syncing {REPO_NAME} to GitHub ===")

    # 1. Initialize git if not present
    git_dir = PROJECT_ROOT / ".git"
    if not git_dir.exists():
        run_cmd(["git", "init", "-b", "main"])
        run_cmd(["git", "config", "user.name", ORG_OR_USER])
        run_cmd(["git", "config", "user.email", f"260197497+{ORG_OR_USER}@users.noreply.github.com"])

    # 2. Check if GitHub remote repository exists, create if missing
    remote_check = subprocess.run(["git", "remote", "get-url", "origin"], cwd=PROJECT_ROOT, capture_output=True, text=True)
    if remote_check.returncode != 0:
        print("[GitHub] Creating remote repository on GitHub via gh CLI...")
        try:
            run_cmd([
                "gh", "repo", "create", f"{ORG_OR_USER}/{REPO_NAME}",
                "--public",
                "--description", "Autonomous, niche-agnostic commercial apparel generation, background extraction & QA engine for DTG/POD.",
                "--source=.",
                "--remote=origin"
            ])
        except Exception as e:
            print(f"[Notice] gh repo create fallback or repo may already exist: {e}")
            run_cmd(["git", "remote", "add", "origin", f"https://github.com/{ORG_OR_USER}/{REPO_NAME}.git"], check=False)

    # 3. Stage and commit
    run_cmd(["git", "add", "."])
    status = subprocess.run(["git", "status", "--porcelain"], cwd=PROJECT_ROOT, capture_output=True, text=True)
    if status.stdout.strip():
        run_cmd(["git", "commit", "-m", commit_message])
    else:
        print("Working tree clean, no new changes to commit.")

    # 4. Push to main
    print("[GitHub] Pushing to GitHub (origin/main)...")
    push_res = subprocess.run(["git", "push", "-u", "origin", "main"], cwd=PROJECT_ROOT, capture_output=True, text=True)
    print(push_res.stdout)
    if push_res.returncode != 0:
        print("[Notice] Push retry with branch tracking...")
        subprocess.run(["git", "push", "-f", "origin", "main"], cwd=PROJECT_ROOT, check=True)

    print(f"\n>>> Successfully synced {REPO_NAME} to https://github.com/{ORG_OR_USER}/{REPO_NAME}")

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "feat: initial open-source release of Universal Apparel Design Engine"
    sync_to_github(msg)
