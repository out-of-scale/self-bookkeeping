"""
智谱 GLM-4.6V-Flash AI 服务封装
"""
import os
import json
import re
import base64
import httpx
from datetime import date

ZHIPU_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"


def _get_api_key() -> str:
    """延迟读取 API Key，确保 load_dotenv() 已执行"""
    return os.getenv("ZHIPU_API_KEY", "")


def _detect_mime(b64_str: str) -> str:
    """从 Base64 数据的前几个字节检测图片 MIME 类型"""
    try:
        header = base64.b64decode(b64_str[:32])
        if header[:3] == b'\xff\xd8\xff':
            return "image/jpeg"
        elif header[:8] == b'\x89PNG\r\n\x1a\n':
            return "image/png"
        elif header[:4] == b'RIFF' and header[8:12] == b'WEBP':
            return "image/webp"
    except Exception:
        pass
    return "image/jpeg"  # 默认 JPEG（手机截图最常见）

RECEIPT_PROMPT = """你是一个专业的账单识别助手。请分析这张支付截图，提取以下信息并以纯 JSON 格式返回：
{
  "date": "YYYY-MM-DD 格式的交易日期",
  "merchant": "商家名称",
  "amount": 数字格式的金额（不带货币符号）,
  "type": "income 或 expense",
  "category": "从以下分类中选择一个：餐饮、交通、购物、娱乐、医疗、教育、住房、通讯、其他"
}
注意：
1. 只返回 JSON，不要任何其他文字
2. 金额必须是数字，不要包含 ¥ 或 元
3. 日期如果无法从图中识别，使用今天的日期
4. 如果是红包、转账收入等，type 为 income
5. 如果图片中包含多笔交易，只提取金额最大的那笔"""

# 合法分类列表
VALID_CATEGORIES = {"餐饮", "交通", "购物", "娱乐", "医疗", "教育", "住房", "通讯", "其他"}
VALID_TYPES = {"income", "expense"}


async def recognize_receipt(image_base64: str) -> dict:
    """
    调用智谱 GLM-4.6V-Flash 识别支付截图

    Args:
        image_base64: 图片 Base64 编码（可带或不带 data:image/... 前缀）

    Returns:
        dict: 包含 date, merchant, amount, type, category 的字典

    Raises:
        ValueError: AI 返回无法解析时
        httpx.HTTPError: 网络请求失败时
    """
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("未配置 ZHIPU_API_KEY，请在 .env 文件中设置")

    # 确保 Base64 有正确的前缀，自动检测图片格式
    if not image_base64.startswith("data:image"):
        mime = _detect_mime(image_base64)
        image_base64 = f"data:{mime};base64,{image_base64}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "GLM-4.6V-Flash",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": RECEIPT_PROMPT},
                    {"type": "image_url", "image_url": {"url": image_base64}},
                ],
            }
        ],
        "temperature": 0.1,  # 低温度确保输出稳定
        "max_tokens": 2048,  # 推理模型需要大量 token 用于思考 + 输出
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(ZHIPU_API_URL, headers=headers, json=payload)
        response.raise_for_status()

    result = response.json()
    message = result["choices"][0]["message"]
    raw_content = message.get("content", "") or ""

    # GLM-4.6V-Flash 是推理模型，content 可能为空，JSON 在 reasoning_content 中
    if not raw_content.strip():
        reasoning = message.get("reasoning_content", "")
        if reasoning:
            raw_content = reasoning

    if not raw_content.strip():
        raise ValueError(f"AI 返回内容为空，原始响应: {json.dumps(result, ensure_ascii=False)[:500]}")

    # 解析并清洗数据
    return _parse_and_clean(raw_content)


def _parse_and_clean(raw_content: str) -> dict:
    """
    解析 AI 返回的内容并清洗为标准格式

    Args:
        raw_content: AI 原始返回字符串

    Returns:
        dict: 清洗后的结构化数据，额外包含 raw_response 字段
    """
    # 尝试提取 JSON（AI 可能返回带 markdown 代码块的 JSON）
    json_match = re.search(r'\{[^{}]*\}', raw_content, re.DOTALL)
    if not json_match:
        raise ValueError(f"AI 返回内容中未找到 JSON: {raw_content}")

    try:
        data = json.loads(json_match.group())
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败: {e}, 原始内容: {raw_content}")

    # 验证必要字段
    required_fields = ["date", "merchant", "amount", "type", "category"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"AI 返回缺少字段: {field}, 数据: {data}")

    # 清洗 amount：确保是数字
    amount = data["amount"]
    if isinstance(amount, str):
        amount = float(re.sub(r'[¥￥元,]', '', amount))
    data["amount"] = round(float(amount), 2)

    # 清洗 type
    if data["type"] not in VALID_TYPES:
        data["type"] = "expense"  # 默认支出

    # 清洗 category
    if data["category"] not in VALID_CATEGORIES:
        data["category"] = "其他"

    # 清洗 date：确保格式正确
    try:
        from datetime import datetime
        datetime.strptime(data["date"], "%Y-%m-%d")
    except (ValueError, TypeError):
        data["date"] = date.today().isoformat()

    # 保留原始返回用于调试
    data["raw_response"] = raw_content

    return data
