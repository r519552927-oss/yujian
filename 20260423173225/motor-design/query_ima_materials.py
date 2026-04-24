# -*- coding: utf-8 -*-
"""从IMA知识库获取电机材料数据"""

import urllib.request
import urllib.parse
import json
import os

# 读取凭证
CLIENT_ID_PATH = os.path.expanduser("~/.config/ima/client_id")
API_KEY_PATH = os.path.expanduser("~/.config/ima/api_key")

with open(CLIENT_ID_PATH, 'r') as f:
    CLIENT_ID = f.read().strip()
with open(API_KEY_PATH, 'r') as f:
    API_KEY = f.read().strip()

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

def search_kb(query):
    """搜索知识库"""
    url = "https://ima.qq.com/openapi/wiki/v1/search_knowledge_base"
    headers = {
        "ima-openapi-clientid": CLIENT_ID,
        "ima-openapi-apikey": API_KEY,
        "Content-Type": "application/json; charset=utf-8"
    }
    body = {"query": query, "cursor": "", "limit": 50}
    
    req = urllib.request.Request(url,
                                  data=json.dumps(body).encode('utf-8'),
                                  headers=headers,
                                  method='POST')
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))

def get_kb_content(knowledge_base_id, cursor=""):
    """获取知识库内容"""
    url = "https://ima.qq.com/openapi/wiki/v1/get_knowledge_list"
    headers = {
        "ima-openapi-clientid": CLIENT_ID,
        "ima-openapi-apikey": API_KEY,
        "Content-Type": "application/json; charset=utf-8"
    }
    body = {
        "knowledge_base_id": knowledge_base_id,
        "cursor": cursor,
        "limit": 50
    }
    
    req = urllib.request.Request(url,
                                  data=json.dumps(body).encode('utf-8'),
                                  headers=headers,
                                  method='POST')
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))

def search_kb_content(knowledge_base_id, query):
    """在知识库中搜索"""
    url = "https://ima.qq.com/openapi/wiki/v1/search_knowledge"
    headers = {
        "ima-openapi-clientid": CLIENT_ID,
        "ima-openapi-apikey": API_KEY,
        "Content-Type": "application/json; charset=utf-8"
    }
    body = {
        "knowledge_base_id": knowledge_base_id,
        "query": query,
        "cursor": ""
    }
    
    req = urllib.request.Request(url,
                                  data=json.dumps(body).encode('utf-8'),
                                  headers=headers,
                                  method='POST')
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode('utf-8'))

if __name__ == "__main__":
    print("=" * 60)
    print("从IMA知识库获取电机材料数据")
    print("=" * 60)
    
    # 获取所有知识库
    print("\n[1] 获取知识库列表...")
    kb_result = get_kb_list()
    
    if kb_result.get("code") == 0 or kb_result.get("retcode") == 0:
        kbs = kb_result["data"]["info_list"]
        
        # 找出材料相关的知识库
        material_kbs = []
        print(f"   找到 {len(kbs)} 个知识库")
        
        for kb in kbs:
            name = kb.get("name", "")
            kb_id = kb.get("knowledge_base_id", kb.get("id", ""))
            count = kb.get("content_count", 0)
            
            if any(keyword in name for keyword in ["材料", "硅钢", "磁钢", "永磁"]):
                print(f"   ★ 材料库: {name} (ID: {kb_id})")
                material_kbs.append(kb)
        
        # 搜索包含"电机"的知识库
        motor_kbs = []
        for kb in kbs:
            name = kb.get("name", "")
            kb_id = kb.get("knowledge_base_id", kb.get("id", ""))
            if "电机" in name:
                print(f"   ◉ 电机库: {name} (ID: {kb_id})")
                motor_kbs.append(kb)
        
        # 搜索内容
        print("\n[2] 搜索硅钢材料...")
        steel_result = search_kb("硅钢")
        if steel_result.get("code") == 0 or steel_result.get("retcode") == 0:
            items = steel_result.get("data", {}).get("info_list", [])
            print(f"   找到 {len(items)} 条相关知识库")
            for item in items[:5]:
                print(f"   - {item.get('name', item.get('title', 'N/A'))}")
        
        print("\n[3] 搜索永磁体...")
        pm_result = search_kb("永磁体 钕铁硼")
        if pm_result.get("code") == 0 or pm_result.get("retcode") == 0:
            items = pm_result.get("data", {}).get("info_list", [])
            print(f"   找到 {len(items)} 条相关知识库")
        
        # 浏览硅钢/磁钢材料库
        print("\n[4] 浏览「硅钢/磁钢材料库」...")
        for kb in kbs:
            if "硅钢" in kb.get("name", "") or "磁钢" in kb.get("name", ""):
                kb_id = kb.get("knowledge_base_id", kb.get("id", ""))
                print(f"   浏览: {kb.get('name')}")
                
                content = get_kb_content(kb_id)
                if content.get("code") == 0 or content.get("retcode") == 0:
                    items = content.get("data", {}).get("knowledge_list", content.get("data", {}).get("info_list", []))
                    print(f"   内容数量: {len(items)}")
                    
                    for item in items[:20]:
                        title = item.get("title", item.get("name", ""))
                        content_text = item.get("content", item.get("highlight_content", ""))[:300]
                        print(f"\n   --- {title} ---")
                        if content_text:
                            print(f"   {content_text}...")
        
        print("\n" + "=" * 60)
        print("材料数据收集完成")
        print("=" * 60)
    else:
        print(f"获取知识库失败: {kb_result}")
