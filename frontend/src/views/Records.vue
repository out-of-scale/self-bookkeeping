<template>
  <div class="page-container">
    <div class="page-header">
      <h2 style="display:flex;align-items:center;"><Icon name="list" size="24" /> 账单明细</h2>
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
      <div class="search-input-wrapper">
        <input
          v-model="searchText"
          placeholder="搜索商家名称..."
          class="search-input"
          @input="debouncedSearch"
        />
      </div>
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
            <button class="action-btn edit" @click="openEdit(item)">编辑</button>
            <button class="action-btn delete" @click="confirmDelete(item)">删除</button>
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
import Icon from '../components/Icon.vue'

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
  '餐饮': 'rgba(194,163,131,0.2)', '交通': 'rgba(142,177,199,0.2)', '购物': 'rgba(217,136,128,0.2)',
  '娱乐': 'rgba(214,187,159,0.2)', '医疗': 'rgba(130,168,141,0.2)', '教育': 'rgba(234,182,118,0.2)',
  '住房': 'rgba(118,155,139,0.2)', '通讯': 'rgba(224,157,141,0.2)', '其他': 'rgba(169,160,152,0.2)',
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
  margin-bottom: 16px; flex-wrap: wrap; gap: 12px;
}
.add-btn {
  padding: 10px 18px; border-radius: 12px; border: none;
  background: var(--gradient-primary); color: #fff; font-weight: 600;
  font-size: 14px; cursor: pointer; transition: transform 0.2s var(--spring), box-shadow 0.2s;
  box-shadow: var(--shadow-sm);
}
.add-btn:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.add-btn:active { transform: scale(0.95); }

.filter-group { display: flex; gap: 8px; }
.filter-select {
  padding: 8px 12px; border-radius: 10px;
  border: 1px solid var(--border-color); background: var(--bg-card);
  color: var(--text-primary); font-size: 13px; cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.filter-select:focus { border-color: var(--primary-light); outline: none; box-shadow: 0 0 0 2px rgba(194, 163, 131, 0.3); }

/* 搜索栏 */
.search-bar { margin-bottom: 16px; }
.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}
.search-icon {
  position: absolute;
  left: 14px;
  color: var(--text-muted);
  font-size: 14px;
  pointer-events: none;
}
.search-input {
  width: 100%; padding: 12px 14px 12px 14px; border-radius: 12px;
  border: 1px solid var(--border-color); background: var(--bg-card);
  color: var(--text-primary); font-size: 14px; transition: border-color 0.2s, box-shadow 0.2s;
}
.search-input:focus { border-color: var(--primary-light); outline: none; box-shadow: 0 0 0 2px rgba(194, 163, 131, 0.3); }
.search-input::placeholder { color: var(--text-muted); }

