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

# Style for to-do name in to-do details window
AT_TODO_HEADER_STYLE = (
    'w-[85%] bg-white font-inter font-bold text-zinc-900 text-[31px] '
    'leading-[1.5] tracking-[-0.16px] px-2 py-[6px] rounded-md '
    'shadow-[0_0_1px_0_rgba(0,0,0,0.32),0_1px_3px_0_rgba(0,0,0,0.08)]'
)

# Style for to-do details window done button
AT_DONE_CTA_BTN_STYLE = (
    'w-[15%] h-[40px] !bg-[#1555d9] text-white text-medium rounded-md '
    'shadow-[0_0_1px_0_rgba(0,0,0,0.32),0_1px_3px_0_rgba(0,0,0,0.08)]'
)

AT_DONE_DELETE_BTN_STYLE = (
    'w-[15%] h-[40px] !bg-[#FF0000] text-white text-medium rounded-md '
    'shadow-[0_0_1px_0_rgba(0,0,0,0.32),0_1px_3px_0_rgba(0,0,0,0.08)]'
)

# Style for to-do details window properties selector type
AT_PROPERTY_SELECTOR_STYLE = (
    'w-full bg-white font-inter font-bold text-zinc-900 '
    'leading-[1.5] tracking-[-0.16px] px-2 py-0 rounded-md '
    'shadow-[0_0_1px_0_rgba(0,0,0,0.32),0_1px_3px_0_rgba(0,0,0,0.08)]'
)

# Style for to-do details window mini properties heading
AT_TODO_PROPERTIES_HEADING = 'font-inter text-zinc-900 text-[13px] leading-[1.5] font-medium'

# Style for to-do details window date type labels
AT_DATE_LABEL_STYLE = (
    'w-full bg-white font-inter text-zinc-900'
    'leading-[1.5] tracking-[-0.16px] px-2 py-2 rounded-md '
    'shadow-[0_0_1px_0_rgba(0,0,0,0.32),0_1px_3px_0_rgba(0,0,0,0.08)]'
)

# Style for to-do details window upload type property
AT_UPLOAD_ZONE_STYLE = (
    'max-w-full font-inter text-zinc-900'
    'leading-[1.5] tracking-[-0.16px] px-2 py-2 rounded-md '
    'shadow-[0_0_1px_0_rgba(0,0,0,0.32),0_1px_3px_0_rgba(0,0,0,0.08)]'
)

# Style for to-do creation window create button
AT_CREATE_TODO_BTN_STYLE = (
    'w-[15%] h-[40px] !bg-[#127b0d] text-white text-medium rounded-md '
    'shadow-[0_0_1px_0_rgba(0,0,0,0.32),0_1px_3px_0_rgba(0,0,0,0.08)]'
)

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
