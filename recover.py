import json
import os

log_path = r'C:\Users\n5376\.gemini\antigravity\brain\8d3cde02-c9c7-43f4-a594-2ddb09e42164\.system_generated\logs\transcript_full.jsonl'

with open(log_path, encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        for call in data.get('tool_calls', []):
            if isinstance(call, dict) and 'write_to_file' in call.get('name', ''):
                args = call.get('arguments', {})
                if 'CodeContent' in args and 'TargetFile' in args:
                    target_file = args['TargetFile']
                    if '1_Prediction.py' in target_file:
                        out_path = 'pages/1_Prediction.py'
                    elif '2_Market_Insights.py' in target_file:
                        out_path = 'pages/2_Market_Insights.py'
                    elif '3_AI_Insights.py' in target_file:
                        out_path = 'pages/3_AI_Insights.py'
                    elif 'app.py' in target_file:
                        out_path = 'app.py'
                    else:
                        continue
                        
                    content = args['CodeContent']
                    with open(out_path, 'w', encoding='utf-8') as out_f:
                        out_f.write(content)
                    print(f"Recovered {out_path}")