/* 记录卡片 */
.record-card {
  background: var(--bg-card); border-radius: 16px; border: 1px solid var(--border-color);
  margin-bottom: 12px; overflow: hidden;
  transition: transform 0.2s var(--spring), box-shadow 0.2s var(--ease), border-color 0.2s;
}
.record-card:hover {
  transform: translateY(-2px); box-shadow: var(--shadow-md); border-color: var(--border-light);
  background: var(--bg-card-hover);
}
.record-main {
  display: flex; align-items: center; padding: 16px; gap: 14px; cursor: pointer;
}
.record-icon {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; flex-shrink: 0; box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
}
.record-info { flex: 1; min-width: 0; }
.record-merchant { font-weight: 600; font-size: 15px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.record-meta { font-size: 12px; color: var(--text-muted); margin-top: 4px; display: flex; align-items: center; gap: 8px; }
.record-type-badge {
  padding: 2px 6px; border-radius: 6px; font-size: 10px; font-weight: 600;
}
.record-type-badge.expense { background: var(--danger-bg); color: var(--danger); }
.record-type-badge.income { background: var(--success-bg); color: var(--success); }
.record-amount { font-weight: 700; font-size: 16px; white-space: nowrap; font-variant-numeric: tabular-nums; letter-spacing: -0.5px; }
.record-amount.expense { color: var(--danger); }
.record-amount.income { color: var(--success); }
.record-actions {
  display: flex; justify-content: flex-end; padding: 0 16px 12px; gap: 8px;
}
.action-btn {
  padding: 6px 14px; border-radius: 8px; border: 1px solid var(--border-color);
  font-size: 13px; font-weight: 500; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; background: var(--bg-card); color: var(--text-secondary);
}
.action-btn:hover { border-color: var(--primary-light); background: var(--bg-card-hover); color: var(--text-primary); }
.action-btn.edit:hover { background: rgba(194, 163, 131, 0.1); border-color: var(--primary-light); color: var(--primary-dark); }
.action-btn.delete:hover { background: rgba(217, 136, 128, 0.1); border-color: var(--danger); color: var(--danger); }

/* 分页 */
.pagination {
  display: flex; justify-content: center; align-items: center; gap: 16px;
  padding: 24px 0;
}
.page-btn {
  padding: 8px 16px; border-radius: 10px;
  border: 1px solid var(--border-color); background: var(--bg-card);
  color: var(--text-secondary); font-size: 13px; font-weight: 500; cursor: pointer;
  transition: all 0.2s;
}
.page-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.page-btn:not(:disabled):hover { color: var(--primary-light); border-color: var(--primary-light); background: var(--bg-card-hover); }
.page-info { font-size: 13px; color: var(--text-muted); font-weight: 600; font-variant-numeric: tabular-nums; }

/* 弹窗 */
.dialog-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  display: flex; align-items: center; justify-content: center;
  z-index: 2000; padding: 20px;
  animation: fadeIn 0.2s ease-out;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.dialog-box {
  background: var(--bg-surface); border-radius: 20px;
  width: 100%; max-width: 420px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-lg);
  transform: translateY(0) scale(1);
  animation: slideUp 0.3s var(--spring);
}
@keyframes slideUp { from { transform: translateY(20px) scale(0.95); opacity: 0; } to { transform: translateY(0) scale(1); opacity: 1; } }

.dialog-box.small { max-width: 360px; }
.dialog-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 24px 12px;
}
.dialog-header h3 { font-size: 18px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; }
.close-btn {
  width: 32px; height: 32px; border-radius: 10px; border: none;
  background: rgba(0,0,0,0.05); color: var(--text-muted);
  font-size: 16px; cursor: pointer; transition: all 0.2s;
  display: flex; align-items: center; justify-content: center;
}
.close-btn:hover { background: rgba(0,0,0,0.08); color: var(--text-primary); transform: rotate(90deg); }
.dialog-body { padding: 8px 24px 20px; }
.dialog-body p { color: var(--text-secondary); font-size: 14px; line-height: 1.6; }
.dialog-footer {
  display: flex; justify-content: flex-end; gap: 12px;
  padding: 12px 24px 24px;
}

/* 表单 */
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 13px; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px; }
.form-input {
  width: 100%; padding: 12px 14px; border-radius: 10px;
  border: 1px solid var(--border-color); background: var(--bg-primary);
  color: var(--text-primary); font-size: 14px; transition: border-color 0.2s, box-shadow 0.2s;
}
.form-input:focus { border-color: var(--primary-light); outline: none; box-shadow: 0 0 0 2px rgba(194, 163, 131, 0.3); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

/* 按钮 */
.btn-cancel {
  padding: 10px 20px; border-radius: 10px;
  border: 1px solid var(--border-color); background: transparent;
  color: var(--text-muted); font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s;
}
.btn-cancel:hover { color: var(--text-primary); background: rgba(0,0,0,0.03); }
.btn-cancel:active { transform: scale(0.96); }

.btn-primary {
  padding: 10px 20px; border-radius: 10px; border: none;
  background: var(--gradient-primary); color: #fff; font-weight: 600;
  font-size: 14px; cursor: pointer; transition: all 0.2s var(--spring); box-shadow: var(--shadow-sm);
}
.btn-primary:hover:not(:disabled) { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.btn-primary:active:not(:disabled) { transform: scale(0.96); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; box-shadow: none; }

.btn-danger {
  padding: 10px 20px; border-radius: 10px; border: none;
  background: var(--gradient-expense); color: #fff; font-weight: 600;
  font-size: 14px; cursor: pointer; transition: all 0.2s var(--spring); box-shadow: var(--shadow-sm);
}
.btn-danger:hover:not(:disabled) { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.btn-danger:active:not(:disabled) { transform: scale(0.96); }
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; box-shadow: none; }

@media (max-width: 768px) {
  .action-bar { flex-direction: column; align-items: stretch; }
  .filter-group { justify-content: stretch; }
  .filter-select { flex: 1; }
  .record-main { padding: 10px; }
}
</style>
