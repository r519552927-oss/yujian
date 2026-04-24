# -*- coding: utf-8 -*-
"""从IMA知识库获取电机材料数据"""

import urllib.request
import urllib.parse
import json

# IMA凭证
CLIENT_ID = "34c0f65a6c4e544e9a6f29bb637da9ea"
API_KEY = "+oddXHKF4LxPfWoo8HnFIYaLX6Sy+aQJYFeVVrlnURivNVlX0HnWUwgGv+yR+XAVhPtzjHxttg=="

def query_ima(query, knowledge_base_id=None):
    """查询IMA知识库"""
    url = "https://ima.qq.com/openapi/wiki/v1/search_knowledge_base"
    
    headers = {
        "ima-openapi-clientid": CLIENT_ID,
        "ima-openapi-apikey": API_KEY,
        "Content-Type": "application/json; charset=utf-8"
    }
    
    body = {
        "query": query,
        "cursor": "",
        "limit": 20
    }
    
    if knowledge_base_id:
        body["knowledge_base_id"] = knowledge_base_id
    
    req = urllib.request.Request(url, 
                                  data=json.dumps(body).encode('utf-8'),
                                  headers=headers,
                                  method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

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
        "limit": 50
    }
    
    req = urllib.request.Request(url,
                                  data=json.dumps(body).encode('utf-8'),
                                  headers=headers,
                                  method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("=" * 60)
    print("从IMA知识库获取电机材料数据")
    print("=" * 60)
    
    # 搜索铁心材料知识库
    print("\n1. 搜索硅钢/磁钢材料库...")
    result = query_ima("硅钢片 材料参数 B-H曲线 牌号")
    print(f"   结果: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
    
    # 搜索永磁体材料
    print("\n2. 搜索永磁体材料...")
    result2 = query_ima("钕铁硼 N35 N42 N52 性能参数 剩磁 矫顽力")
    print(f"   结果: {json.dumps(result2, ensure_ascii=False, indent=2)[:500]}...")
    
    # 获取磁钢材料库详细内容
    print("\n3. 获取磁钢材料库详细内容...")
    # 先列出所有知识库
    result3 = query_ima("N35 N38 N40 N42 N45 N48 N50 N52")
    print(f"   结果: {json.dumps(result3, ensure_ascii=False, indent=2)[:800]}...")
