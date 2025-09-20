// API服务层 - 处理所有的API请求

import { promises } from 'dns'
import { InventoryData, DateItem, ItemTrendData, ItemDataDict, DurationDict } from '../types/inventory'

// API基础配置
// const BASE_URL = 'http://localhost:3001/'
const BASE_URL = '/'

// API请求封装函数
class ApiService {
  private baseUrl: string

  constructor(baseUrl: string = BASE_URL) {
    this.baseUrl = baseUrl
  }

  // 获取日期列表
  async fetchDateList(): Promise<DateItem[]> {
    try {
      const response = await fetch(this.baseUrl + 'api/LogList')
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const responseData = await response.json()
      const dates = responseData.list || []
      
      return Array.isArray(dates) ? dates.map(date => ({
        value: date,
        label: date
      })) : []
    } catch (error) {
      console.error('Error fetching date list:', error)
      throw new Error('获取日期列表失败，请稍后再试')
    }
  }

  // 获取物品和日期的全部数据
  async fetchAllData():Promise<{itemData:ItemDataDict,durationData:DurationDict}>{
    try {
      const response = await fetch(this.baseUrl + 'api/LogData')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      
      // 转换data.item的字段名映射
      const itemData: ItemDataDict = {
        ItemName: data.item.物品名称 || [],
        Task: data.item.归属配置组 || [],
        TimeStamp: data.item.时间 || [],
        Date: data.item.日期 || []
      }
      // 转换data.duration的字段名映射
      const durationData: DurationDict = {
        Date: data.duration.日期 || [],
        Duration: data.duration.持续时间 || []
      }
      
      return {
        itemData,
        durationData
      }
    } catch (error) {
      console.error('Error fetching data:', error)
      throw new Error('获取数据失败，请稍后再试')
    }
  }
}

// 导出API服务实例
export const apiService = new ApiService()

// 导出默认实例
export default apiService