from fastapi import Request
from nanoid import generate as nanoid_generate

NANOID_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def generate_id(prefix: str):
    def generate_id_wrapper():
        return prefix + "_" + nanoid_generate(alphabet=NANOID_ALPHABET, size=32 - len(prefix))

    return generate_id_wrapper


def get_actor(request: Request):
    return request.state.actor if hasattr(request.state, "actor") else {"id": "unknown"}


def get_default_success_criteria():
    return (
        "Evaluate whether the REPLAYED response to each question matches the BASELINE"
        " response in the following categories: tone, intent, sentiment, and most importantly"
        " factual information. If any of these categories do not match then fail the test."
    )
