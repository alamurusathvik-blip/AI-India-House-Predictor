import re
import glob

for filepath in glob.glob('pages/*.py'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    def replacer(m):
        arg = m.group(1)
        return f"st.html({arg})"

    new_content = re.sub(r'st\.markdown\((.*?),\s*unsafe_allow_html=True\)', replacer, content, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

print("Replaced st.markdown with st.html in all pages")
