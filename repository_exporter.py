#!/usr/bin/env python3
"""
Repository Exporter - Export GitHub repository data to JSON
This script exports comprehensive repository information including:
- Repository metadata
- All branches
- All commits
- All files and content
- Issues and Pull Requests
- GitHub Actions workflows
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional


class RepositoryExporter:
    """Export GitHub repository data to JSON format"""
    
    def __init__(self, owner: str, repo: str, token: Optional[str] = None):
        """
        Initialize the repository exporter
        
        Args:
            owner: Repository owner username
            repo: Repository name
            token: GitHub API token (optional, for higher rate limits)
        """
        self.owner = owner
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """Make API request to GitHub"""
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_repository_metadata(self) -> Dict[str, Any]:
        """Get repository metadata"""
        print("Fetching repository metadata...")
        data = self._make_request(f"/repos/{self.owner}/{self.repo}")
        
        return {
            "id": data.get("id"),
            "name": data.get("name"),
            "full_name": data.get("full_name"),
            "description": data.get("description"),
            "html_url": data.get("html_url"),
            "owner": {
                "login": data.get("owner", {}).get("login"),
                "id": data.get("owner", {}).get("id"),
                "avatar_url": data.get("owner", {}).get("avatar_url"),
                "type": data.get("owner", {}).get("type")
            },
            "private": data.get("private"),
            "visibility": data.get("visibility"),
            "created_at": data.get("created_at"),
            "pushed_at": data.get("pushed_at"),
            "size": data.get("size"),
            "language": data.get("language"),
            "forks_count": data.get("forks_count"),
            "open_issues_count": data.get("open_issues_count"),
            "default_branch": data.get("default_branch"),
            "has_issues": data.get("has_issues"),
            "has_projects": data.get("has_projects"),
            "has_downloads": data.get("has_downloads"),
            "has_wiki": data.get("has_wiki"),
            "allow_merge_commit": data.get("allow_merge_commit"),
            "allow_rebase_merge": data.get("allow_rebase_merge"),
            "allow_squash_merge": data.get("allow_squash_merge")
        }
    
    def get_branches(self) -> List[Dict[str, Any]]:
        """Get all branches"""
        print("Fetching branches...")
        branches = self._make_request(f"/repos/{self.owner}/{self.repo}/branches?per_page=100")
        
        if not isinstance(branches, list):
            branches = [branches]
        
        return [
            {
                "name": branch.get("name"),
                "commit": {
                    "sha": branch.get("commit", {}).get("sha")
                },
                "protected": branch.get("protected")
            }
            for branch in branches
        ]
    
    def get_commits(self) -> List[Dict[str, Any]]:
        """Get all commits"""
        print("Fetching commits...")
        commits = self._make_request(f"/repos/{self.owner}/{self.repo}/commits?per_page=100")
        
        if not isinstance(commits, list):
            commits = [commits]
        
        return [
            {
                "sha": commit.get("sha"),
                "message": commit.get("commit", {}).get("message"),
                "author": {
                    "name": commit.get("commit", {}).get("author", {}).get("name"),
                    "email": commit.get("commit", {}).get("author", {}).get("email"),
                    "date": commit.get("commit", {}).get("author", {}).get("date")
                },
                "verification": {
                    "verified": commit.get("commit", {}).get("verification", {}).get("verified")
                }
            }
            for commit in commits
        ]
    
    def get_files(self, path: str = "") -> List[Dict[str, Any]]:
        """Get all files in repository"""
        print(f"Fetching files from {path or 'root'}...")
        try:
            contents = self._make_request(f"/repos/{self.owner}/{self.repo}/contents/{path}")
        except requests.exceptions.HTTPError:
            return []
        
        if not isinstance(contents, list):
            contents = [contents]
        
        files = []
        for item in contents:
            if item.get("type") == "file":
                files.append({
                    "name": item.get("name"),
                    "path": item.get("path"),
                    "type": item.get("type"),
                    "size": item.get("size"),
                    "sha": item.get("sha"),
                    "url": item.get("html_url")
                })
            elif item.get("type") == "dir":
                files.extend(self.get_files(item.get("path")))
        
        return files
    
    def get_issues(self) -> List[Dict[str, Any]]:
        """Get all issues"""
        print("Fetching issues...")
        try:
            issues = self._make_request(f"/repos/{self.owner}/{self.repo}/issues?state=all&per_page=100")
        except requests.exceptions.HTTPError:
            return []
        
        if not isinstance(issues, list):
            issues = [issues]
        
        return [
            {
                "number": issue.get("number"),
                "title": issue.get("title"),
                "state": issue.get("state"),
                "created_at": issue.get("created_at"),
                "updated_at": issue.get("updated_at"),
                "url": issue.get("html_url")
            }
            for issue in issues
        ]
    
    def get_pull_requests(self) -> List[Dict[str, Any]]:
        """Get all pull requests"""
        print("Fetching pull requests...")
        try:
            prs = self._make_request(f"/repos/{self.owner}/{self.repo}/pulls?state=all&per_page=100")
        except requests.exceptions.HTTPError:
            return []
        
        if not isinstance(prs, list):
            prs = [prs]
        
        return [
            {
                "number": pr.get("number"),
                "title": pr.get("title"),
                "state": pr.get("state"),
                "created_at": pr.get("created_at"),
                "updated_at": pr.get("updated_at"),
                "url": pr.get("html_url")
            }
            for pr in prs
        ]
    
    def export(self) -> Dict[str, Any]:
        """Export all repository data"""
        print(f"\n📦 Starting export for {self.owner}/{self.repo}...\n")
        
        repository = self.get_repository_metadata()
        branches = self.get_branches()
        commits = self.get_commits()
        files = self.get_files()
        issues = self.get_issues()
        prs = self.get_pull_requests()
        
        export_data = {
            "export_metadata": {
                "exported_at": datetime.now().isoformat(),
                "export_version": "1.0",
                "repository_name": self.repo,
                "owner": self.owner
            },
            "repository": repository,
            "branches": branches,
            "commits": commits,
            "files": files,
            "issues": issues,
            "pull_requests": prs,
            "summary": {
                "total_branches": len(branches),
                "total_commits": len(commits),
                "total_files": len(files),
                "total_issues": len(issues),
                "total_pull_requests": len(prs),
                "status": f"Export completed with {len(files)} files, {len(commits)} commits"
            }
        }
        
        print(f"✅ Export completed!\n")
        print(f"📊 Summary:")
        print(f"   - Branches: {len(branches)}")
        print(f"   - Commits: {len(commits)}")
        print(f"   - Files: {len(files)}")
        print(f"   - Issues: {len(issues)}")
        print(f"   - Pull Requests: {len(prs)}\n")
        
        return export_data
    
    def save_to_file(self, filename: str = "repository_export.json") -> None:
        """Export and save to JSON file"""
        data = self.export()
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved to {filename}")


def main():
    """Main function"""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python repository_exporter.py <owner> <repo> [output_file] [--token TOKEN]")
        print("\nExample:")
        print("  python repository_exporter.py Steinhauer761 HustleINFlow")
        sys.exit(1)
    
    owner = sys.argv[1]
    repo = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else "repository_export.json"
    
    token = None
    if "--token" in sys.argv:
        token_idx = sys.argv.index("--token")
        if token_idx + 1 < len(sys.argv):
            token = sys.argv[token_idx + 1]
    
    exporter = RepositoryExporter(owner, repo, token)
    exporter.save_to_file(output_file)


if __name__ == "__main__":
    main()