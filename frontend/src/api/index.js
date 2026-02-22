/**
 * API 请求封装
 */
import axios from 'axios'

const api = axios.create({
    baseURL: '/api',
    timeout: 60000,
})

/** 获取月度统计 */
export function getMonthStats(year, month) {
    return api.get('/get_stats', { params: { year, month } })
}

/** 获取年度汇总 */
export function getYearlyStats(year) {
    return api.get('/get_yearly', { params: { year } })
}

/** 获取账单明细 */
export function getReceipts(params) {
    return api.get('/receipts', { params })
}

/** 上传账单截图 */
export function uploadReceipt(imageBase64) {
    return api.post('/upload_receipt', { image_base64: imageBase64 })
}

/** 编辑账单 */
export function updateReceipt(id, data) {
    return api.put(`/receipts/${id}`, data)
}

/** 删除账单 */
export function deleteReceipt(id) {
    return api.delete(`/receipts/${id}`)
}

/** 手动添加账单 */
export function manualAddReceipt(data) {
    return api.post('/receipts/manual', data)
}

/** 获取总净资产 */
export function getNetWorth() {
    return api.get('/net_worth')
}

/** 手动更新/校准总净资产 */
export function updateNetWorth(currentNetWorth) {
    return api.put('/net_worth', { current_net_worth: currentNetWorth })
}

export default api
