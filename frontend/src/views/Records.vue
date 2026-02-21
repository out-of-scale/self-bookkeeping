<template>
  <div class="page-container">
    <div class="page-header">
      <h2>📋 账单明细</h2>
      <p class="subtitle">管理所有交易记录</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <button class="add-btn" @click="showAddDialog = true">＋ 手动记账</button>
      <div class="filter-group">
        <select v-model="filters.type" @change="fetchData" class="filter-select">
          <option value="">全部类型</option>
          <option value="expense">支出</option>
          <option value="income">收入</option>
        </select>
        <select v-model="filters.category" @change="fetchData" class="filter-select">
          <option value="">全部分类</option>
          <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
        </select>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <input
        v-model="searchText"
        placeholder="🔍 搜索商家名称..."
        class="search-input"
        @input="debouncedSearch"
      />
    </div>

    <!-- 列表 -->
    <div class="records-list" v-loading="loading">
      <div v-if="receipts.length > 0">
        <div
          class="record-card"
          v-for="item in receipts"
          :key="item.id"
        >
          <div class="record-main" @click="openEdit(item)">
            <div class="record-icon" :style="{ background: getCategoryColor(item.category) }">
              {{ getCategoryIcon(item.category) }}
            </div>
            <div class="record-info">
              <div class="record-merchant">{{ item.merchant }}</div>
              <div class="record-meta">
                {{ formatDate(item.date) }} · {{ item.category }}
                <span class="record-type-badge" :class="item.type">
                  {{ item.type === 'expense' ? '支出' : '收入' }}
                </span>
              </div>
            </div>
            <div class="record-amount" :class="item.type">
              {{ item.type === 'expense' ? '-' : '+' }}¥{{ formatMoney(item.amount) }}
            </div>
          </div>
          <div class="record-actions">
            <button class="action-icon edit" @click="openEdit(item)" title="编辑">✏️</button>
            <button class="action-icon delete" @click="confirmDelete(item)" title="删除">🗑️</button>
          </div>
        </div>
      </div>
      <div v-else class="empty-state">
        <div class="emoji">📭</div>
        <div class="title">暂无记录</div>
        <div class="desc">使用快捷指令或手动添加开始记账</div>
      </div>

      <!-- 分页 -->
      <div v-if="totalRecords > pageSize" class="pagination">
        <button class="page-btn" :disabled="page <= 1" @click="page--; fetchData()">上一页</button>
        <span class="page-info">{{ page }} / {{ Math.ceil(totalRecords / pageSize) }}</span>
        <button class="page-btn" :disabled="page * pageSize >= totalRecords" @click="page++; fetchData()">下一页</button>
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <div v-if="showEditDialog" class="dialog-overlay" @click.self="showEditDialog = false">
      <div class="dialog-box">
        <div class="dialog-header">
          <h3>编辑记录</h3>
          <button class="close-btn" @click="showEditDialog = false">✕</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>商家</label>
            <input v-model="editForm.merchant" class="form-input" />
          </div>
          <div class="form-group">
            <label>金额</label>
            <input v-model.number="editForm.amount" type="number" step="0.01" class="form-input" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>日期</label>
              <input v-model="editForm.date" type="date" class="form-input" />
            </div>
            <div class="form-group">
              <label>类型</label>
              <select v-model="editForm.type" class="form-input">
                <option value="expense">支出</option>
                <option value="income">收入</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>分类</label>
            <select v-model="editForm.category" class="form-input">
              <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showEditDialog = false">取消</button>
          <button class="btn-primary" @click="saveEdit" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 添加弹窗 -->
    <div v-if="showAddDialog" class="dialog-overlay" @click.self="showAddDialog = false">
      <div class="dialog-box">
        <div class="dialog-header">
          <h3>手动记账</h3>
          <button class="close-btn" @click="showAddDialog = false">✕</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>商家</label>
            <input v-model="addForm.merchant" class="form-input" placeholder="例如：星巴克" />
          </div>
          <div class="form-group">
            <label>金额</label>
            <input v-model.number="addForm.amount" type="number" step="0.01" class="form-input" placeholder="0.00" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>日期</label>
              <input v-model="addForm.date" type="date" class="form-input" />
            </div>
            <div class="form-group">
              <label>类型</label>
              <select v-model="addForm.type" class="form-input">
                <option value="expense">支出</option>
                <option value="income">收入</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>分类</label>
            <select v-model="addForm.category" class="form-input">
              <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showAddDialog = false">取消</button>
          <button class="btn-primary" @click="saveAdd" :disabled="saving">
            {{ saving ? '添加中...' : '添加' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除确认 -->
    <div v-if="showDeleteDialog" class="dialog-overlay" @click.self="showDeleteDialog = false">
      <div class="dialog-box small">
        <div class="dialog-header">
          <h3>确认删除</h3>
          <button class="close-btn" @click="showDeleteDialog = false">✕</button>
        </div>
        <div class="dialog-body">
          <p>确定删除「{{ deleteTarget?.merchant }}」的 ¥{{ deleteTarget?.amount }} 记录吗？</p>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="showDeleteDialog = false">取消</button>
          <button class="btn-danger" @click="doDelete" :disabled="saving">
            {{ saving ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getReceipts, updateReceipt, deleteReceipt, manualAddReceipt } from '../api'

const loading = ref(false)
const saving = ref(false)
const receipts = ref([])
const page = ref(1)
const pageSize = 20
const totalRecords = ref(0)
const searchText = ref('')
let searchTimer = null

// 筛选
const filters = ref({ type: '', category: '' })
const categories = ['餐饮', '交通', '购物', '娱乐', '医疗', '教育', '住房', '通讯', '其他']

// 弹窗
const showEditDialog = ref(false)
const showAddDialog = ref(false)
const showDeleteDialog = ref(false)
const editForm = ref({})
const editId = ref(null)
const deleteTarget = ref(null)

const today = new Date()
const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
const addForm = ref({
  merchant: '', amount: null, date: todayStr,
  type: 'expense', category: '其他',
})

const categoryIcons = {
  '餐饮': '🍜', '交通': '🚗', '购物': '🛍️', '娱乐': '🎮',
  '医疗': '🏥', '教育': '📚', '住房': '🏠', '通讯': '📱', '其他': '📦',
}
const categoryColors = {
  '餐饮': 'rgba(99,102,241,0.2)', '交通': 'rgba(59,130,246,0.2)', '购物': 'rgba(244,63,94,0.2)',
  '娱乐': 'rgba(139,92,246,0.2)', '医疗': 'rgba(16,185,129,0.2)', '教育': 'rgba(245,158,11,0.2)',
  '住房': 'rgba(20,184,166,0.2)', '通讯': 'rgba(236,72,153,0.2)', '其他': 'rgba(100,116,139,0.2)',
}
function getCategoryIcon(cat) { return categoryIcons[cat] || '📦' }
function getCategoryColor(cat) { return categoryColors[cat] || 'rgba(100,116,139,0.2)' }

function formatMoney(n) {
  return Number(n || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
function formatDate(dateStr) {
  if (!dateStr) return ''
  const parts = dateStr.split('-')
  return `${parts[0]}-${parts[1]}-${parts[2]}`
}

function debouncedSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; fetchData() }, 300)
}

async function fetchData() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize }
    if (filters.value.type) params.type = filters.value.type
    if (filters.value.category) params.category = filters.value.category
    if (searchText.value) params.merchant = searchText.value
    const res = await getReceipts(params)
    receipts.value = res.data.items
    totalRecords.value = res.data.total
  } catch (e) {
    console.error('Failed to load records:', e)
  } finally {
    loading.value = false
  }
}

