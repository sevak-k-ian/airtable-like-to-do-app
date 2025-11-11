from nicegui import ui

# "Inter" font from Google Fonts for the whole page
GOOGLE_INTER_FONT = ui.add_head_html('''
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
    /* Apply the font to all elements that use it */
    body, .font-inter {
        font-family: 'Inter', sans-serif;
    }
</style>
''')

# Dictionaries to map values to Tailwind CSS classes for color
STATUS_COLORS = {
    'Todo': 'bg-gray-200 text-gray-800',
    'In Progress': 'bg-blue-200 text-blue-800',
    'Done': 'bg-green-200 text-green-800',
}
PRIORITY_COLORS = {
    'Low': 'bg-yellow-200 text-yellow-800',
    'Medium': 'bg-orange-200 text-orange-800',
    'High': 'bg-red-200 text-red-800',
}

