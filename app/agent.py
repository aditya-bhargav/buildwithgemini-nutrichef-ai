# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import json
import os
import re
import time
import urllib.parse
import urllib.request

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google import genai
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.cloud import firestore, storage
from google.genai import types

try:
    from .a2ui_utils import a2ui_callback
except ImportError:
    from a2ui_utils import a2ui_callback

MODEL = "gemini-3.8-flash"

# Hardcoded GCP project ID as required for Agent Platform compatibility
PROJECT_ID = "qwiklabs-gcp-04-e6962f2702e7"
BUCKET_NAME = "nutrichef-ai-media-e6962f27"
IMAGE_MODEL = "gemini-2.5-flash-image"
IMAGE_LOCATION = "us-central1"


def get_firestore_client() -> firestore.Client:
    """Initialize and return a Firestore client with the hardcoded project ID."""
    return firestore.Client(project=PROJECT_ID)


def search_recipes(
    query: str = "",
    max_calories: int = 0,
    min_protein: int = 0,
    dietary_tag: str = "",
) -> list[dict]:
    """Search and filter recipes in the Firestore catalog.

    Args:
        query: Optional search keyword to match against title, description, or ingredients.
        max_calories: Optional maximum calories filter (0 means no limit).
        min_protein: Optional minimum protein in grams filter (0 means no minimum).
        dietary_tag: Optional dietary tag to filter by (e.g., 'vegan', 'high-protein', 'gluten-free', 'pescatarian').

    Returns:
        A list of matching recipe summary dictionaries.
    """
    db = get_firestore_client()
    docs = db.collection("recipes").stream()
    results = []

    q_lower = query.lower().strip()
    tag_lower = dietary_tag.lower().strip()

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id

        # Check calorie limit
        if max_calories > 0 and data.get("calories", 0) > max_calories:
            continue

        # Check protein minimum
        if min_protein > 0 and data.get("protein_g", 0) < min_protein:
            continue

        # Check dietary tag
        if tag_lower:
            tags = [t.lower() for t in data.get("dietary_tags", [])]
            if not any(tag_lower in t for t in tags):
                continue

        # Check query match in title, description, or ingredients
        if q_lower:
            text_corpus = f"{data.get('title', '')} {data.get('description', '')} {' '.join(data.get('ingredients', []))}".lower()
            if q_lower not in text_corpus:
                continue

        results.append({
            "id": data["id"],
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "calories": data.get("calories", 0),
            "protein_g": data.get("protein_g", 0),
            "carbs_g": data.get("carbs_g", 0),
            "fat_g": data.get("fat_g", 0),
            "dietary_tags": data.get("dietary_tags", []),
            "prep_time_minutes": data.get("prep_time_minutes", 0),
            "cook_time_minutes": data.get("cook_time_minutes", 0),
        })

    return results


def get_recipe_details(recipe_id_or_title: str) -> dict:
    """Retrieve full details for a recipe, including ingredients, step-by-step instructions, and macros.

    Args:
        recipe_id_or_title: The document ID or title of the recipe to look up.

    Returns:
        The full recipe dictionary with ingredients and instructions, or an error dictionary if not found.
    """
    db = get_firestore_client()
    doc_ref = db.collection("recipes").document(recipe_id_or_title)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data

    target = recipe_id_or_title.lower()
    for d in db.collection("recipes").stream():
        data = d.to_dict()
        if target in d.id.lower() or target in data.get("title", "").lower():
            data["id"] = d.id
            return data

    return {"error": f"Recipe '{recipe_id_or_title}' not found in catalog."}


def save_recipe(
    title: str,
    description: str,
    calories: int,
    protein_g: int,
    carbs_g: int,
    fat_g: int,
    prep_time_minutes: int,
    cook_time_minutes: int,
    dietary_tags: list[str],
    ingredients: list[str],
    instructions: list[str],
) -> str:
    """Save a new recipe to the Firestore database.

    Args:
        title: Title of the recipe.
        description: Short description of the dish.
        calories: Calories per serving.
        protein_g: Protein in grams per serving.
        carbs_g: Carbohydrates in grams per serving.
        fat_g: Fat in grams per serving.
        prep_time_minutes: Prep time in minutes.
        cook_time_minutes: Cooking time in minutes.
        dietary_tags: Tags such as ['high-protein', 'vegan', 'keto-friendly'].
        ingredients: List of ingredients with quantities.
        instructions: Step-by-step cooking instructions.

    Returns:
        Confirmation string with the created recipe ID.
    """
    db = get_firestore_client()
    doc_id = re.sub(r"[-\s]+", "-", re.sub(r"[^\w\s-]", "", title.lower())).strip("-")
    if not doc_id:
        doc_id = f"recipe-{int(datetime.datetime.now().timestamp())}"

    recipe_data = {
        "id": doc_id,
        "title": title,
        "description": description,
        "calories": calories,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
        "prep_time_minutes": prep_time_minutes,
        "cook_time_minutes": cook_time_minutes,
        "dietary_tags": dietary_tags,
        "ingredients": ingredients,
        "instructions": instructions,
    }

    db.collection("recipes").document(doc_id).set(recipe_data)
    return f"Successfully saved recipe '{title}' to Firestore with ID: {doc_id}"


