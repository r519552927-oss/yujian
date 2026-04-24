# -*- coding: utf-8 -*-
"""浏览IMA知识库内容"""

import urllib.request
import json

CLIENT_ID = "34c0f65a6c4e544e9a6f29bb637da9ea"
API_KEY = "+oddXHKF4LxPfWoo8HnFIYaLX6Sy+aQJYFeVVrlnURivNVlX0HnWUwgGv+yR+XAVhPtzjHxttg=="

def get_kb_list():
    """获取知识库列表"""
    url = "https://ima.qq.com/openapi/wiki/v1/list_knowledge_base"
    headers = {
        "ima-openapi-clientid": CLIENT_ID,
        "ima-openapi-apikey": API_KEY,
        "Content-Type": "application/json; charset=utf-8"
    }
    body = {"query": "", "cursor": "", "limit": 50}
    
    req = urllib.request.Request(url,
                                  data=json.dumps(body).encode('utf-8'),
                                  headers=headers,
                                  method='POST')
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))

def get_kb_content(knowledge_base_id, cursor=""):
    """获取知识库内容"""
    url = "https://ima.qq.com/openapi/wiki/v1/get_knowledge_base_content"
    headers = {
        "ima-openapi-clientid": CLIENT_ID,
        "ima-openapi-apikey": API_KEY,
        "Content-Type": "application/json; charset=utf-8"
    }
    body = {
        "knowledge_base_id": knowledge_base_id,
        "cursor": cursor,
        "limit": 100
    }
    
    req = urllib.request.Request(url,
                                  data=json.dumps(body).encode('utf-8'),
                                  headers=headers,
                                  method='POST')
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))

if __name__ == "__main__":
    # 获取所有知识库
    print("=" * 60)
    print("IMA 知识库列表")
    print("=" * 60)
    
    result = get_kb_list()
    if result.get("code") == 0:
        kbs = result["data"]["info_list"]
        
        # 找出材料相关的知识库
        material_kbs = []
        for kb in kbs:
            name = kb.get("name", "")
            kb_id = kb.get("knowledge_base_id", "")
            count = kb.get("content_count", 0)
            print(f"ID: {kb_id} | {name} | {count}条")
            
            if any(keyword in name for keyword in ["材料", "硅钢", "磁钢", "永磁", "电机", "铁心"]):
                material_kbs.append(kb)
        
        print("\n" + "=" * 60)
        print("材料相关知识库")
        print("=" * 60)
        
        for kb in material_kbs:
            print(f"\n浏览: {kb['name']}")
            print("-" * 40)
            
            # 获取内容
            content_result = get_kb_content(kb["knowledge_base_id"])
            if content_result.get("code") == 0:
                items = content_result["data"]["info_list"]
                for item in items[:30]:  # 只显示前30条
                    title = item.get("title", "")
                    content = item.get("content", "")[:200]
                    print(f"  [{title}]")
                    if content:
                        print(f"    {content}...")
            else:
                print(f"  获取失败: {content_result}")
