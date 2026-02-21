"""
SQLAlchemy 数据模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Index
from database import Base


class Receipt(Base):
    """账单记录表"""
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String(10), nullable=False, index=True)          # 'YYYY-MM-DD'
    merchant = Column(String(100), nullable=False)                  # 商家名称
    amount = Column(Float, nullable=False)                          # 金额
    type = Column(String(10), nullable=False, index=True)           # 'income' | 'expense'
    category = Column(String(20), nullable=False, index=True)       # 分类
    raw_response = Column(Text, nullable=True)                      # AI 原始返回
    image_hash = Column(String(32), nullable=True, unique=True)     # 图片 MD5
    created_at = Column(DateTime, default=datetime.now)             # 入库时间

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "merchant": self.merchant,
            "amount": self.amount,
            "type": self.type,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