function openEdit(item) {
  editId.value = item.id
  editForm.value = { ...item }
  showEditDialog.value = true
}

async function saveEdit() {
  saving.value = true
  try {
    await updateReceipt(editId.value, {
      date: editForm.value.date,
      merchant: editForm.value.merchant,
      amount: editForm.value.amount,
      type: editForm.value.type,
      category: editForm.value.category,
    })
    showEditDialog.value = false
    fetchData()
  } catch (e) {
    alert('保存失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}

function confirmDelete(item) {
  deleteTarget.value = item
  showDeleteDialog.value = true
}

async function doDelete() {
  saving.value = true
  try {
    await deleteReceipt(deleteTarget.value.id)
    showDeleteDialog.value = false
    fetchData()
  } catch (e) {
    alert('删除失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}

async function saveAdd() {
  if (!addForm.value.merchant || !addForm.value.amount) {
    alert('请填写商家和金额')
    return
  }
  saving.value = true
  try {
    await manualAddReceipt(addForm.value)
    showAddDialog.value = false
    addForm.value = { merchant: '', amount: null, date: todayStr, type: 'expense', category: '其他' }
    page.value = 1
    fetchData()
  } catch (e) {
    alert('添加失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
/* 操作栏 */
.action-bar {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 10px; flex-wrap: wrap; gap: 8px;
}
.add-btn {
  padding: 8px 16px; border-radius: 8px; border: none;
  background: var(--primary); color: #fff; font-weight: 500;
  font-size: 13px; cursor: pointer; transition: opacity 0.2s;
}
.add-btn:hover { opacity: 0.85; }
.filter-group { display: flex; gap: 6px; }
.filter-select {
  padding: 7px 10px; border-radius: 8px;
  border: 1px solid var(--border-color); background: var(--bg-card);
  color: var(--text-primary); font-size: 12px; cursor: pointer;
}
.filter-select:focus { border-color: var(--primary); outline: none; }

/* 搜索栏 */
.search-bar { margin-bottom: 12px; }
.search-input {
  width: 100%; padding: 10px 14px; border-radius: 10px;
  border: 1px solid var(--border-color); background: var(--bg-card);
  color: var(--text-primary); font-size: 13px; transition: border-color 0.2s;
}
.search-input:focus { border-color: var(--primary); outline: none; }
.search-input::placeholder { color: var(--text-muted); }

/* 记录卡片 */
.record-card {
  background: var(--bg-card); border-radius: 10px; border: 1px solid var(--border-color);
  margin-bottom: 6px; overflow: hidden;
}
.record-main {
  display: flex; align-items: center; padding: 12px 14px; gap: 10px; cursor: pointer;
}
.record-icon {
  width: 36px; height: 36px; border-radius: 9px;
  display: flex; align-items: center; justify-content: center;
  font-size: 17px; flex-shrink: 0;
}
.record-info { flex: 1; min-width: 0; }
.record-merchant { font-weight: 500; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.record-meta { font-size: 11px; color: var(--text-muted); margin-top: 2px; display: flex; align-items: center; gap: 5px; }
.record-type-badge {
  padding: 1px 5px; border-radius: 4px; font-size: 10px; font-weight: 500;
}
.record-type-badge.expense { background: rgba(240,112,112,0.12); color: var(--danger); }
.record-type-badge.income { background: rgba(91,217,164,0.12); color: var(--success); }
.record-amount { font-weight: 600; font-size: 14px; white-space: nowrap; font-variant-numeric: tabular-nums; }
.record-amount.expense { color: var(--danger); }
.record-amount.income { color: var(--success); }
.record-actions {
  display: flex; justify-content: flex-end; padding: 0 10px 8px; gap: 6px;
}
.action-icon {
  width: 28px; height: 28px; border-radius: 6px; border: none;
  font-size: 13px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: background 0.15s; background: transparent;
}
.action-icon.edit:hover { background: rgba(124,131,247,0.12); }
.action-icon.delete:hover { background: rgba(240,112,112,0.12); }

/* 分页 */
.pagination {
  display: flex; justify-content: center; align-items: center; gap: 14px;
  padding: 16px 0;
}
.page-btn {
  padding: 6px 14px; border-radius: 6px;
  border: 1px solid var(--border-color); background: transparent;
  color: var(--text-secondary); font-size: 12px; cursor: pointer;
}
.page-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.page-btn:not(:disabled):hover { color: var(--primary); border-color: var(--primary); }
.page-info { font-size: 12px; color: var(--text-muted); }

/* 弹窗 */
.dialog-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  z-index: 2000; padding: 20px;
}
.dialog-box {
  background: var(--bg-secondary); border-radius: 14px;
  width: 100%; max-width: 400px;
  border: 1px solid var(--border-color);
}
.dialog-box.small { max-width: 340px; }
.dialog-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 18px 20px 10px;
}
.dialog-header h3 { font-size: 16px; font-weight: 600; }
.close-btn {
  width: 28px; height: 28px; border-radius: 7px; border: none;
  background: transparent; color: var(--text-muted);
  font-size: 14px; cursor: pointer;
}
.close-btn:hover { background: var(--bg-card-hover); }
.dialog-body { padding: 6px 20px 16px; }
.dialog-body p { color: var(--text-secondary); font-size: 13px; line-height: 1.5; }
.dialog-footer {
  display: flex; justify-content: flex-end; gap: 8px;
  padding: 10px 20px 18px;
}

/* 表单 */
.form-group { margin-bottom: 12px; }
.form-group label { display: block; font-size: 12px; font-weight: 500; color: var(--text-muted); margin-bottom: 4px; }
.form-input {
  width: 100%; padding: 9px 11px; border-radius: 8px;
  border: 1px solid var(--border-color); background: var(--bg-card);
  color: var(--text-primary); font-size: 13px;
}
.form-input:focus { border-color: var(--primary); outline: none; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

/* 按钮 */
.btn-cancel {
  padding: 8px 16px; border-radius: 8px;
  border: 1px solid var(--border-color); background: transparent;
  color: var(--text-muted); font-size: 13px; cursor: pointer;
}
.btn-cancel:hover { color: var(--text-secondary); }
.btn-primary {
  padding: 8px 16px; border-radius: 8px; border: none;
  background: var(--primary); color: #fff; font-weight: 500;
  font-size: 13px; cursor: pointer;
}
.btn-primary:hover { opacity: 0.85; }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-danger {
  padding: 8px 16px; border-radius: 8px; border: none;
  background: var(--danger); color: #fff; font-weight: 500;
  font-size: 13px; cursor: pointer;
}
.btn-danger:hover { opacity: 0.85; }
.btn-danger:disabled { opacity: 0.4; cursor: not-allowed; }

@media (max-width: 768px) {
  .action-bar { flex-direction: column; align-items: stretch; }
  .filter-group { justify-content: stretch; }
  .filter-select { flex: 1; }
  .record-main { padding: 10px; }
}
</style>
