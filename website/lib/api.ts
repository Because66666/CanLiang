// API服务层 - 处理所有的API请求

import { promises } from 'dns'
import { InventoryData, DateItem, ItemTrendData, ItemDataDict, DurationDict, WebhookDataResponse, ProgramListResponse, VideoStreamConfig, VideoStreamErrorResponse } from '../types/inventory'

// API基础配置
const BASE_URL = process.env.NODE_ENV === 'production' ? '/' : 'http://localhost:3001/'

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

  /**
   * 获取webhook数据列表
   * @param limit 返回记录数限制，默认100
   * @returns Promise<WebhookDataResponse> webhook数据响应
   */
  async fetchWebhookData(limit: number = 100): Promise<WebhookDataResponse> {
    try {
      const response = await fetch(`${this.baseUrl}api/webhook-data?limit=${limit}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const responseData = await response.json()
      
      // 确保返回的数据结构符合预期
      return {
        success: responseData.success || true,
        data: responseData.data || [],
        count: responseData.count || 0,
        message: responseData.message
      }
    } catch (error) {
      console.error('Error fetching webhook data:', error)
      throw new Error('获取webhook数据失败，请稍后再试')
    }
  }

  /**
   * 获取可推流的程序列表
   * @returns Promise<ProgramListResponse> 程序列表响应
   */
  async fetchProgramList(): Promise<ProgramListResponse> {
    try {
      const response = await fetch(`${this.baseUrl}api/programlist`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const responseData = await response.json()
      
      // 确保返回的数据结构符合预期
      return {
        success: responseData.success || true,
        data: responseData.data || [],
        count: responseData.count || 0,
        message: responseData.message
      }
    } catch (error) {
      console.error('Error fetching program list:', error)
      throw new Error('获取程序列表失败，请稍后再试')
    }
  }

  /**
   * 获取视频流URL
   * @param config 视频流配置，包含目标应用程序名称
   * @returns string 视频流URL
   */
  getVideoStreamUrl(config: VideoStreamConfig): string {
    if (!config.app) {
      throw new Error('应用程序名称不能为空')
    }
    
    if (!config.app.endsWith('.exe')) {
      throw new Error('应用程序名称必须以.exe结尾')
    }
    
    return `${this.baseUrl}api/stream?app=${encodeURIComponent(config.app)}`
  }

  /**
   * 验证视频流参数并获取流URL
   * @param config 视频流配置
   * @returns Promise<string> 视频流URL或错误信息
   */
  async validateAndGetStreamUrl(config: VideoStreamConfig): Promise<string> {
    try {
      // 参数验证
      if (!config.app) {
        throw new Error('请指定目标应用程序名称')
      }
      
      if (!config.app.endsWith('.exe')) {
        throw new Error('应用程序名称必须以.exe结尾')
      }
      
      // 返回视频流URL
      return this.getVideoStreamUrl(config)
      
    } catch (error) {
      console.error('Error validating stream config:', error)
      throw error
    }
  }
}

// 导出API服务实例
export const apiService = new ApiService()

// 导出默认实例
export default apiService