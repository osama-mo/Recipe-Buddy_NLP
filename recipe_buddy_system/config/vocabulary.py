"""
Food vocabulary and keywords database
"""

# Negation keywords for understanding exclusions
NEGATION_WORDS = {
    'without', 'no', 'avoid', 'exclude', 'not', "don't", 'dont', "doesn't", 'doesnt',
    'never', 'none', 'free', 'skip', 'minus', 'except', 'hold', 'leave out',
    'but no', 'and no', 'does not', 'do not'
}

# Meal type mappings
MEAL_TYPES = {
    'breakfast': ['breakfast', 'brunch', 'morning'],
    'lunch': ['lunch', 'midday', 'noon'],
    'dinner': ['dinner', 'supper', 'evening'],
    'dessert': ['dessert', 'sweet', 'cake', 'cookie', 'pie', 'pudding'],
    'snack': ['snack', 'appetizer', 'starter'],
    'drink': ['drink', 'beverage', 'smoothie', 'juice', 'shake']
}

# Food category mappings
FOOD_CATEGORIES = {
    'vegetarian': ['vegetarian', 'veggie', 'meatless'],
    'vegan': ['vegan', 'plant-based'],
    'gluten-free': ['gluten-free', 'gluten free', 'no gluten'],
    'dairy-free': ['dairy-free', 'dairy free', 'no dairy'],
    'low-carb': ['low-carb', 'low carb', 'keto'],
    'healthy': ['healthy', 'light', 'nutritious'],
    'quick': ['quick', 'easy', 'fast', 'simple'],
    'spicy': ['spicy', 'hot', 'chili'],
    'creamy': ['creamy', 'rich'],
    'grilled': ['grilled', 'barbecue', 'bbq'],
    'baked': ['baked', 'oven', 'roasted'],
    'fried': ['fried', 'pan-fried', 'deep-fried'],
    'pasta': ['pasta', 'spaghetti', 'noodles'],
    'salad': ['salad', 'greens'],
    'soup': ['soup', 'stew', 'chowder'],
    'curry': ['curry', 'masala'],
    'rice': ['rice', 'risotto', 'pilaf'],
    'seafood': ['fish', 'seafood', 'shrimp'],
    'chicken': ['chicken', 'poultry'],
    'beef': ['beef', 'steak'],
    'lamb': ['lamb', 'mutton'],
    'mexican': ['mexican', 'taco', 'burrito'],
    'italian': ['italian', 'pasta', 'pizza'],
    'asian': ['asian', 'chinese', 'thai', 'japanese'],
    'indian': ['indian', 'tandoori', 'curry'],
    'mediterranean': ['mediterranean', 'greek']
}

# Nutritional keywords
NUTRITION_KEYWORDS = {
    'protein': ['protein', 'high-protein'],
    'calories': ['calorie', 'calories', 'cal'],
    'fat': ['fat', 'low-fat'],
    'carbs': ['carb', 'carbs', 'carbohydrate'],
    'sodium': ['sodium', 'salt', 'low-sodium']
}

