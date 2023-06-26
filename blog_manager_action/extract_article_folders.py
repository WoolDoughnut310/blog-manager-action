from connections import get_repo
from github import UnknownObjectException


def extract_article_folders(files):
    repo = get_repo()

    # Maps folder name to whether an article should be updated or not
    folders = {}

    for file in files:
        parts = file.filename.split("/")
        for i in range(-2, -len(parts) - 1, -1):
            folder = "/".join(parts[0 : i + 1])
            try:
                dir_contents = repo.get_contents(folder)

                # If `article.md` exists within the directory
                if any(
                    ["article.md" in file_content.name for file_content in dir_contents]
                ):
                    if parts[i] not in folders:
                        folders[folder] = True

                    # Create if `article.md` has been created
                    if not (
                        parts[-1] == "article.md" and file.additions == file.changes
                    ):
                        folders[folder] = False
                    break
            except UnknownObjectException:
                pass

    return folders
