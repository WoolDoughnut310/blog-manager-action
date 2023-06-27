import requests
import os

from connections import get_github
from patterns import MARKDOWN_CODE_BLOCK
from urllib.parse import urlparse
from github import InputFileContent


def get_user_id():
    res = requests.get(
        "https://api.medium.com/v1/me",
        headers={
            "Authorization": f"Bearer {os.environ.get('MEDIUM_INTEGRATION_TOKEN')}"
        },
    )
    print("json for user request", res.json())
    res.raise_for_status()
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
        print("code match:", match)
        gist = user.create_gist(True, {match[1]: InputFileContent(match[2])})
        print("created gist!", gist)
        new_content = (
            new_content[: match.start()] + gist.html_url + new_content[match.end() :]
        )
        match = MARKDOWN_CODE_BLOCK.search(new_content)
    return new_content


def publish_medium(article, cover_image_url=None):
    user_id = get_user_id()
    
    def transform_content(article):
        content = gistify_code_blocks(article.content)
        if "medium_id" not in article.keys():
            content = f"# {article['title']}\n" + content

        if cover_image_url:
            content = f"![cover image]({cover_image_url})\n" + content

        if "canonical_url" in article.keys():
            content += create_canonical_reference(article["canonical_url"])

        return content

    res = requests.post(
        f"https://api.medium.com/v1/users/{user_id}/posts",
        headers={
            "Authorization": f"Bearer {os.environ.get('MEDIUM_INTEGRATION_TOKEN')}"
        },
        json={
            "title": article["title"],
            "contentFormat": "markdown",
            "content": transform_content(article),
            "tags": article.get("tags", []),
            "canonicalUrl": canonical_url,
            # change to public
            "publishStatus": "draft",
        },
    )
    print("response:", res.json())

    json = res.json()

    if json.get("errors") and len(json["errors"]) > 0:
        exit(json["errors"][0]["message"])

    return json["data"]["url"]
