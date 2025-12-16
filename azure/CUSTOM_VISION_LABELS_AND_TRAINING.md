# Custom Vision labels + training tips (ingredients)

## Recommended label list (starter)
Vegetables:
- tomato, onion, garlic, carrot, potato, bell_pepper, cucumber, lettuce, zucchini, eggplant, spinach

Herbs & spices:
- basil, parsley, cilantro, ginger

Proteins:
- chicken, beef, fish, tuna, egg

Carbs:
- pasta, rice, bread

Dairy:
- cheese, milk, yogurt, butter

Fruits:
- lemon, avocado, apple, banana

## Training tips (to improve reliability)
1) **Per label: 30–50 images minimum** (more is better).
2) **Diversity**: different angles, backgrounds, lighting, camera phones.
3) **Avoid “mixed label noise”**:
   - If an image shows tomato + onion, either:
     - use multi-label classification carefully, OR
     - create images mostly focused on one main ingredient for early training.
4) **Consistent naming**:
   - use lowercase and underscores (bell_pepper).
5) **Iteration strategy**:
   - Train Iteration1 with the most common 15–25 ingredients.
   - Publish it, test, then add more labels.
6) **Threshold tuning**:
   - Start with 0.60; if too strict, reduce to 0.50.
   - If too many wrong labels, increase to 0.70.
7) **Test set**:
   - Keep 5–10 images per label as “never seen” images for evaluation.
