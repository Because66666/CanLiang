// API服务层 - 处理所有的API请求（使用模拟数据）

import { promises } from 'dns'
import { InventoryData, DateItem, ItemTrendData,
   ItemDataDict, DurationDict, WebhookDataResponse,
    ProgramListResponse, VideoStreamConfig,
     VideoStreamErrorResponse } from '../types/inventory'

// 导入JSON数据
import LogListData from '../json/LogList.json'
import LogData from '../json/LogData.json'
import WebhookData from '../json/webhook-data.json'
import ProgramListData from '../json/programlist.json'
import SystemDetailData from '../json/systemdetail.json'

// API基础配置
const BASE_URL = process.env.NODE_ENV === 'production' ? '/' : 'http://localhost:3001/'

// API请求封装函数
class ApiService {
  private baseUrl: string

  constructor(baseUrl: string = BASE_URL) {
    this.baseUrl = baseUrl
  }

  /**
   * 获取日期列表（使用模拟数据）
   * @returns Promise<DateItem[]> 日期列表
   */
  async fetchDateList(): Promise<DateItem[]> {
    try {
      // 模拟网络延迟
      await new Promise(resolve => setTimeout(resolve, 100))
      
      const dates = LogListData.list || []
      
      return Array.isArray(dates) ? dates.map(date => ({
        value: date,
        label: date
      })) : []
    } catch (error) {
      console.error('Error fetching date list:', error)
      throw new Error('获取日期列表失败，请稍后再试')
    }
  }

  /**
   * 获取物品和日期的全部数据（使用模拟数据）
   * @returns Promise<{itemData:ItemDataDict,durationData:DurationDict}> 物品和持续时间数据
   */
  async fetchAllData():Promise<{itemData:ItemDataDict,durationData:DurationDict}>{
    try {
      // 模拟网络延迟
      await new Promise(resolve => setTimeout(resolve, 200))
      
      // 转换data.item的字段名映射
      const itemData: ItemDataDict = {
        ItemName: LogData.item.物品名称 || [],
        Task: LogData.item.归属配置组 || [],
        TimeStamp: LogData.item.时间 || [],
        Date: LogData.item.日期 || []
      }
      // 转换data.duration的字段名映射
      const durationData: DurationDict = {
        Date: LogData.duration.日期 || [],
        Duration: LogData.duration.持续时间 || []
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
   * 获取webhook数据列表（使用模拟数据）
   * @param limit 返回记录数限制，默认100
   * @returns Promise<WebhookDataResponse> webhook数据响应
   */
  async fetchWebhookData(limit: number = 100): Promise<WebhookDataResponse> {
    try {
      // 模拟网络延迟
      await new Promise(resolve => setTimeout(resolve, 150))
      
      // 根据limit参数截取数据
      const limitedData = WebhookData.data.slice(0, limit)
      
      // 确保返回的数据结构符合预期
      return {
        success: true,
        data: limitedData,
        count: limitedData.length,
        message: `成功获取到 ${limitedData.length} 条webhook数据`
      }
    } catch (error) {
      console.error('Error fetching webhook data:', error)
      throw new Error('获取webhook数据失败，请稍后再试')
    }
  }

  /**
   * 获取可推流的程序列表（使用模拟数据）
   * @returns Promise<ProgramListResponse> 程序列表响应
   */
  async fetchProgramList(): Promise<ProgramListResponse> {
    try {
      // 模拟网络延迟
      await new Promise(resolve => setTimeout(resolve, 100))
      
      // 确保返回的数据结构符合预期
      return {
        success: ProgramListData.success || true,
        data: ProgramListData.data || [],
        count: ProgramListData.count || 0,
        message: ProgramListData.message || '获取程序列表成功'
      }
    } catch (error) {
      console.error('Error fetching program list:', error)
      throw new Error('获取程序列表失败，请稍后再试')
    }
  }

  /**
   * 获取视频流URL（返回固定图片）
   * @param config 视频流配置，包含目标应用程序名称
   * @returns string 图片文件路径
   */
  getVideoStreamUrl(config: VideoStreamConfig): string {
    if (!config.app) {
      throw new Error('应用程序名称不能为空')
    }
    
    if (!config.app.endsWith('.exe')) {
      throw new Error('应用程序名称必须以.exe结尾')
    }
    
    // 返回固定的图片文件路径
    return '/demo_pic.jpg'
  }

  /**
   * 验证视频流参数并获取流URL（返回固定图片）
   * @param config 视频流配置
   * @returns Promise<string> 图片文件路径
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
      
      // 模拟网络延迟
      await new Promise(resolve => setTimeout(resolve, 50))
      
      // 返回固定图片路径
      return this.getVideoStreamUrl(config)
      
    } catch (error) {
      console.error('Error validating stream config:', error)
      throw error
    }
  }

  /**
   * 关闭视频流（模拟操作）
   * @returns Promise<{success: boolean, message: string}> 操作结果
   */
  async closeVideoStream(): Promise<{success: boolean, message: string}> {
    try {
      // 模拟网络延迟
      await new Promise(resolve => setTimeout(resolve, 100))
      
      // 模拟成功响应
      return {
        success: true,
        message: '关闭视频流成功'
      }
      
    } catch (error) {
      console.error('Error closing video stream:', error)
      throw error
    }
  }

  /**
   * 获取系统详细信息（使用模拟数据）
   * @returns Promise<{success: boolean, data: {memory_usage: number, cpu_usage: number}, message: string}> 系统信息响应
   */
  async fetchSystemInfo(): Promise<{success: boolean, data: {memory_usage: number, cpu_usage: number}, message: string}> {
    try {
      // 模拟网络延迟
      await new Promise(resolve => setTimeout(resolve, 100))
      
      // 确保返回的数据结构符合预期
      return {
        success: SystemDetailData.success || true,
        data: SystemDetailData.data || { memory_usage: 0.0, cpu_usage: 0.0 },
        message: SystemDetailData.message || '获取系统信息成功'
      }
    } catch (error) {
      console.error('Error fetching system info:', error)
      throw new Error('获取系统信息失败，请稍后再试')
    }
  }
}

// 导出API服务实例
export const apiService = new ApiService()

// 导出默认实例
export default apiService