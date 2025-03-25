from flamapy.core.discover import DiscoverMetamodels

dm = DiscoverMetamodels()
fm_ingredients = dm.use_transformation_t2m('models/restauration/Bausatz/IngredientsBausatz2025.uvl', 'fm')
ingredients = {f.name for f in fm_ingredients.get_features()}
print(f'#Ingredients: {len(ingredients)}')

pizza_fm = dm.use_transformation_t2m('models/restauration/Bausatz/PizzaBausatz2025.uvl', 'fm')
pizza_ingredients = {f.name for f in pizza_fm.get_features()}
print(f'#Pizza ingredients: {len(pizza_ingredients)}')

diff = ingredients - pizza_ingredients
print(f'#Diff ingredients: {len(diff)}')
for i in diff:
    print(i)
