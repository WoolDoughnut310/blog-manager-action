from connections import get_repo
from github import UnknownObjectException


def extract_article_folders(files):
    repo = get_repo()
    folders = []

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
                    folders.append(folder)
                    break
            except UnknownObjectException:
                pass

    return folders
