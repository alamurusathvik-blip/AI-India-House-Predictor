import re
import glob

for filepath in glob.glob('pages/*.py'):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'import textwrap' not in content:
        content = 'import textwrap\n' + content

    def replacer(m):
        arg1 = m.group(1)
        if 'st.markdown' in arg1 or 'textwrap.dedent' in arg1:
            return m.group(0)
        return f"st.html(textwrap.dedent({arg1}))"

    # Match st.html( <non-greedy anything> )
    content = re.sub(r'st\.markdown\((.*?),\s*unsafe_allow_html=True\)', replacer, content, flags=re.DOTALL)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Applied textwrap.dedent to all st.markdown calls in pages/")
