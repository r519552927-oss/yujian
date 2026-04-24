import json
import urllib.request

# IMA凭证
client_id = "34c0f65a6c4e544e9a6f29bb637da9ea"
api_key = "+oddXHKF4LxPfWoo8HnFIYaLX6Sy+aQJYFeVVrlnURivNVlX0HnWUwgGv+yR+XAVhPtzjHxttg=="

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

# 电机设计相关的知识库ID - 只取前3个最相关的
relevant_kbs = [
    ("电机教程|自学知识库", "vdMKGhWku0tH8xomh48hHhJThXe62UQ1KOWOBSUmyXw="),
    ("电机学/电机设计", "1hdIUqt4l7pr5TLLPfBR6WUztgonQpCG7KAs8Xc9_lA="),
    ("ANSYS EM电磁仿真知识库", "mmKJlBUFeERptdEzdwzwqvGY25_NfO6RzqpEE3LNL2c="),
]

print("=" * 70)
print("[Browsing Motor Design Knowledge Bases]")
print("=" * 70)

for kb_name, kb_id in relevant_kbs[:2]:  # 先看前2个
    print(f"\n\n=== {kb_name} ===")
    
    # 浏览根目录
    result = call_ima_api("openapi/wiki/v1/get_knowledge_list", {
        "knowledge_base_id": kb_id,
        "cursor": "",
        "limit": 50
    })
    
    if result.get('retcode') == 0:
        data = result.get('data', {})
        knowledge_list = data.get('knowledge_list', [])
        
        if knowledge_list:
            print(f"Found {len(knowledge_list)} items:\n")
            for item in knowledge_list:
                title = item.get('title', 'Unknown')
                media_type = item.get('media_type', 0)
                folder_id = item.get('folder_id', '')
                
                # 判断类型
                if folder_id:
                    print(f"  [DIR]  {title}/")
                else:
                    type_names = {1: "PDF", 2: "网页", 6: "微信", 7: "Markdown", 9: "图片", 11: "笔记", 13: "TXT"}
                    type_name = type_names.get(media_type, f"Type{media_type}")
                    print(f"  [{type_name}] {title}")
        else:
            print("  (empty)")
        
        # 检查是否有下一页
        is_end = data.get('is_end', True)
        if not is_end:
            print(f"  ... (more content, next_cursor: {data.get('next_cursor', '')})")
    else:
        print(f"  Error: {result}")
