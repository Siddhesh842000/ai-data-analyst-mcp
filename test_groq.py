import urllib.request
import json
import re
import os

print("Starting Groq API Diagnostic...")

# 1. Get Key
try:
    with open('.streamlit/secrets.toml', 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'GROQ_API_KEY\s*=\s*[\"\'](.*?)[\"\']', content)
    key = match.group(1)
except Exception as e:
    print(f"Failed to read key: {e}")
    exit(1)

# 2. Get Models allowed for this specific key
req = urllib.request.Request('https://api.groq.com/openai/v1/models', headers={'Authorization': 'Bearer ' + key, 'User-Agent': 'Mozilla/5.0'})
try:
    res = urllib.request.urlopen(req)
    data = json.loads(res.read())
    models = [m['id'] for m in data.get('data', [])]
    print(f"Models authorized for your key: {models}")
except Exception as e:
    print(f"FAILED TO GET MODELS: {e}")
    exit(1)

# 3. Test Models to find one that works for Chat
working_model = None
for model_id in models:
    # Skip audio and moderation models
    if 'whisper' in model_id or 'guard' in model_id or 'embed' in model_id:
        continue
        
    print(f"Testing chat with {model_id}...")
    test_req = urllib.request.Request(
        'https://api.groq.com/openai/v1/chat/completions',
        data=json.dumps({
            "model": model_id,
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }).encode('utf-8'),
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}
    )
    try:
        test_res = urllib.request.urlopen(test_req)
        print(f"✅ SUCCESS with {model_id}")
        working_model = model_id
        break
    except urllib.error.HTTPError as e:
        print(f"❌ FAILED {model_id}: HTTP {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"❌ FAILED {model_id}: {e}")

# 4. Update app.py automatically
if working_model:
    with open('app.py', 'r', encoding='utf-8') as f:
        app_code = f.read()
    
    # Safely replace the model string
    app_code = re.sub(r'model="[^"]+"', f'model="{working_model}"', app_code)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_code)
    print(f"\n🎉 UPDATED APP.PY TO USE VERIFIED MODEL: {working_model}")
else:
    print("\n❌ NO WORKING CHAT MODELS FOUND FOR THIS API KEY.")
