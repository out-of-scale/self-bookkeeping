"""测试：通过后端API测试真实截图识别"""
import base64
import httpx
import json

IMAGE_PATH = r"e:\self_bookkeeping\d4b8164d1aa87a885cb9f0bfc0ea3774.jpg"
API_URL = "http://localhost:8000/api/upload_receipt"

print("读取图片...")
with open(IMAGE_PATH, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
print(f"Base64 长度: {len(b64)} 字符")

print("通过后端 API 发送...")
import sys; sys.stdout.flush()

r = httpx.post(API_URL, json={"image_base64": b64}, timeout=120.0)
print(f"状态码: {r.status_code}")
print(json.dumps(r.json(), ensure_ascii=False, indent=2))
