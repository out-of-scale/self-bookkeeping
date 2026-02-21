"""
测试脚本：插入模拟数据 + 测试 AI 识别
"""
import httpx
import json
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    r = httpx.get(f"{BASE_URL}/api/health")
    print(f"[健康检查] {r.status_code}: {r.json()}")
    return r.status_code == 200

def insert_test_data():
    """
    通过直接操作数据库插入测试数据（独立连接）
    """
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "bookkeeping.db")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    db = Session()
    
    from models import Receipt
    
    # 检查是否已有数据
    count = db.query(Receipt).count()
    if count > 0:
        print(f"[跳过] 数据库已有 {count} 条记录")
        db.close()
        return
    
    test_records = [
        Receipt(date='2026-02-21', merchant='瑞幸咖啡', amount=16.5, type='expense', category='餐饮'),
        Receipt(date='2026-02-20', merchant='滴滴出行', amount=23.0, type='expense', category='交通'),
        Receipt(date='2026-02-19', merchant='淘宝', amount=199.0, type='expense', category='购物'),
        Receipt(date='2026-02-18', merchant='公司工资', amount=12000.0, type='income', category='其他'),
        Receipt(date='2026-02-15', merchant='美团外卖', amount=35.5, type='expense', category='餐饮'),
        Receipt(date='2026-02-14', merchant='电影票', amount=45.0, type='expense', category='娱乐'),
        Receipt(date='2026-02-10', merchant='中国移动', amount=58.0, type='expense', category='通讯'),
        Receipt(date='2026-01-20', merchant='美团外卖', amount=42.0, type='expense', category='餐饮'),
        Receipt(date='2026-01-15', merchant='加油站', amount=300.0, type='expense', category='交通'),
        Receipt(date='2026-01-10', merchant='1月工资', amount=12000.0, type='income', category='其他'),
    ]
    
    for r in test_records:
        db.add(r)
    db.commit()
    print(f"[成功] 插入 {len(test_records)} 条测试数据")
    db.close()

def test_stats():
    """测试统计接口"""
    r = httpx.get(f"{BASE_URL}/api/get_stats", params={"year": 2026, "month": 2})
    data = r.json()
    print(f"\n[月度统计] 2月")
    print(f"  总支出: ¥{data['total_expense']}")
    print(f"  总收入: ¥{data['total_income']}")
    print(f"  结余:   ¥{data['balance']}")
    print(f"  分类:   {json.dumps(data['by_category'], ensure_ascii=False, indent=4)}")

def test_yearly():
    """测试年度接口"""
    r = httpx.get(f"{BASE_URL}/api/get_yearly", params={"year": 2026})
    data = r.json()
    print(f"\n[年度统计] {data['year']}年")
    for m in data['monthly']:
        if m['income'] > 0 or m['expense'] > 0:
            print(f"  {m['month']}月: 收入 ¥{m['income']} / 支出 ¥{m['expense']} / 结余 ¥{m['balance']}")

def test_receipts():
    """测试明细接口"""
    r = httpx.get(f"{BASE_URL}/api/receipts", params={"page": 1, "page_size": 5})
    data = r.json()
    print(f"\n[账单明细] 共 {data['total']} 条, 第 {data['page']} 页")
    for item in data['items']:
        emoji = '💰' if item['type'] == 'income' else '💸'
        print(f"  {emoji} {item['date']} {item['merchant']} ¥{item['amount']} [{item['category']}]")

def test_ai_upload():
    """
    测试 AI 识别接口（用一张简单的模拟图片）
    """
    from PIL import Image, ImageDraw, ImageFont
    import base64
    import io
    
    # 创建模拟支付截图
    img = Image.new('RGB', (400, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("msyh.ttc", 20)
        font_small = ImageFont.truetype("msyh.ttc", 14)
    except:
        font = ImageFont.load_default()
        font_small = font
    
    draw.text((120, 20), "支付成功", fill=(0, 0, 0), font=font)
    draw.text((50, 80), "商户: 星巴克咖啡", fill=(51, 51, 51), font=font_small)
    draw.text((50, 120), "金额: ¥38.00", fill=(51, 51, 51), font=font_small)
    draw.text((50, 160), "时间: 2026-02-21 12:00:00", fill=(51, 51, 51), font=font_small)
    draw.text((50, 200), "支付方式: 微信支付", fill=(51, 51, 51), font=font_small)
    draw.text((50, 240), "订单号: 2026022112345678", fill=(153, 153, 153), font=font_small)
    
    # 转 Base64
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode()
    
    print("\n[AI 识别] 发送模拟支付截图...")
    r = httpx.post(
        f"{BASE_URL}/api/upload_receipt",
        json={"image_base64": b64},
        timeout=30.0,
    )
    
    if r.status_code == 200:
        data = r.json()
        print(f"  ✅ {data['message']}")
        print(f"  数据: {json.dumps(data['data'], ensure_ascii=False, indent=4)}")
    else:
        print(f"  ❌ 状态码: {r.status_code}")
        print(f"  错误: {r.text}")


if __name__ == "__main__":
    print("=" * 50)
    print("个人记账系统 — 全链路测试")
    print("=" * 50)
    
    # 1. 健康检查
    if not test_health():
        print("后端未启动！请先运行 python main.py")
        sys.exit(1)
    
    # 2. 插入测试数据
    insert_test_data()
    
    # 3. 测试查询接口
    test_stats()
    test_yearly()
    test_receipts()
    
    # 4. 测试 AI 识别
    try:
        test_ai_upload()
    except ImportError:
        print("\n[跳过 AI 测试] 需要安装 Pillow: pip install Pillow")
    except Exception as e:
        print(f"\n[AI 测试失败] {e}")
    
    print("\n" + "=" * 50)
    print("测试完成！请打开 http://localhost:5173 查看前端效果")
    print("=" * 50)
