import json
from datetime import datetime, timezone
from statistics import median
from typing import List

import openai
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from sqlmodel import SQLModel
from sqlmodel.orm.session import Session

from src.models.db_schema import Bot
from src.settings import logger, settings

openai.api_key = settings.openai_api_key


def send_slack_alert(content: str):
    client = WebClient(token=settings.slack_token)
    channel_id = "C072QC03ETW"  # alerts channel

    try:
        client.chat_postMessage(
            channel=channel_id,
            text="",
            blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": content}}],
        )
    except SlackApiError as e:
        logger.exception(f"Error posting message: '{content}' to Slack: {e.response['error']}")


def calculate_performance_buckets(
    performance_data,
    comparison_data,
    num_buckets=10,
):
    # Will calculate the values of the buckets based on the data in the comparison
    # and then will put both performance and comparison data into the bucket grouping

    def get_bucket_ranges(comparison_data, num_buckets):
        sorted_data = sorted(comparison_data)
        n = len(sorted_data)
        lower_bound = sorted_data[int(0.1 * n)]
        upper_bound = sorted_data[int(0.9 * n)]

        bucket_size = (upper_bound - lower_bound) / (num_buckets - 2)
        buckets = [lower_bound + i * bucket_size for i in range(num_buckets - 1)]

        return [sorted_data[0]] + buckets + [sorted_data[-1]]

    def get_bucket_labels(bucket_ranges):
        labels = []
        for i in range(len(bucket_ranges) - 1):
            if i == 0:
                labels.append(f"<{bucket_ranges[i+1]:.0f}")
            elif i == len(bucket_ranges) - 2:
                labels.append(f"{bucket_ranges[i]:.0f}+")
            else:
                labels.append(f"{bucket_ranges[i]:.0f} - {bucket_ranges[i+1]:.0f}")
        return labels

    def count_in_buckets(data, bucket_ranges):
        counts = [0] * (len(bucket_ranges) - 1)
        for value in data:
            for i in range(len(bucket_ranges) - 1):
                if bucket_ranges[i] <= value < bucket_ranges[i + 1]:
                    counts[i] += 1
                    break
                elif value >= bucket_ranges[-2]:
                    counts[-1] += 1
                    break
        return counts

    bucket_ranges = get_bucket_ranges(comparison_data, num_buckets)
    bucket_labels = get_bucket_labels(bucket_ranges)
    performance_counts = count_in_buckets(performance_data, bucket_ranges)
    comparison_counts = count_in_buckets(comparison_data, bucket_ranges)

    return {
        "buckets": bucket_labels,
        "values": performance_counts,
        "comparison_values": comparison_counts,
    }


def calculate_boxplot_points(data: List[float]):
    # Sort the data
    sorted_data = sorted(data)
    n = len(sorted_data)

    # Calculate median
    median_value = median(sorted_data)

    # Properly determine lower and upper half, including median if necessary
    if n % 2 == 0:
        lower_half = [x for x in sorted_data if x <= median_value]
        upper_half = [x for x in sorted_data if x >= median_value]
    else:
        lower_half = [x for x in sorted_data if x < median_value]
        upper_half = [x for x in sorted_data if x > median_value]

    # calculate Q1 and Q3
    Q1 = median(lower_half or [median_value])
    Q3 = median(upper_half or [median_value])

    # Calculate IQR
    IQR = Q3 - Q1

    # Calculate bounds for outliers
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Separate outliers
    outliers = []
    for i, num in enumerate(sorted_data):
        if num < lower_bound or num > upper_bound:
            outliers.append(sorted_data.pop(i))

    # Determine boxplot values
    boxplot_values = [sorted_data[0], Q1, median_value, Q3, sorted_data[-1]]

    return (boxplot_values, outliers)


def _generic_has_permissions(actor: dict, bot: Bot, permissions: List[str]):
    if settings.environment == "local":
        return True

    # Check if actor is making change to personal
    actor_id = actor.get("id")
    org_id = actor.get("org_id")

    if not org_id and bot.user_id == actor_id:
        return True

    # get org memberships
    org_memberships = requests.get(
        f"https://api.clerk.com/v1/users/{actor_id}/organization_memberships",
        headers={"Authorization": f"Bearer {settings.clerk_api_key}"},
    ).json()

    for membership in org_memberships.get("data", {}):
        if not (membership["organization"]["id"] == bot.organization_id == org_id):
            continue

        # find correct membership and return if permissions exist
        return membership["role"] in permissions

    return False


def has_editor_permissions(actor: dict, bot: Bot):
    return _generic_has_permissions(actor, bot, permissions=["org:admin", "org:editor"])


