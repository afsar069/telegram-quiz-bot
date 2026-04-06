import json
import logging
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

LOGGER = logging.getLogger(__name__)
POST_DELAY_SECONDS = 2
MAX_RETRIES = 5


JSON_FILE = "american_literature_mcqs_1_to_50.json"
DEFAULT_JSON_FILE = "questions.json"

if len(sys.argv) > 1:
    json_file = sys.argv[1]
else:
    json_file = DEFAULT_JSON_FILE

if not os.path.exists(json_file):
    local_candidate = Path(__file__).with_name(json_file)
    if local_candidate.exists():
        json_file = str(local_candidate)
    else:
        print(f"ERROR: File not found: {json_file}")
        sys.exit(1)

print(f"Using JSON file: {json_file}")


def load_quiz_questions():
    with open(json_file, "r", encoding="utf-8") as file_handle:
        questions = json.load(file_handle)

    if not isinstance(questions, list) or not questions:
        raise ValueError(f"JSON file is empty or invalid: {json_file}")

    return questions


def validate_question(item, question_number):
    if not isinstance(item.get("options"), list):
        message = (
            f"Skipping question {question_number} due to invalid options."
        )
        LOGGER.warning(message)
        print(message)
        return False

    if not item["options"]:
        message = (
            f"Skipping question {question_number} due to invalid options."
        )
        LOGGER.warning(message)
        print(message)
        return False

    correct_option_index = item.get("correct_option_index")
    if not isinstance(correct_option_index, int):
        message = (
            f"Skipping question {question_number} due to invalid correct_option_index."
        )
        LOGGER.warning(message)
        print(message)
        return False

    if correct_option_index < 0 or correct_option_index >= len(item["options"]):
        message = (
            f"Skipping question {question_number} due to invalid correct_option_index."
        )
        LOGGER.warning(message)
        print(message)
        return False

    return True


def validate_quiz_questions(questions):
    valid_questions = []
    skipped_count = 0

    for index, item in enumerate(questions, start=1):
        if validate_question(item, index):
            valid_questions.append(item)
        else:
            skipped_count += 1

    return valid_questions, skipped_count


def build_poll_payload(channel_id, item, index, total_questions):
    options = item["options"]
    correct_option_id = item["correct_option_index"]

    return json.dumps(
        {
            "chat_id": channel_id,
            "question": f"Question {index}/{total_questions}: {item['question']}",
            "options": options,
            "type": "quiz",
            "correct_option_id": correct_option_id,
            "explanation": item["explanation"],
            "is_anonymous": True,
        }
    ).encode("utf-8")


def send_quiz_poll(bot_token, payload):
    url = f"https://api.telegram.org/bot{bot_token}/sendPoll"
    request = urllib.request.Request(url, data=payload, method="POST")
    request.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
        return json.loads(body)


def post_with_retry(bot_token, channel_id, item, message_number, total_questions):
    attempt = 0

    while attempt < MAX_RETRIES:
        attempt += 1
        try:
            payload = build_poll_payload(channel_id, item, message_number, total_questions)
            response = send_quiz_poll(bot_token, payload)
            if response.get("ok"):
                LOGGER.info("Quiz poll %s sent successfully.", message_number)
                return True

            description = response.get("description", "Unknown Telegram API error")
            LOGGER.error(
                "Quiz poll %s failed on attempt %s: %s",
                message_number,
                attempt,
                description,
            )
        except urllib.error.HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="replace")
            retry_after = None
            try:
                error_data = json.loads(response_body)
                retry_after = (
                    error_data.get("parameters", {}).get("retry_after")
                    if isinstance(error_data, dict)
                    else None
                )
                description = error_data.get("description", response_body)
            except json.JSONDecodeError:
                description = response_body or str(exc)

            LOGGER.error(
                "Quiz poll %s hit HTTP %s on attempt %s: %s",
                message_number,
                exc.code,
                attempt,
                description,
            )

            if exc.code == 429:
                wait_seconds = retry_after or 5
                LOGGER.warning(
                    "Rate limit reached for quiz poll %s. Waiting %s seconds before retry.",
                    message_number,
                    wait_seconds,
                )
                time.sleep(wait_seconds)
                continue

            return False
        except urllib.error.URLError as exc:
            LOGGER.error(
                "Quiz poll %s failed on attempt %s due to network error: %s",
                message_number,
                attempt,
                exc,
            )
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception(
                "Unexpected error while sending quiz poll %s on attempt %s: %s",
                message_number,
                attempt,
                exc,
            )

        if attempt < MAX_RETRIES:
            LOGGER.info(
                "Retrying quiz poll %s after %s seconds.",
                message_number,
                POST_DELAY_SECONDS,
            )
            time.sleep(POST_DELAY_SECONDS)

    LOGGER.error(
        "Quiz poll %s failed after %s attempts.", message_number, MAX_RETRIES
    )
    return False


def main():
    bot_token = os.getenv("BOT_TOKEN")
    channel_id = os.getenv("CHANNEL_ID")

    if not bot_token or not channel_id:
        raise SystemExit(
            "Missing environment variables. Please set BOT_TOKEN and CHANNEL_ID."
        )

    try:
        quiz_questions = load_quiz_questions()
    except FileNotFoundError as exc:
        raise SystemExit(f"Error: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Error: Failed to parse JSON file '{json_file}': {exc}") from exc
    except ValueError as exc:
        raise SystemExit(f"Error: {exc}") from exc

    print(f"Loaded {len(quiz_questions)} questions from JSON.")
    valid_questions, skipped_count = validate_quiz_questions(quiz_questions)

    if not valid_questions:
        raise SystemExit("Error: No valid questions found in the JSON file.")

    success_count = 0
    total_questions = len(valid_questions)

    for index, question in enumerate(valid_questions, start=1):
        was_sent = post_with_retry(
            bot_token, channel_id, question, index, total_questions
        )
        if was_sent:
            success_count += 1

        if index < total_questions:
            time.sleep(POST_DELAY_SECONDS)

    LOGGER.info(
        "Finished sending quiz. Successful messages: %s/%s",
        success_count,
        total_questions,
    )
    print(f"Successfully posted {success_count} questions.")
    print(f"Skipped {skipped_count} invalid questions.")


if __name__ == "__main__":
    main()
