from connections import get_repo
import requests
import os
import mimetypes
import frontmatter
from hashnode import publish_hashnode
from medium import publish_medium
import re

COVER_IMAGE_NAME = "cover.png"


def get_image_links(files):
    urls = {}
    for file in files:
        file_type = mimetypes.guess_type(file.name)[0]
        if file_type == None or not file_type.startswith("image/"):
            continue

        # Upload file content to CDN
        res = requests.post(
            "https://api.imgbb.com/1/upload",
            {
                "key": os.environ.get("IMGBB_API_KEY"),
                "image": file.content,
            },
        )

        # Throw if status code != 200
        print("image link response", res.json())
        res.raise_for_status()
        urls[file.name] = res.json()["data"]["url"]
    return urls


def replace_image_links(markdown, images):
    new_content = markdown

    image_names = [re.escape(name) for name in images.keys()]

    MARKDOWN_IMAGE = re.compile(
        rf'!\[[^\]]*\]\(({"|".join(image_names)})\s*((?:\w+=)?"(?:.*[^"])")?\s*\)'
    )
    match = MARKDOWN_IMAGE.search(new_content)
    print("match", match)
    while match != None:
        # Replace URL
        new_content = (
            new_content[: match.start(1)]
            + images[match[1]]
            + new_content[match.end(1) :]
        )
        match = MARKDOWN_IMAGE.search(new_content)
    return new_content


def publish_article(folder):
    repo = get_repo()
    contents = repo.get_contents(folder)

    article_file = next(file for file in contents if file.name == "article.md")
    article = article_file.decoded_content.decode()

    # Upload all the images within the folder to the CDN
    images = get_image_links(contents)

    # Replace all image references with their uploaded CDN URLs
    article = replace_image_links(article, images)

    # Tag `.metadata` onto article, using frontmatter
    article = frontmatter.loads(article)

    # Publish to blogging platforms
    cover_image_url = images.get(COVER_IMAGE_NAME)

    hashnode_url = publish_hashnode(article, cover_image_url)
    print(f"Published to Hashnode at {hashnode_url}")
    print(f"::set-output name=hashnode_url::{hashnode_url}")

    medium_url = publish_medium(article, cover_image_url)
    print(f"Published to Medium at {medium_url}")
    print(f"::set-output name=medium_url::{medium_url}")

    article["is_published"] = True

    result = repo.update_file(
        f"{folder}/article.md",
        os.environ.get("CI_COMMIT_MESSAGE"),
        frontmatter.dumps(article),
        article_file.sha,
    )

    new_commit = result["commit"].sha

    # Push to remote
    head = repo.get_git_ref("heads/main")
    head.edit(new_commit)
