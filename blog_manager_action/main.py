from connections import get_last_commit
from extract_article_folders import extract_article_folders
from publish_article import publish_article

commit = get_last_commit()
folders = extract_article_folders(commit.files)

for folder in folders:
    publish_article(folder)
