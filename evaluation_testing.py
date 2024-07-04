from src.core.utils import make_json_openai_request


def evaluate_against_baseline(
    success_criteria: str, baseline_conversation_json: dict, evaluation_conversation_json: dict
):
    system_role = (
        "You are a helpful assistant who is responsible for determining if a BASELINE matches the content of a TEST."
        " You must compare each response from the chatbot in the TEST conversation with the corresponding response in"
        " the BASELINE. If you cannot find a corresponding matching response, fail the test. Each response from the"
        " chatbot in TEST must meet the success criteria, or you will FAIL the test. Carefully reason through why the"
        " test passes or fails. Respond in JSON format, either as { pass: true } OR { pass: false, reason: REASON_HERE"
        " }, where REASON_HERE is a 2 sentence summary as to specifically why the test failed.\n\nThe success criteria for the"
        " conversation is: " + success_criteria
    )

    messages = [
        {"role": "system", "content": system_role},
        {
            "role": "user",
            "content": f"BASELINE: {baseline_conversation_json}\n\nTEST: {evaluation_conversation_json}",
        },
    ]

    return make_json_openai_request(messages)


SUCCESS_CRITERIA = (
    "Evaluate whether the REPLAYED response to each question matches the BASELINE"
    " response in the following categories: tone, intent, sentiment, and most importantly"
    " factual information. If any of these categories do not match then fail the test."
)

BASELINE_CONVERSATION_JSON = {
    "0": {
        "author": "user",
        "message": "Hello, what types of things can you help me with?",
    },
    "1": {
        "author": "bot",
        "message": "Hello! I'm here to help with a variety of customer service needs. Here are a few things I can assist you with:\nRefund Requests: If you need to request a refund for a purchase, I can guide you through the process.\nAccount Setup: If you're having trouble setting up your account, I can help you get everything up and running.\nPassword Resets: If you’ve forgotten your password or need to reset it, I can help you with that as well.\nFeel free to let me know how I can assist you today!",
    },
    "3": {
        "author": "user",
        "message": "How do I do a refund?",
    },
    "4": {
        "author": "bot",
        "message": "I can help you with that! To process a refund, I'll need a bit of information from you. Here are the steps we'll follow:\nPurchase Details: Provide the order number and the date of purchase.\nReason for Refund: Let me know why you are requesting a refund.\nPayment Method: Confirm the payment method you used for the purchase.\nOnce I have this information, I'll guide you through the next steps. Please provide the order number and any additional details you have.",
    },
    "5": {
        "author": "user",
        "message": "Okay. The order number is #19023284, I want the refund because the product didn't fit, and I purchased it last week on Monday.",
    },
    "6": {
        "author": "bot",
        "message": "Thank you for providing the details. Here’s a summary of your refund request:\nOrder Number: #19023284\nReason for Refund: Product didn't fit\nDate of Purchase: Last week on Monday\nI'll now process your refund request. This may involve a few steps, depending on our company’s policy:\nReturn Authorization: I will issue a return authorization if required.\nReturn Instructions: I'll provide instructions on how to return the item.\nRefund Processing: Once the item is returned, your refund will be processed.\nPlease confirm the payment method you used for this purchase, and I’ll proceed with the next steps.",
    },
}

EVALUATION_CONVERSATION_JSON = {
    "0": {"author": "user", "message": "Hello, what types of things can you help me with?"},
    "1": {
        "author": "bot",
        "message": "Hi! I'm here to assist you with a variety of customer service needs. Here are some things I can help you with:\nReturn Requests: If you need to request a return for a purchase, I can guide you through the process.\nAccount Setup: If you're having issues setting up your account, I can help you with that.\nPassword Updates: If you’ve forgotten your password or need to update it, I can assist with that too.\nPlease let me know how I can help you today!",
    },
    "3": {"author": "user", "message": "How do I do a refund?"},
    "4": {
        "author": "bot",
        "message": "I can assist you with that! To initiate a refund, I'll need some details from you. Here are the steps we’ll take:\nOrder Information: Provide the order number and the date of purchase.\nReason for Refund: Let me know why you’re requesting a refund.\nPreferred Refund Method: Confirm how you would like to receive your refund.\nOnce I have this information, I'll guide you through the next steps. Please share the order number and any other relevant details.",
    },
    "5": {
        "author": "user",
        "message": "Okay. The order number is #19023284, I want the refund because the product didn't fit, and I purchased it last week on Monday.",
    },
    "6": {
        "author": "bot",
        "message": "Thank you for providing the details. Here’s a summary of your refund request:\nOrder Number: #19023284\nReason for Refund: Product didn't fit\nDate of Purchase: Last week on Monday\nI'll now process your refund request. This may involve a few steps, depending on our policy:\nReturn Authorization: I'll issue a return authorization if required.\nReturn Instructions: I'll provide instructions on how to return the item.\nRefund Processing: Once we receive the item, your refund will be processed.\nPlease confirm how you would like to receive your refund, and I’ll proceed with the next steps.",
    },
}


response = evaluate_against_baseline(SUCCESS_CRITERIA, BASELINE_CONVERSATION_JSON, EVALUATION_CONVERSATION_JSON)

print(response)
