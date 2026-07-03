"""Dry-run-first Atlas Cloud patient education visual generator.

This helper creates safe, de-identified patient education image or video prompts,
fetches the live Atlas Cloud model schema, and prepares a schema-valid request.
It submits generation jobs only when --submit is passed.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


MEDIA_BASE_URL = "https://api.atlascloud.ai/api/v1"
MODELS_URL = f"{MEDIA_BASE_URL}/models"
DEFAULT_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "openclaw-patient-education-visuals/1.0",
}
TERMINAL_STATUSES = {"completed", "succeeded", "failed"}


class VisualRequestError(RuntimeError):
    """Raised for expected validation and API failures."""


@dataclass(frozen=True)
class ModelChoice:
    model: str
    display_name: str
    model_type: str
    schema_url: str
    price: Any


def fetch_json(url: str, headers: dict[str, str] | None = None, timeout: int = 30) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={**DEFAULT_HEADERS, **(headers or {})})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise VisualRequestError(f"GET {url} failed with HTTP {exc.code}: {body}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise VisualRequestError(f"GET {url} failed: {exc}") from exc


def post_json(url: str, payload: dict[str, Any], api_key: str, timeout: int = 60) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            **DEFAULT_HEADERS,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise VisualRequestError(f"POST {url} failed with HTTP {exc.code}: {body}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise VisualRequestError(f"POST {url} failed: {exc}") from exc


def choose_model(model_type: str, keyword: str) -> ModelChoice:
    catalog = fetch_json(MODELS_URL)
    keyword_norm = keyword.lower()
    matches = []
    for item in catalog.get("data", []):
        if item.get("display_console") is not True or item.get("type") != model_type:
            continue
        haystack = " ".join(
            str(item.get(field, ""))
            for field in ("model", "displayName", "familyDisplayName", "profile", "tags")
        ).lower()
        if keyword_norm in haystack:
            matches.append(item)

    if not matches:
        raise VisualRequestError(f"No display-console {model_type} model matched keyword: {keyword}")

    selected = matches[0]
    schema_url = selected.get("schema")
    if not schema_url:
        raise VisualRequestError(f"Selected model {selected.get('model')} has no schema URL")

    return ModelChoice(
        model=selected["model"],
        display_name=selected.get("displayName") or selected["model"],
        model_type=selected["type"],
        schema_url=schema_url,
        price=selected.get("price"),
    )


def load_input_schema(choice: ModelChoice) -> tuple[dict[str, Any], list[str]]:
    schema = fetch_json(choice.schema_url)
    input_schema = schema.get("components", {}).get("schemas", {}).get("Input", {})
    properties = input_schema.get("properties", {})
    required = input_schema.get("required", [])
    if not properties:
        raise VisualRequestError(f"Schema for {choice.model} does not expose Input.properties")
    return properties, required


def parse_points(raw: str) -> list[str]:
    points = [item.strip() for item in raw.replace("\n", ";").split(";") if item.strip()]
    if not 3 <= len(points) <= 7:
        raise VisualRequestError("--points should contain 3 to 7 semicolon-separated education points")
    return points


def parse_extra_json(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise VisualRequestError(f"--extra-json must be valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise VisualRequestError("--extra-json must decode to a JSON object")
    return value


def build_prompt(topic: str, audience: str, objective: str, points: list[str], style: str) -> str:
    numbered_points = "; ".join(f"{index + 1}. {point}" for index, point in enumerate(points))
    return (
        "Create a de-identified patient education visual. "
        f"Topic: {topic}. Audience: {audience}. Objective: {objective}. "
        f"Learning points: {numbered_points}. "
        f"Visual style: {style}. "
        "Use plain language, calm clinical colors, accessible spacing, and clear icons. "
        "Do not include patient names, dates of birth, medical record numbers, addresses, or full dates. "
        "Do not diagnose, recommend treatment, or imply the visual represents any specific patient. "
        "Include this small footer text: Educational information only - follow your clinician's instructions."
    )


def build_request_body(
    choice: ModelChoice,
    properties: dict[str, Any],
    required: list[str],
    prompt: str,
    extra: dict[str, Any],
) -> dict[str, Any]:
    request_body: dict[str, Any] = {"model": choice.model}
    if "prompt" in properties:
        request_body["prompt"] = prompt
    elif "text" in properties:
        request_body["text"] = prompt
    else:
        raise VisualRequestError("Selected model schema has neither 'prompt' nor 'text'")

    allowed_fields = set(properties)
    ignored_fields = sorted(set(extra) - allowed_fields)
    for key, value in extra.items():
        if key in allowed_fields:
            request_body[key] = value

    missing = [field for field in required if field not in request_body and field != "model"]
    if missing:
        raise VisualRequestError(
            "Missing required schema fields: " + ", ".join(missing) + ". Pass them with --extra-json."
        )

    if ignored_fields:
        print(f"Ignored fields not present in the live schema: {', '.join(ignored_fields)}")

    return request_body


def submit_generation(choice: ModelChoice, request_body: dict[str, Any], api_key: str) -> str:
    if choice.model_type == "Image":
        endpoint = "generateImage"
    elif choice.model_type == "Video":
        endpoint = "generateVideo"
    else:
        raise VisualRequestError(f"Unsupported media model type: {choice.model_type}")

    result = post_json(f"{MEDIA_BASE_URL}/model/{endpoint}", request_body, api_key)
    prediction_id = result.get("data", {}).get("id")
    if not prediction_id:
        raise VisualRequestError(f"Generation response did not include data.id: {result}")
    return str(prediction_id)


def poll_prediction(
    prediction_id: str,
    api_key: str,
    interval_seconds: int = 5,
    max_attempts: int = 60,
) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {api_key}"}
    for attempt in range(1, max_attempts + 1):
        result = fetch_json(
            f"{MEDIA_BASE_URL}/model/prediction/{prediction_id}",
            headers=headers,
            timeout=30,
        )
        status = str(result.get("data", {}).get("status", ""))
        print(f"prediction={prediction_id} status={status} attempt={attempt}/{max_attempts}")
        if status in TERMINAL_STATUSES:
            return result
        time.sleep(interval_seconds)

    raise VisualRequestError(
        f"Prediction {prediction_id} did not reach a terminal status after {max_attempts} attempts"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a safe patient education visual request")
    parser.add_argument("--type", choices=["Image", "Video"], default="Image")
    parser.add_argument("--keyword", default="text-to-image", help="Keyword used to select a live model")
    parser.add_argument("--topic", required=True, help="Patient education topic")
    parser.add_argument("--audience", required=True, help="Intended audience")
    parser.add_argument("--objective", required=True, help="Education objective")
    parser.add_argument("--points", required=True, help="Semicolon-separated safe learning points")
    parser.add_argument("--style", default="clean clinic handout illustration", help="Visual style")
    parser.add_argument("--extra-json", help="Optional JSON object with schema-validated fields")
    parser.add_argument("--submit", action="store_true", help="Submit the request after review")
    parser.add_argument("--poll", action="store_true", help="Poll the submitted prediction")
    parser.add_argument("--poll-interval", type=int, default=5, help="Seconds between polling attempts")
    parser.add_argument("--max-poll-attempts", type=int, default=60, help="Maximum polling attempts")
    args = parser.parse_args()

    try:
        points = parse_points(args.points)
        prompt = build_prompt(args.topic, args.audience, args.objective, points, args.style)
        choice = choose_model(args.type, args.keyword)
        properties, required = load_input_schema(choice)
        request_body = build_request_body(
            choice=choice,
            properties=properties,
            required=required,
            prompt=prompt,
            extra=parse_extra_json(args.extra_json),
        )

        preview = {
            "selected_model": choice.__dict__,
            "schema_fields": sorted(properties),
            "required_fields": required,
            "prompt": prompt,
            "request_body": request_body,
            "submit": args.submit,
        }
        print(json.dumps(preview, indent=2, ensure_ascii=False))

        if not args.submit:
            print("Dry run only. Review for PHI, medical safety, schema fit, and cost before --submit.")
            return 0

        api_key = os.environ.get("ATLASCLOUD_API_KEY")
        if not api_key:
            raise VisualRequestError("Set ATLASCLOUD_API_KEY before using --submit.")

        prediction_id = submit_generation(choice, request_body, api_key)
        print(f"Submitted prediction: {prediction_id}")
        if args.poll:
            result = poll_prediction(
                prediction_id,
                api_key,
                interval_seconds=args.poll_interval,
                max_attempts=args.max_poll_attempts,
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except VisualRequestError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
