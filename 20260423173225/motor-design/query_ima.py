import json
import urllib.request

# IMA凭证
client_id = "34c0f65a6c4e544e9a6f29bb637da9ea"
api_key = "+oddXHKF4LxPfWoo8HnFIYaLX6Sy+aQJYFeVVrlnURivNVlX0HnWUwgGv+yR+XAVhPtzjHxttg=="

# 设置请求头
headers = {
    'ima-openapi-clientid': client_id,
    'ima-openapi-apikey': api_key,
    'Content-Type': 'application/json; charset=utf-8'
}

def call_ima_api(path, body):
    url = f"https://ima.qq.com/{path}"
    data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {"retcode": -1, "errmsg": f"HTTP {e.code}: {e.read().decode('utf-8')}"}

# 获取所有知识库
result = call_ima_api("openapi/wiki/v1/search_knowledge_base", {
    "query": "",
    "cursor": "",
    "limit": 20
})

print("=" * 60)
print("[Knowledge Base List]")
print("=" * 60)

if result.get('retcode') == 0:
    data = result.get('data', {})
    knowledge_bases = data.get('knowledge_base_list', [])

    if knowledge_bases:
        print(f"Found {len(knowledge_bases)} knowledge base(s):\n")
        for kb in knowledge_bases:
            print(f"Name: {kb.get('name', 'Unknown')}")
            print(f"  ID: {kb.get('id', 'N/A')}")
            print(f"  Description: {kb.get('description', 'None')}")
            print()
    else:
        print("No knowledge base found")
else:
    print(f"Error: {result.get('errmsg', 'Unknown error')}")
    print(f"Full response: {result}")
