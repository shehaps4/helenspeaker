import re

html = open('index.html', encoding='utf-8').read()
defined_ids = set(re.findall(r'id=["\']([^"\']+)["\']', html))
queried_ids = set(re.findall(r'getElementById\(["\']([^"\']+)["\']\)', html))
missing = queried_ids - defined_ids
print('Missing IDs queried in JS:', missing)
