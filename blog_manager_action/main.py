from connections import get_last_commit
from extract_article_folders import extract_article_folders
from publish_article import publish_article

commit = get_last_commit()
print("extracting folders")
folders = extract_article_folders(commit.files)
print("out folders:", folders)

for folder in folders.keys():
    print("article folder:", folder)
    publish_article(folder, folders[folder])
