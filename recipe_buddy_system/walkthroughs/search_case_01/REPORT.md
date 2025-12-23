# Search walkthrough report (case 01)

Generated: 2025-12-20 08:51:55 UTC

## Query

- Raw: `high protein chicken include tomato no onion`

## Parsed output

- dish_name: `None`
- ingredients (required): `['chicken', 'tomato']`
- excluded_ingredients: `['onion', 'onions', 'onion powder']`
- categories: `['chicken']`
- meal_type: `None`
- nutrition: `{"protein": {"min": 15}}`

## Hard filter order (DB mode)

1. Excluded ingredients (instant reject)
2. Nutrition constraints (instant reject)
3. Required ingredients (ALL must be present)
4. Dish name (if extracted)
5. Score valid candidates

## Results

### #1 — id=2917 — score=0.97 (97.0/100)

Title: `Chicken Breasts Stuffed with Fontina, Artichokes, and Sun-Dried Tomatoes`

**Hard filters**

- Passed: `True`
- PASS: all hard filters satisfied

**Score breakdown**

- dish_name: `0.0`
- ingredients total: `65.0`
- ingredient `chicken`: +`35.0` (title=`25`, text=`10`)
- ingredient `tomato`: +`30.0` (title=`20`, text=`10`)
- combo_bonus: `0.0`
- categories: `12.0`
- meal_type: `0.0`
- nutrition_bonus: `20.0`
- total_points: `97.0`

**Nutrition (from DB)**

- calories: `139.5`
- protein: `18.6`
- fat: `5.7`
- sodium: `274.6`
- sugar: `0.9`
- saturates: `2.0`

### #2 — id=39528 — score=0.86 (86.0/100)

Title: `Feta, Walnut and Sun-Dried Tomato Stuffed Chicken Breasts`

**Hard filters**

- Passed: `True`
- PASS: all hard filters satisfied

**Score breakdown**

- dish_name: `0.0`
- ingredients total: `54.0`
- ingredient `chicken`: +`27.0` (title=`17`, text=`10`)
- ingredient `tomato`: +`27.0` (title=`17`, text=`10`)
- combo_bonus: `0.0`
- categories: `12.0`
- meal_type: `0.0`
- nutrition_bonus: `20.0`
- total_points: `86.0`

**Nutrition (from DB)**

- calories: `202.5`
- protein: `16.3`
- fat: `13.6`
- sodium: `13403.9`
- sugar: `0.6`
- saturates: `3.5`

### #3 — id=245 — score=0.75 (75.0/100)

Title: `Spicy Chicken Mac Skillet`

**Hard filters**

- Passed: `True`
- PASS: all hard filters satisfied

**Score breakdown**

- dish_name: `0.0`
- ingredients total: `43.0`
- ingredient `chicken`: +`33.0` (title=`23`, text=`10`)
- ingredient `tomato`: +`10.0` (title=`0.0`, text=`10`)
- combo_bonus: `0.0`
- categories: `12.0`
- meal_type: `0.0`
- nutrition_bonus: `20.0`
- total_points: `75.0`

**Nutrition (from DB)**

- calories: `248.6`
- protein: `23.4`
- fat: `15.7`
- sodium: `2095.5`
- sugar: `1.1`
- saturates: `9.5`

### #4 — id=8009 — score=0.75 (75.0/100)

Title: `Buffalo Chicken Dip`

**Hard filters**

- Passed: `True`
- PASS: all hard filters satisfied

**Score breakdown**

- dish_name: `0.0`
- ingredients total: `43.0`
- ingredient `chicken`: +`33.0` (title=`23`, text=`10`)
- ingredient `tomato`: +`10.0` (title=`0.0`, text=`10`)
- combo_bonus: `0.0`
- categories: `12.0`
- meal_type: `0.0`
- nutrition_bonus: `20.0`
- total_points: `75.0`

**Nutrition (from DB)**

- calories: `216.3`
- protein: `15.1`
- fat: `15.9`
- sodium: `1234.4`
- sugar: `1.9`
- saturates: `5.1`

### #5 — id=29578 — score=0.75 (75.0/100)

Title: `Ww Chicken With Warm Bean Salsa`

**Hard filters**

- Passed: `True`
- PASS: all hard filters satisfied

**Score breakdown**

- dish_name: `0.0`
- ingredients total: `43.0`
- ingredient `chicken`: +`33.0` (title=`23`, text=`10`)
- ingredient `tomato`: +`10.0` (title=`0.0`, text=`10`)
- combo_bonus: `0.0`
- categories: `12.0`
- meal_type: `0.0`
- nutrition_bonus: `20.0`
- total_points: `75.0`

**Nutrition (from DB)**

- calories: `116.6`
- protein: `21.3`
- fat: `2.7`
- sodium: `607.8`
- sugar: `0.2`
- saturates: `0.6`
