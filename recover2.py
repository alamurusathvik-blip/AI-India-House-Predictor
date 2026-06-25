import json
import glob
import os

logs = glob.glob(r'C:\Users\n5376\.gemini\antigravity\brain\*\.system_generated\logs\transcript_full.jsonl')
files_to_recover = ['1_Prediction.py', '2_Market_Insights.py', '3_AI_Insights.py', 'app.py']
best_contents = {f: "" for f in files_to_recover}

for log_path in logs:
    with open(log_path, encoding='utf-8') as f:
        for line in f:
            if 'write_to_file' not in line:
                continue
            data = json.loads(line)
            for call in data.get('tool_calls', []):
                if isinstance(call, dict) and 'write_to_file' in call.get('name', ''):
                    # Handle both 'arguments' and 'args' schema
                    args = call.get('arguments', call.get('args', {}))
                    target_file = args.get('TargetFile', '')
                    content = args.get('CodeContent', '')
                    for f_name in files_to_recover:
                        # Wait, sometimes TargetFile is missing if it's the very first argument and the subagent didn't pass it?
                        # No, the screenshot of the JSON shows:
                        # "args": {"CodeContent": "\"\"\"\nShared Utilities...
                        # Oh, the UI subagent didn't even specify TargetFile for some files!
                        # But we can infer the file from the content!
                        if f_name in target_file or f_name.replace('.py', '').replace('_', ' ') in content or '3_AI_Insights' in content or 'Landing Page' in content:
                            pass
                        
                    # Let's use simple heuristics since we know the content
                    if 'Prediction Page' in content and len(content) > len(best_contents['1_Prediction.py']):
                        best_contents['1_Prediction.py'] = content
                    elif 'Market Insights Page' in content and len(content) > len(best_contents['2_Market_Insights.py']):
                        best_contents['2_Market_Insights.py'] = content
                    elif 'AI Insights Page' in content and len(content) > len(best_contents['3_AI_Insights.py']):
                        best_contents['3_AI_Insights.py'] = content
                    elif 'Landing Page' in content and len(content) > len(best_contents['app.py']):
                        best_contents['app.py'] = content

for f_name, content in best_contents.items():
    if not content:
        print(f"Could not find {f_name}")
        continue
    out_path = 'app.py' if f_name == 'app.py' else f'pages/{f_name}'
    with open(out_path, 'w', encoding='utf-8') as out_f:
        out_f.write(content)
    print(f"Recovered {out_path} ({len(content)} bytes)")
