import glob
import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '??' in content or '?' in content:
        # replace common ones
        content = content.replace('?? Quick Navigation', '🧭 Quick Navigation')
        content = content.replace('?? <strong>Prediction</strong>', '🔮 <strong>Prediction</strong>')
        content = content.replace('?? <strong>Market Insights</strong>', '📊 <strong>Market Insights</strong>')
        content = content.replace('?? <strong>AI Insights</strong>', '🧠 <strong>AI Insights</strong>')
        
        # fix header emojis
        content = content.replace('<div style="font-size: 2.5rem;">??</div>', '<div style="font-size: 2.5rem;">🏠</div>')
        content = content.replace('<div style="font-size: 1.8rem;">??</div>', '<div style="font-size: 1.8rem;">🔮</div>')
        # We need to make sure we don't blindly replace all 1.8rem ?? with the same thing if they are different pages,
        # but let's just use generic ones or replace them uniquely per file.
        if '1_Prediction' in filepath:
            content = content.replace('<div style="font-size: 1.8rem;">??</div>', '<div style="font-size: 1.8rem;">🔮</div>')
        elif '2_Market_Insights' in filepath:
            content = content.replace('<div style="font-size: 1.8rem;">??</div>', '<div style="font-size: 1.8rem;">📊</div>')
        elif '3_AI_Insights' in filepath:
            content = content.replace('<div style="font-size: 1.8rem;">??</div>', '<div style="font-size: 1.8rem;">🧠</div>')
        
        # Indian Rupee symbol
        content = content.replace('?{predicted_pps_rupees', '₹{predicted_pps_rupees')
        content = content.replace('?{market_pps_rupees', '₹{market_pps_rupees')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed {filepath}')

for f in glob.glob('*.py') + glob.glob('pages/*.py'):
    if f != 'fix_emojis.py':
        fix_file(f)
