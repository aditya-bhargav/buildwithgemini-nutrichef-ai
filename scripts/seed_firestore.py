#!/usr/bin/env python3
"""Seed initial recipe catalog in Firestore for NutriChef AI."""

from google.cloud import firestore

# Hardcoded project ID as required for Agent Platform compatibility
PROJECT_ID = "qwiklabs-gcp-04-e6962f2702e7"

SAMPLE_RECIPES = [
    {
        "id": "grilled-lemon-herb-salmon",
        "title": "Grilled Lemon Herb Salmon",
        "description": "Pan-seared salmon with garlic, fresh dill, lemon zest, and grilled asparagus.",
        "calories": 420,
        "protein_g": 38,
        "carbs_g": 8,
        "fat_g": 26,
        "prep_time_minutes": 15,
        "cook_time_minutes": 15,
        "dietary_tags": ["high-protein", "keto-friendly", "gluten-free", "pescatarian"],
        "ingredients": [
            "6 oz salmon fillet",
            "1 bunch asparagus",
            "1 tbsp olive oil",
            "1 lemon (juiced and zested)",
            "2 cloves garlic (minced)",
            "1 tbsp fresh dill (chopped)",
            "1/2 tsp salt",
            "1/4 tsp black pepper"
        ],
        "instructions": [
            "Preheat a grill pan or cast iron skillet over medium-high heat.",
            "Toss trimmed asparagus with half of the olive oil, salt, and pepper.",
            "Season salmon fillet with remaining oil, minced garlic, dill, lemon zest, salt, and pepper.",
            "Sear salmon skin-side down for 4-5 minutes, flip carefully and cook for 3-4 minutes until flaky.",
            "Grill asparagus alongside salmon for 4-5 minutes until tender-crisp.",
            "Squeeze fresh lemon juice over salmon and asparagus before serving."
        ]
    },
    {
        "id": "mediterranean-quinoa-bowl",
        "title": "Mediterranean Chickpea & Quinoa Bowl",
        "description": "Vibrant plant-powered bowl with seasoned chickpeas, fluffy quinoa, crisp veggies, and lemon-tahini dressing.",
        "calories": 480,
        "protein_g": 18,
        "carbs_g": 68,
        "fat_g": 16,
        "prep_time_minutes": 15,
        "cook_time_minutes": 20,
        "dietary_tags": ["vegan", "vegetarian", "high-fiber", "gluten-free"],
        "ingredients": [
            "1 cup cooked quinoa",
            "1 can (15 oz) chickpeas (rinsed and drained)",
            "1 cup Persian cucumber (diced)",
            "1 cup cherry tomatoes (halved)",
            "1/4 cup kalamata olives (pitted)",
            "2 tbsp tahini",
            "1 tbsp extra virgin olive oil",
            "1 tbsp fresh lemon juice",
            "1/2 tsp cumin",
            "Salt and pepper to taste"
        ],
        "instructions": [
            "Toss drained chickpeas with olive oil, cumin, salt, and pepper. Lightly toast in a skillet for 6 minutes.",
            "Whisk tahini, lemon juice, 2 tbsp warm water, and a pinch of salt to make a smooth dressing.",
            "Divide cooked quinoa between bowls as the base.",
            "Arrange toasted chickpeas, diced cucumber, cherry tomatoes, and olives over quinoa.",
            "Drizzle generously with lemon-tahini dressing and garnish with fresh parsley."
        ]
    },
    {
        "id": "turkey-sweet-potato-skillet",
        "title": "Spiced Turkey & Sweet Potato Skillet",
        "description": "High-protein, clean-eating meal prep skillet featuring lean ground turkey, cubed sweet potatoes, and tender baby spinach.",
        "calories": 390,
        "protein_g": 34,
        "carbs_g": 32,
        "fat_g": 14,
        "prep_time_minutes": 15,
        "cook_time_minutes": 20,
        "dietary_tags": ["high-protein", "dairy-free", "gluten-free", "meal-prep"],
        "ingredients": [
            "1 lb 93% lean ground turkey",
            "2 medium sweet potatoes (peeled and diced into 1/2-inch cubes)",
            "1 red bell pepper (diced)",
            "1/2 yellow onion (diced)",
            "3 cups fresh baby spinach",
            "1 tbsp olive oil",
            "1 tsp smoked paprika",
            "1 tsp garlic powder",
            "1/2 tsp chili powder",
            "Salt and black pepper to taste"
        ],
        "instructions": [
            "Heat olive oil in a large skillet over medium heat.",
            "Add diced sweet potatoes, cover and steam-cook for 8-10 minutes until tender, stirring occasionally.",
            "Push potatoes to the side, add ground turkey, onion, and bell pepper; break up turkey and brown completely.",
            "Stir in smoked paprika, garlic powder, chili powder, salt, and black pepper.",
            "Fold in fresh baby spinach and cook 2 minutes until wilted.",
            "Divide into 4 servings for meal prep or serve immediately."
        ]
    },
    {
        "id": "greek-yogurt-berry-parfait",
        "title": "High-Protein Greek Yogurt Berry Parfait",
        "description": "Quick breakfast or post-workout fuel with thick Greek yogurt, antioxidant-rich berries, and chia seeds.",
        "calories": 290,
        "protein_g": 24,
        "carbs_g": 36,
        "fat_g": 4,
        "prep_time_minutes": 5,
        "cook_time_minutes": 0,
        "dietary_tags": ["high-protein", "quick-breakfast", "vegetarian"],
        "ingredients": [
            "1 cup plain nonfat Greek yogurt",
            "1/2 cup fresh blueberries",
            "1/2 cup fresh raspberries",
            "1 tbsp chia seeds",
            "1/4 cup rolled oats or high-protein granola",
            "1 tsp raw honey or pure maple syrup",
            "1/4 tsp ground cinnamon"
        ],
        "instructions": [
            "Spoon half of the Greek yogurt into a glass or bowl.",
            "Layer with half the blueberries, raspberries, and a sprinkle of chia seeds.",
            "Add remaining Greek yogurt and top with remaining berries, rolled oats, and cinnamon.",
            "Drizzle with honey or maple syrup and serve chilled."
        ]
    },
    {
        "id": "tofu-veggie-stir-fry",
        "title": "Crispy Tofu & Rainbow Veggie Stir-Fry",
        "description": "Savory plant-based stir-fry with crispy baked tofu cubes, broccoli florets, and snap peas in garlic-ginger tamari sauce.",
        "calories": 340,
        "protein_g": 22,
        "carbs_g": 26,
        "fat_g": 16,
        "prep_time_minutes": 20,
        "cook_time_minutes": 15,
        "dietary_tags": ["vegan", "vegetarian", "dairy-free", "low-calorie"],
        "ingredients": [
            "1 block (14 oz) extra firm tofu (pressed and cubed)",
            "2 cups broccoli florets",
            "1 cup snap peas",
            "1 medium carrot (julienned)",
            "1 tbsp toasted sesame oil",
            "2 tbsp reduced-sodium tamari or soy sauce",
            "1 tbsp grated fresh ginger",
            "2 cloves garlic (minced)",
            "1 tsp sesame seeds for garnish"
        ],
        "instructions": [
            "Press tofu for 15 minutes, cube, and pan-sear in 1 tsp sesame oil until all sides are golden and crispy (approx 8 mins). Set aside.",
            "In the same skillet, heat remaining sesame oil. Add broccoli, carrots, and snap peas; stir-fry for 4-5 minutes until tender-crisp.",
            "Add minced garlic and grated ginger, cook 30 seconds until fragrant.",
            "Return crispy tofu to skillet, pour tamari sauce over everything, and toss well for 1 minute.",
            "Garnish with toasted sesame seeds and serve warm."
        ]
    }
]


def seed_database():
    print(f"Connecting to Firestore with project '{PROJECT_ID}'...")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection("recipes")

    for recipe in SAMPLE_RECIPES:
        doc_id = recipe["id"]
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(recipe)
        print(f"  ✓ Seeded recipe: {recipe['title']} (ID: {doc_id})")

    print(f"Successfully seeded {len(SAMPLE_RECIPES)} recipes into 'recipes' collection.")


if __name__ == "__main__":
    seed_database()