def has_viewer_permissions(actor: dict, bot: Bot):
    return _generic_has_permissions(actor, bot, permissions=["org:admin", "org:editor", "org:viewer"])


def has_admin_permissions(actor: dict, bot: Bot):
    return _generic_has_permissions(actor, bot, permissions=["org:admin"])


def update_db_model_with_request(model: SQLModel, request: SQLModel, db_session: Session, actor: dict):
    request_data = request.model_dump()
    for key, value in request_data.items():
        if value is not None:
            setattr(model, key, value)

    if hasattr(model, "last_updated_at"):
        model.last_updated_at = datetime.now(timezone.utc)
    if hasattr(model, "last_updated_by"):
        model.last_updated_by = actor.get("id", "unknown")

    db_session.commit()

    return model


def billing_plan_to_evals_available(billing_plan: str):
    if billing_plan == "Free":
        return 100
    if billing_plan == "Personal":
        return 500
    if billing_plan == "Team":
        return 1000
    if billing_plan == "Enterprise":
        return 10000

    raise Exception(f"Invalid billing plan: {billing_plan}")


def make_json_openai_request(messages: list) -> dict:
    response = openai.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        temperature=0,
        messages=messages,
    )

    return json.loads(response.choices[0].message.content)


def parse_conversation_dict_from_html(html_blob: str, get_selector: bool = False, baseline: bool = False):
    # For now, stub out to reduce costs, get rid of baseline param when for real
    if baseline:
        resp = {
            "conversation": {
                0: {
                    "author": "user",
                    "message": (
                        "This is a baseline prompt\n What are 5 creative things I could do with my kids' art? I don't"
                        " want to throw them away, but it's also so much clutter"
                    ),
                },
                1: {
                    "author": "bot",
                    "message": (
                        "This is a baseline response\n Certainly! Here are five creative ideas for repurposing your"
                        " kids' art:\n\nCreate a Collage or Mosaic:\nSelect pieces of artwork that share similar colors"
                        " or themes.\nCut or tear the artwork into smaller pieces.\nArrange and glue the pieces onto a"
                        " canvas or poster board to create a vibrant collage or mosaic.\nCustomized Wrapping"
                        " Paper:\n\nScan or take photos of your kids' drawings.\nPrint the images onto large sheets of"
                        " paper.\nUse the customized wrapping paper for special occasions like birthdays or"
                        " holidays.\nTurn Art into Functional Items:\n\nTransform drawings into practical items such as"
                        " coasters, placemats, or mouse pads.\nScan or take pictures of the art and have them printed"
                        " onto fabric or transferred onto other materials.\nMake a Memory Book:\n\nCompile a scrapbook"
                        " or memory book showcasing your kids' artistic journey.\nInclude photographs, captions, and"
                        " anecdotes about each piece.\nThis way, you can keep a record of their artistic development"
                        " over time.\nDigital Gallery:\n\nScan or photograph the artwork and create a digital"
                        " gallery.\nCompile the images into a slideshow or digital photo frame.\nThis not only"
                        " preserves the art but also reduces physical clutter.\nRemember, the key is to find a balance"
                        " between keeping meaningful pieces and decluttering. You can also involve your kids in the"
                        " decision-making process to choose which pieces they value the most."
                    ),
                },
                3: {
                    "author": "user",
                    "message": "How about specifically for a watercolor painting? Give me one answer.",
                },
                4: {
                    "author": "bot",
                    "message": (
                        "Certainly! One specific idea for repurposing a watercolor painting is to turn it into a set of"
                        " customized note cards. Cut the watercolor painting into smaller sections, mount them on blank"
                        " cards, and use them as unique and artistic greeting cards or thank-you notes."
                    ),
                },
                5: {
                    "author": "user",
                    "message": "What about for a sculpture?",
                },
                6: {
                    "author": "bot",
                    "message": (
                        "For a sculpture, you can create a shadow box display. Select a shadow box or deep frame that"
                        " can accommodate the sculpture's dimensions.\n\nArrange the sculpture inside the shadow box,"
                        " ensuring that it is securely attached.\nAdd a background or base to enhance the sculpture's"
                        " appearance.\nYou can also include a small plaque with the artist's name and the sculpture's"
                        " title.\nThis way, you can showcase the sculpture as a piece of art while protecting it from"
                        " dust and damage."
                    ),
                },
                7: {
                    "author": "user",
                    "message": "Thank you! These are great ideas.",
                },
                8: {
                    "author": "bot",
                    "message": (
                        "You're welcome! I'm glad you found the ideas helpful. If you have any more questions or need"
                        " further inspiration, feel free to ask!"
                    ),
                },
            }
        }
    else:
        resp = {
            "conversation": {
                0: {
                    "author": "user",
                    "message": (
                        "This is an eval prompt\n What are 5 creative things I could do with my kids' art? I don't want"
                        " to throw them away, but it's also so much clutter."
                    ),
                },
                1: {
                    "author": "bot",
                    "message": (
                        "This is an eval response\n Certainly! Here are five creative ideas for repurposing your kids'"
                        " art:\n\nCreate a Collage or Mosaic:\nSelect pieces of artwork that share similar colors or"
                        " themes.\nCut or tear the artwork into smaller pieces.\nArrange and glue the pieces onto a"
                        " canvas or poster board to create a vibrant collage or mosaic.\nCustomized Wrapping"
                        " Paper:\n\nScan or take photos of your kids' drawings.\nPrint the images onto large sheets of"
                        " paper.\nUse the customized wrapping paper for special occasions like birthdays or"
                        " holidays.\nTurn Art into Functional Items:\n\nTransform drawings into practical items such as"
                        " coasters, placemats, or mouse pads.\nScan or take pictures of the art and have them printed"
                        " onto fabric or transferred onto other materials.\nMake a Memory Book:\n\nCompile a scrapbook"
                        " or memory book showcasing your kids' artistic journey.\nInclude photographs, captions, and"
                        " anecdotes about each piece.\nThis way, you can keep a record of their artistic development"
                        " over time.\nDigital Gallery:\n\nScan or photograph the artwork and create a digital"
                        " gallery.\nCompile the images into a slideshow or digital photo frame.\nThis not only"
                        " preserves the art but also reduces physical clutter.\nRemember, the key is to find a balance"
                        " between keeping meaningful pieces and decluttering. You can also involve your kids in the"
                        " decision-making process to choose which pieces they value the most."
                    ),
                },
                3: {
                    "author": "user",
                    "message": "How about specifically for a watercolor painting? Give me one answer.",
                },
                4: {
                    "author": "bot",
                    "message": (
                        "Certainly! One specific idea for repurposing a watercolor painting is to turn it into a set of"
                        " customized note cards. Cut the watercolor painting into smaller sections, mount them on blank"
                        " cards, and use them as unique and artistic greeting cards or thank-you notes."
                    ),
                },
                5: {
                    "author": "user",
                    "message": "What about for a sculpture?",
                },
                6: {
                    "author": "bot",
                    "message": (
                        "For a sculpture, you can create a shadow box display. Select a shadow box or deep frame that"
                        " can accommodate the sculpture's dimensions.\n\nArrange the sculpture inside the shadow box,"
                        " ensuring that it is securely attached.\nAdd a background or base to enhance the sculpture's"
                        " appearance.\nYou can also include a small plaque with the artist's name and the sculpture's"
                        " title.\nThis way, you can showcase the sculpture as a piece of art while protecting it from"
                        " dust and damage."
                    ),
                },
                7: {
                    "author": "user",
                    "message": "Thank you! These are great ideas.",
                },
                8: {
                    "author": "bot",
                    "message": (
                        "You're welcome! I'm glad you found the ideas helpful. If you have any more questions or need"
                        " further inspiration, feel free to ask!"
                    ),
                },
            }
        }

    if get_selector:
        resp["selector"] = "stubbed_selector"
    return resp

    system_role = (
        "You are helpful assistant who is responsible for parsing out a conversation from a blob of HTML. The user will"
        " send a raw HTML blob and you must respond only with a JSON object of the resulting conversation between a"
        " user and a chatbot. ONLY filter out the HTML tags and unecesarry artifacts of the page, do not condense or"
        " remove textual content from conversation. You may use the fact that this conversation is happening between a"
        " user and a chatbot to infer who sent which message if the HTML structure does not make it perfectly clear to"
        " you. The JSON format of your response must be in the format: { conversation: {0: {author: user, message:"
        " question}, 1: {author: bot, message: response}, ... } }"
    )
    if get_selector:
        system_role += (
            "\nYou want to save me time, tokens, and money for future requests to your API when passing HTML from this"
            " webpage. While the conversations will be different size/length with different content, HTML is structured"
            " where you can filter out a lot of unecesarry HTML from the blob I gave you regardless of the"
            " conversation. Therefore, you must also provide the query selector so when running"
            " `document.querySelectorAll(SELECTOR_HERE)` on the HTML blob, you will get all the necessary elements of"
            " the conversation. The JSON format is therefore the same as before, but with an additional key: {"
            " conversation: {...}, selector: SELECTOR_HERE }"
        )

    messages = [
        {
            "role": "system",
            "content": system_role,
        },
        {
            "role": "user",
            "content": html_blob,
        },
    ]
    return make_json_openai_request(messages)
