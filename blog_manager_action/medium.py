import requests
import os

from connections import get_github
from patterns import MARKDOWN_CODE_BLOCK
from urllib.parse import urlparse


def get_user_id():
    res = requests.get(
        "https://api.medium.com/v1/me",
        headers={
            "Authorization": f"Bearer {os.environ.get('MEDIUM_INTEGRATION_TOKEN')}"
        },
    )
    res.raise_for_status()
    print("json for user request", res.json())
    return res.json()["data"]["id"]


def create_canonical_reference(url):
    if url == None:
        return ""
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.hostname}"
    return f"\n\n---\n\n*Originally published at [{base_url}]({url}).*"


def gistify_code_blocks(markdown):
    gh = get_github()
    user = gh.get_user()
    new_content = markdown
    match = MARKDOWN_CODE_BLOCK.search(new_content)

    while match != None:
        gist = user.create_gist(True, {match[1]: match[2]})
        new_content = (
            new_content[: match.start()] + gist.html_url + new_content[match.end() :]
        )
        match = MARKDOWN_CODE_BLOCK.search(new_content)


def publish_medium(article, cover_image_url=None, canonical_url=None):
    user_id = get_user_id()

    article.content = f"# {article['title']}\n" + article.content
    if cover_image_url:
        article.content = f"![cover image]({cover_image_url})\n" + article.content

    if canonical_url:
        article.content += create_canonical_reference(canonical_url)

    res = requests.post(
        f"https://api.medium.com/v1/users/{user_id}/posts",
        headers={
            "Authorization": f"Bearer {os.environ.get('MEDIUM_INTEGRATION_TOKEN')}"
        },
        json={
            "title": article["title"],
            "contentFormat": "markdown",
            "content": article.content,
            "tags": article["tags"],
            "canonicalUrl": canonical_url,
            # change to public
            "status": "draft",
        },
    )
    print("response:", res.json())

    json = res.json()

    if json.get("errors") and len(json["errors"] > 0):
        exit(json["errors"][0]["message"])

    data = json["data"]
    return (data["id"], data["url"])
