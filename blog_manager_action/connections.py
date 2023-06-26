from github import Github
from github import Auth
import os

print(os.environ)

_auth = _gh = _repo = _last_commit = None


def get_auth():
    global _auth
    if not _auth:
        _auth = Auth.Token(os.environ.get("GITHUB_TOKEN"))
    return _auth


def get_github():
    global _gh
    if not _gh:
        _gh = Github(auth=get_auth())
    return _gh


def get_repo():
    global _repo
    if not _repo:
        _repo = get_github().get_repo(os.environ.get("GITHUB_REPO"))
    return _repo


def get_last_commit():
    global _last_commit
    if not _last_commit:
        _last_commit = get_repo().get_commit(sha=os.environ.get("GITHUB_SHA"))
    return _last_commit