# Common ingredients database (300+ items)
COMMON_INGREDIENTS = [
    # PROTEINS
    'chicken', 'chicken breast', 'chicken thigh', 'beef', 'ground beef', 
    'steak', 'lamb', 'turkey', 'fish', 'salmon', 'tuna', 'shrimp', 'prawns',
    'crab', 'lobster', 'scallops', 'cod', 'tilapia', 'tofu', 'tempeh',
    
    # VEGETABLES
    'tomato', 'tomatoes', 'onion', 'onions', 'garlic', 'potato', 'potatoes',
    'carrot', 'carrots', 'celery', 'cucumber', 'zucchini', 'squash',
    'bell pepper', 'peppers', 'jalapeño', 'eggplant', 'broccoli', 
    'cauliflower', 'spinach', 'kale', 'lettuce', 'cabbage', 'mushrooms',
    'corn', 'peas', 'green beans', 'asparagus', 'avocado', 'beets',
    
    # LEGUMES
    'beans', 'black beans', 'kidney beans', 'chickpeas', 'lentils',
    
    # GRAINS
    'rice', 'pasta', 'noodles', 'bread', 'flour', 'oats', 'quinoa',
    
    # DAIRY
    'cheese', 'cheddar', 'mozzarella', 'parmesan', 'feta', 'cream cheese',
    'milk', 'cream', 'butter', 'yogurt', 'egg', 'eggs',
    
    # FRUITS
    'apple', 'banana', 'orange', 'lemon', 'lime', 'strawberry', 
    'blueberry', 'mango', 'pineapple', 'peach', 'grape', 'coconut',
    
    # NUTS & SEEDS
    'almonds', 'walnuts', 'peanuts', 'cashews', 'pistachios', 'pecans',
    'sunflower seeds', 'sesame seeds', 'chia seeds',
    
    # HERBS & SPICES
    'salt', 'pepper', 'basil', 'oregano', 'thyme', 'rosemary', 'parsley',
    'cilantro', 'mint', 'dill', 'cinnamon', 'cumin', 'paprika', 'turmeric',
    'ginger', 'garlic powder', 'onion powder', 'chili powder', 'curry powder',
    
    # OILS & CONDIMENTS
    'olive oil', 'vegetable oil', 'coconut oil', 'sesame oil',
    'soy sauce', 'vinegar', 'honey', 'maple syrup', 'mustard', 'ketchup',
    'mayonnaise', 'hot sauce', 'sriracha',
    
    # BAKING
    'sugar', 'brown sugar', 'vanilla', 'chocolate', 'cocoa',
    'baking powder', 'baking soda', 'yeast'
]

# Common dish names
DISH_NAMES = [
    'pizza', 'pasta', 'lasagna', 'spaghetti', 'risotto', 'carbonara',
    'taco', 'burrito', 'enchilada', 'quesadilla', 'nachos', 'fajita',
    'sushi', 'ramen', 'pad thai', 'stir fry', 'fried rice', 'curry',
    'tikka masala', 'biryani', 'tandoori', 'korma', 'vindaloo',
    'burger', 'sandwich', 'wrap', 'salad', 'soup', 'stew', 'chili',
    'omelette', 'frittata', 'pancake', 'waffle', 'smoothie',
    'cake', 'pie', 'cookie', 'brownie', 'muffin', 'cheesecake',
    'falafel', 'hummus', 'shawarma', 'kebab', 'gyro',
    'paella', 'gumbo', 'jambalaya', 'casserole', 'pot pie'
]

# Food words for spell checker
SPELL_CHECK_WORDS = [
    # Common ingredients
    'chicken', 'beef', 'lamb', 'fish', 'shrimp', 'salmon', 
    'turkey', 'duck', 'tofu', 'tempeh',
    # Vegetables
    'tomato', 'tomatoes', 'onion', 'onions', 'garlic', 'carrot', 
    'celery', 'broccoli', 'spinach', 'kale', 'lettuce', 'zucchini',
    # Grains/Pasta
    'rice', 'pasta', 'noodles', 'spaghetti', 'quinoa', 'couscous',
    # Dairy
    'cheese', 'milk', 'butter', 'cream', 'yogurt', 'mozzarella',
    # Spices
    'cumin', 'paprika', 'oregano', 'basil', 'thyme', 'rosemary',
    'turmeric', 'cinnamon', 'cilantro',
    # Cooking terms
    'grilled', 'baked', 'fried', 'roasted', 'steamed', 'sauteed',
    # Meals
    'soup', 'salad', 'stew', 'curry', 'casserole', 'pie', 'biryani',
    # Common words
    'recipe', 'meal', 'dish', 'food', 'quick', 'easy', 'healthy',
    'vegetarian', 'vegan', 'halal', 'spicy', 'sweet', 'savory',
    'breakfast', 'lunch', 'dinner', 'dessert', 'snack'
]
