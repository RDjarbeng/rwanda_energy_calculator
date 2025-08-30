from fasthtml.common import *
from main import app
import os

# Create output directory
os.makedirs('dist', exist_ok=True)

# Generate static HTML for sample routes
routes = ['/', '/calculate-cost?units=10', '/calculate-units?amount=10000']
for route in routes:
    response = app.test_client().get(route)
    file_name = 'index.html' if route == '/' else route.replace('/', '_').replace('?', '_') + '.html'
    with open(f'dist/{file_name}', 'w') as f:
        f.write(response.text)