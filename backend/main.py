"""
个人记账系统 — FastAPI 后端主入口
"""
import os
import hashlib
import base64
from datetime import date, datetime
from typing import Optional
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()  # 加载 .env 文件（必须在其他模块导入前）

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from database import get_db, init_db
from models import Receipt
from schemas import (
    UploadReceiptRequest, UploadReceiptResponse, ReceiptData,
    UpdateReceiptRequest, ManualReceiptRequest,
    MonthStatsResponse, CategoryStat, DailyStat,
    YearlyResponse, MonthlySummary,
    ReceiptListResponse,
)
from ai_service import recognize_receipt


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库"""
    init_db()
    yield


app = FastAPI(
    title="个人记账系统 API",
    description="接收支付截图，AI 识别后入库，并提供统计查询接口",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置 — 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请改为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 上传接口 ====================

@app.post("/api/upload_receipt", response_model=UploadReceiptResponse)
async def upload_receipt(req: UploadReceiptRequest, db: Session = Depends(get_db)):
    """
    接收支付截图 Base64，调用 AI 识别并入库
    """
    try:
        # 1. 计算图片哈希用于去重
        raw_b64 = req.image_base64
        if "," in raw_b64:
            raw_b64 = raw_b64.split(",", 1)[1]
        try:
            image_bytes = base64.b64decode(raw_b64)
        except Exception:
            raise HTTPException(status_code=400, detail="Base64 解码失败，请检查图片数据")

        image_hash = hashlib.md5(image_bytes).hexdigest()

        # 2. 检查是否重复提交
        existing = db.query(Receipt).filter(Receipt.image_hash == image_hash).first()
        if existing:
            return UploadReceiptResponse(
                success=True,
                message=f"⚠️ 该账单已存在：{existing.merchant} - {existing.amount}元",
                data=ReceiptData(**existing.to_dict()),
            )

        # 3. 调用 AI 识别
        parsed = await recognize_receipt(req.image_base64)

        # 4. 入库
        receipt = Receipt(
            date=parsed["date"],
            merchant=parsed["merchant"],
            amount=parsed["amount"],
            type=parsed["type"],
            category=parsed["category"],
            raw_response=parsed.get("raw_response"),
            image_hash=image_hash,
        )
        db.add(receipt)
        db.commit()
        db.refresh(receipt)

        # 5. 构建友好消息
        type_emoji = "💰" if receipt.type == "income" else "💸"
        message = f"✅ 记账成功：{receipt.merchant} - {type_emoji}{receipt.amount}元"

        return UploadReceiptResponse(
            success=True,
            message=message,
            data=ReceiptData(**receipt.to_dict()),
        )

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


# ==================== 统计接口 ====================

@app.get("/api/get_stats", response_model=MonthStatsResponse)
def get_stats(
    year: int = Query(default=None, description="年份"),
    month: int = Query(default=None, ge=1, le=12, description="月份"),
    db: Session = Depends(get_db),
):
    """
    获取月度统计数据：总收支、分类占比、每日支出
    """
    today = date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    # 构建日期范围 YYYY-MM-01 到 YYYY-MM-31
    month_prefix = f"{year:04d}-{month:02d}"

    records = db.query(Receipt).filter(Receipt.date.like(f"{month_prefix}%")).all()

    total_expense = sum(r.amount for r in records if r.type == "expense")
    total_income = sum(r.amount for r in records if r.type == "income")

    # 分类统计（仅支出）
    category_map: dict[str, float] = {}
    for r in records:
        if r.type == "expense":
            category_map[r.category] = category_map.get(r.category, 0) + r.amount

    by_category = []
    for cat, amt in sorted(category_map.items(), key=lambda x: -x[1]):
        pct = round(amt / total_expense * 100, 1) if total_expense > 0 else 0
        by_category.append(CategoryStat(category=cat, amount=round(amt, 2), percentage=pct))

    # 每日支出
    daily_map: dict[str, float] = {}
    for r in records:
        if r.type == "expense":
            daily_map[r.date] = daily_map.get(r.date, 0) + r.amount

    daily_expense = [
        DailyStat(date=d, amount=round(a, 2))
        for d, a in sorted(daily_map.items())
    ]

    return MonthStatsResponse(
        total_expense=round(total_expense, 2),
        total_income=round(total_income, 2),
        balance=round(total_income - total_expense, 2),
        by_category=by_category,
        daily_expense=daily_expense,
    )


# ==================== 年度接口 ====================

@app.get("/api/get_yearly", response_model=YearlyResponse)
def get_yearly(
    year: int = Query(default=None, description="年份"),
    db: Session = Depends(get_db),
):
    """
    获取年度按月汇总数据
    """
    if year is None:
        year = date.today().year

    year_prefix = f"{year:04d}"
    records = db.query(Receipt).filter(Receipt.date.like(f"{year_prefix}%")).all()

    # 按月汇总
    monthly_data: dict[int, dict] = {}
    for m in range(1, 13):
        monthly_data[m] = {"income": 0.0, "expense": 0.0}

    for r in records:
        try:
            m = int(r.date[5:7])
            monthly_data[m][r.type] += r.amount
        except (ValueError, KeyError):
            pass

    monthly = [
        MonthlySummary(
            month=m,
            income=round(d["income"], 2),
            expense=round(d["expense"], 2),
            balance=round(d["income"] - d["expense"], 2),
        )
        for m, d in sorted(monthly_data.items())
    ]

    return YearlyResponse(year=year, monthly=monthly)


# ==================== 明细接口 ====================

@app.get("/api/receipts", response_model=ReceiptListResponse)
def get_receipts(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页条数"),
    start_date: Optional[str] = Query(default=None, description="起始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(default=None, description="结束日期 YYYY-MM-DD"),
    category: Optional[str] = Query(default=None, description="分类筛选"),
    type: Optional[str] = Query(default=None, description="income / expense"),
    merchant: Optional[str] = Query(default=None, description="商家名称搜索"),
    db: Session = Depends(get_db),
):
    """
    分页查询账单明细，支持多维度筛选
    """
    query = db.query(Receipt)

    if start_date:
        query = query.filter(Receipt.date >= start_date)
    if end_date:
        query = query.filter(Receipt.date <= end_date)
    if category:
        query = query.filter(Receipt.category == category)
    if type:
        query = query.filter(Receipt.type == type)
    if merchant:
        query = query.filter(Receipt.merchant.contains(merchant))

    total = query.count()
    items = (
        query.order_by(Receipt.date.desc(), Receipt.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return ReceiptListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[ReceiptData(**r.to_dict()) for r in items],
    )


# ==================== 编辑/删除/手动添加 ====================

@app.put("/api/receipts/{receipt_id}", response_model=UploadReceiptResponse)
def update_receipt(receipt_id: int, req: UpdateReceiptRequest, db: Session = Depends(get_db)):
    """编辑账单记录（修正 AI 识别错误）"""
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="记录不存在")

    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(receipt, key, value)
    db.commit()
    db.refresh(receipt)

    return UploadReceiptResponse(
        success=True,
        message=f"✅ 已更新：{receipt.merchant} ¥{receipt.amount}",
        data=ReceiptData(**receipt.to_dict()),
    )


@app.delete("/api/receipts/{receipt_id}")
def delete_receipt(receipt_id: int, db: Session = Depends(get_db)):
    """删除账单记录"""
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="记录不存在")

    merchant = receipt.merchant
    db.delete(receipt)
    db.commit()
    return {"success": True, "message": f"🗑️ 已删除：{merchant}"}


@app.post("/api/receipts/manual", response_model=UploadReceiptResponse)
def manual_add(req: ManualReceiptRequest, db: Session = Depends(get_db)):
    """手动添加账单（不走 AI）"""
    receipt = Receipt(
        date=req.date,
        merchant=req.merchant,
        amount=req.amount,
        type=req.type,
        category=req.category,
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)

    type_emoji = "💰" if receipt.type == "income" else "💸"
    return UploadReceiptResponse(
        success=True,
        message=f"✅ 手动记账：{receipt.merchant} - {type_emoji}{receipt.amount}元",
        data=ReceiptData(**receipt.to_dict()),
    )


# ==================== 健康检查 ====================

@app.get("/api/health")
def health_check():
    return {"status": "ok", "time": datetime.now().isoformat()}


# ==================== 启动入口 ====================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