def generate_recipe_visual(
    recipe_title_or_id: str,
    extra_details: str = "",
) -> dict:
    """Generate a photo of a recipe plating, upload it to Cloud Storage, and link it.

    Args:
        recipe_title_or_id: The title or ID of the recipe to visualize.
        extra_details: Optional specific visual instructions (e.g. 'rustic wooden table, natural sunlight').

    Returns:
        A dictionary with the generated image's public URL, recipe title, and status.
    """
    db = get_firestore_client()
    recipe_data = {}
    doc_id = re.sub(r"[-\s]+", "-", re.sub(r"[^\w\s-]", "", recipe_title_or_id.lower())).strip("-")

    # Look up recipe from Firestore to enrich the prompt
    doc = db.collection("recipes").document(doc_id).get()
    if doc.exists:
        recipe_data = doc.to_dict()
    else:
        # Check by title
        target = recipe_title_or_id.lower()
        for d in db.collection("recipes").stream():
            d_dict = d.to_dict()
            if target in d.id.lower() or target in d_dict.get("title", "").lower():
                recipe_data = d_dict
                doc_id = d.id
                break

    title = recipe_data.get("title", recipe_title_or_id)
    description = recipe_data.get("description", "")
    ingredients = recipe_data.get("ingredients", [])

    ingredients_summary = ", ".join(ingredients[:5]) if ingredients else ""
    prompt = (
        f"A beautifully plated, high-end culinary dish of {title}. "
        f"{description} Key ingredients: {ingredients_summary}. "
        f"{extra_details} "
        f"Professional food photography, top-down 45-degree angle, appetizing, soft natural lighting, Michelin star restaurant plating."
    )

    client = genai.Client(vertexai=True, project=PROJECT_ID, location=IMAGE_LOCATION)

    image_bytes = None
    mime_type = "image/png"
    last_error = None

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=IMAGE_MODEL,
                contents=prompt,
            )
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/png"
                    break
            if image_bytes:
                break
        except Exception as e:
            last_error = e
            time.sleep(2 * (attempt + 1))

    if not image_bytes:
        return {
            "error": f"Failed to generate image after retries: {last_error}",
            "recipe_id": doc_id,
            "title": title,
        }

    # Upload to Cloud Storage
    filename = f"recipes/{doc_id}.png"
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

    # Update recipe document in Firestore if it exists
    if doc_id:
        try:
            db.collection("recipes").document(doc_id).set(
                {"image_url": public_url}, merge=True
            )
        except Exception:
            pass

    return {
        "recipe_id": doc_id,
        "title": title,
        "image_url": public_url,
        "status": "success",
        "message": f"Successfully generated visual for '{title}' and published to {public_url}",
    }


def search_external_recipes(query: str) -> list[dict]:
    """Search for real recipes from the global culinary database (TheMealDB public API).

    Args:
        query: Recipe title, ingredient, or culinary keyword to search for (e.g. 'chicken', 'salad', 'salmon').

    Returns:
        A list of matching recipe dictionaries with title, category, cuisine origin, ingredients, and instructions.
    """
    api_key = os.getenv("THEMEALDB_API_KEY", "1")
    encoded_query = urllib.parse.quote(query.strip())
    url = f"https://www.themealdb.com/api/json/v1/{api_key}/search.php?s={encoded_query}"

    req = urllib.request.Request(url, headers={"User-Agent": "NutriChefAI/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return [{"error": f"Failed to fetch external recipes from TheMealDB: {e}"}]

    meals = data.get("meals")
    if not meals:
        return []

    results = []
    for meal in meals[:3]:
        ingredients = []
        for i in range(1, 21):
            ing = meal.get(f"strIngredient{i}")
            meas = meal.get(f"strMeasure{i}")
            if ing and ing.strip():
                if meas and meas.strip():
                    ingredients.append(f"{meas.strip()} {ing.strip()}")
                else:
                    ingredients.append(ing.strip())

        results.append({
            "title": meal.get("strMeal", ""),
            "category": meal.get("strCategory", ""),
            "cuisine": meal.get("strArea", ""),
            "instructions": meal.get("strInstructions", ""),
            "ingredients": ingredients,
            "source": "TheMealDB",
        })

    return results


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "NutriChef AI, a healthy cooking and macro concierge assistant. "
        "You help users eat healthy, hit their calorie and macro goals, and cook delicious meals "
        "using your internal Firestore catalog and the global TheMealDB culinary database."
    ),
    workflow_description=(
        "Analyze the user request, use your tools (search_recipes, get_recipe_details, "
        "save_recipe, search_external_recipes, generate_recipe_visual) to retrieve or store "
        "information, and return structured A2UI display cards when presenting recipes, food summaries, "
        "or meal recommendations."
    ),
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    tools=[search_recipes, get_recipe_details, save_recipe, generate_recipe_visual, search_external_recipes],
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
