# My agent: NutriChef AI
One-liner: A conversational agent that helps health-conscious individuals eat healthy, hit their calorie and macro goals, and cook zero-waste meals with a catalog of healthy recipes and pantry ingredients.

Tool coverage:
- Memory: Daily calorie and macronutrient targets (protein, carb, fat goals), dietary restrictions, food allergies, current pantry inventory, and meal history/ratings
- Tools: Look up recipes filtered by dietary preferences and available pantry items, update/track pantry ingredients, log daily meals, and compute nutrition breakdowns
- Catalog/UI: Rich recipe cards (displaying macros, prep time, ingredients) and weekly meal plan / grocery tables rendered via A2UI
- Image gen: Plating visuals for suggested healthy dishes and meal prep presentations
- Sandbox: Exact calorie and macro calculations, serving size scaling, and nutritional deficit/surplus analysis

Recommended for every project: memory, storage, tools, image generation, A2UI
Agent-specific / stretch (pick what fits): code sandbox for macro calculations and recipe scaling, Firestore for pantry and macro log persistence, Cloud Trace for observability
