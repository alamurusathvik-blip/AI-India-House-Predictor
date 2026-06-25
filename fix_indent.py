import glob
import re
import os

files = glob.glob('pages/*.py') + ['app.py']

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if 'import textwrap' not in content:
        content = 'import textwrap\n' + content
        
    # Find all st.html("""...""") 
    # and st.html(f"""...""")
    new_content = re.sub(
        r'st\.markdown\(\s*(f?\"\"\"(?:.*?)\"\"\")\s*,\s*unsafe_allow_html=True\s*\)',
        r'st.html(textwrap.dedent(\1))',
        content,
        flags=re.DOTALL
    )
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(new_content)

print("Fixed all markdown indentations!")
