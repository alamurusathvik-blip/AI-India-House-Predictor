import re

with open(r'pages\3_AI_Insights.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Using regex to find all st.html("""...""") or st.markdown(f"""...""")
# that end with """) without unsafe_allow_html=True
# and replace the ending """) with """)
def replacer(match):
    # the match is the whole st.html(f"""...""")
    text = match.group(0)
    if 'unsafe_allow_html=True' not in text:
        # replace the last """) with """)
        return text[:-1] + ', unsafe_allow_html=True)'
    return text

content = re.sub(r'st\.markdown\(f?\"\"\"(?:.*?)\"\"\"\)', replacer, content, flags=re.DOTALL)

with open(r'pages\3_AI_Insights.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Fixed AI Insights markdown calls.")
