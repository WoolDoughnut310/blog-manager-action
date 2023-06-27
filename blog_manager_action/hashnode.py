import requests
import os


def publish_hashnode(article, cover_image_url=None):
    query = """mutation CreateStory($input: CreateStoryInput!) {
                createStory(input: $input) {
                    code
                    success
                    message
                }
            }"""

    if "hashnode_id" in article.keys():
        query = query.replace(
            "createStory(", f'updateStory(postId: "{article["hashnode_id"]}", '
        )

    variables = {
        "input": {
            "title": article["title"],
            "slug": article["slug"],
            "contentMarkdown": article.content,
            "tags": article.get("hashnode_tags", []),
            "isPartOfPublication": { "publicationId": os.environ.get("HASHNODE_PUBLICATION_ID") }
        }
    }

    if cover_image_url:
        variables["input"]["coverImageURL"] = cover_image_url

    res = requests.post(
        "https://api.hashnode.com",
        json={
            "query": query,
            "variables": variables,
        },
        headers={"Authorization": os.environ.get("HASHNODE_INTEGRATION_TOKEN")},
    )

    json = res.json()
    print("hashnode json", json)

    if json.get("errors") and len(json["errors"]) > 0:
        exit(", ".join([e["message"] for e in json["errors"]]))

    post = json["data"]["post"]

    return f'https://{os.environ.get("HASHNODE_HOSTNAME")}/{post["slug"]}'
