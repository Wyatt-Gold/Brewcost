SELECT ingredients.id,
       ingredients.name,
       ingredients.brand,
       ingredients.category_id,
       categories.name AS category,
       ingredients.cost_per_unit,
       ingredients.unit
FROM ingredients
JOIN categories ON ingredients.category_id = categories.id
ORDER BY ingredients.name
