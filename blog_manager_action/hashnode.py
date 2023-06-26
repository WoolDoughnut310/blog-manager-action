import requests
import os


def publish_hashnode(article, cover_image_url=None):
    query = """mutation CreateStory($title: String!, $slug: String, $contentMarkdown: String!, $coverImageURL: String, $tags: [TagInput]) {
                createStory(input: { title: ${title}, contentMarkdown: ${content}, tags: [] }) {
                    code,
                    success,
                    message
                }
            }"""

    if "hashnode_id" in article.keys():
        query = query.replace(
            "createStory(", f'updateStory(postId: "{article["hashnode_id"]}", '
        )

    variables = {
        "title": article["title"],
        "slug": article["slug"],
        "contentMarkdown": article.content,
        "tags": article["tags"],
    }

    if cover_image_url:
        variables["coverImageURL"] = cover_image_url

    res = requests.post(
        "https://api.hashnode.com",
        {
            "query": query,
            "variables": variables,
        },
        headers={"Authorization": os.environ.get("HASHNODE_INTEGRATION_TOKEN")},
    )

    json = res.json()

    if json.errors and len(json["errors"]) > 0:
        exit(", ".join([e["message"] for e in json["errors"]]))

    post = json["post"]

    return (
        post["cuid"],
        f'https://{os.environ.get("HASHNODE_HOSTNAME")}/{post["slug"]}',
    )
