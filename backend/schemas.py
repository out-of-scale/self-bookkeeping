"""
Pydantic 请求/响应模型
"""
from pydantic import BaseModel, Field
from typing import Optional


# ========== 请求模型 ==========

class UploadReceiptRequest(BaseModel):
    """上传账单截图请求"""
    image_base64: str = Field(..., description="图片的 Base64 编码字符串")


class UpdateReceiptRequest(BaseModel):
    """编辑账单请求"""
    date: Optional[str] = None
    merchant: Optional[str] = None
    amount: Optional[float] = None
    type: Optional[str] = None
    category: Optional[str] = None


class ManualReceiptRequest(BaseModel):
    """手动添加账单请求"""
    date: str = Field(..., description="交易日期 YYYY-MM-DD")
    merchant: str = Field(..., description="商家名称")
    amount: float = Field(..., description="金额")
    type: str = Field(default="expense", description="income 或 expense")
    category: str = Field(default="其他", description="分类")


# ========== 响应模型 ==========

class ReceiptData(BaseModel):
    """单条账单数据"""
    id: int
    date: str
    merchant: str
    amount: float
    type: str
    category: str
    created_at: Optional[str] = None


class UploadReceiptResponse(BaseModel):
    """上传账单响应"""
    success: bool
    message: str
    data: Optional[ReceiptData] = None


class CategoryStat(BaseModel):
    """分类统计"""
    category: str
    amount: float
    percentage: float


class DailyStat(BaseModel):
    """每日统计"""
    date: str
    amount: float


class MonthStatsResponse(BaseModel):
    """月度统计响应"""
    total_expense: float
    total_income: float
    balance: float
    by_category: list[CategoryStat]
    daily_expense: list[DailyStat]


class MonthlySummary(BaseModel):
    """月度汇总"""
    month: int
    income: float
    expense: float
    balance: float


class YearlyResponse(BaseModel):
    """年度统计响应"""
    year: int
    monthly: list[MonthlySummary]


class ReceiptListResponse(BaseModel):
    """账单列表响应"""
    total: int
    page: int
    page_size: int
    items: list[ReceiptData]


class NetWorthResponse(BaseModel):
    """净资产总额响应"""
    net_worth: float
    base_worth: float
    total_income: float
    total_expense: float


class UpdateNetWorthRequest(BaseModel):
    """更新净资产请求"""
    current_net_worth: float = Field(..., description="当前实际拥有的总资产")
