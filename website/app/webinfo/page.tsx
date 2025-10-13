"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Search, Clock, Globe, AlertCircle, CheckCircle, XCircle, Info } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ErrorCard } from "@/components/ErrorPage"

// 导入类型定义
import { WebhookDataItem, WebhookDataResponse } from "@/types/inventory"

// 导入API服务
import { apiService } from "@/lib/api"

/**
 * Webhook信息页面状态接口
 */
interface WebInfoPageState {
  data: WebhookDataItem[]
  loading: boolean
  error: string | null
  searchTerm: string
  selectedEvent: string
  limit: number
}

/**
 * 获取事件类型对应的图标
 * @param event 事件类型
 * @returns 对应的图标组件
 */
const getEventIcon = (event: string) => {
  switch (event.toLowerCase()) {
    case 'success':
      return <CheckCircle className="w-4 h-4 text-green-500" />
    case 'error':
      return <XCircle className="w-4 h-4 text-red-500" />
    case 'warning':
      return <AlertCircle className="w-4 h-4 text-yellow-500" />
    default:
      return <Info className="w-4 h-4 text-blue-500" />
  }
}

/**
 * 获取事件类型对应的颜色
 * @param event 事件类型
 * @returns 对应的颜色类名
 */
const getEventColor = (event: string) => {
  switch (event.toLowerCase()) {
    case 'success':
      return 'bg-green-100 text-green-800 border-green-200'
    case 'error':
      return 'bg-red-100 text-red-800 border-red-200'
    case 'warning':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    default:
      return 'bg-blue-100 text-blue-800 border-blue-200'
  }
}

/**
 * 格式化时间戳为指定格式
 * @param timestamp 时间戳字符串
 * @returns 格式化后的时间字符串 (YYYY-MM-DD HH:mm:ss)
 */
const formatTimestamp = (timestamp?: string) => {
  if (!timestamp) return '未知时间'
  try {
    const date = new Date(timestamp)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
    
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  } catch {
    return timestamp
  }
}

/**
 * Webhook信息页面主组件
 */
export default function WebInfoPage() {
  const [state, setState] = useState<WebInfoPageState>({
    data: [],
    loading: true,
    error: null,
    searchTerm: '',
    selectedEvent: 'all',
    limit: 50
  })

  /**
   * 获取Webhook数据
   */
  const fetchWebhookData = async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }))
      const response = await apiService.fetchWebhookData(state.limit)
      
      if (response.success && response.data) {
        setState(prev => ({ 
          ...prev, 
          data: response.data, 
          loading: false 
        }))
      } else {
        setState(prev => ({ 
          ...prev, 
          error: response.message || '获取数据失败', 
          loading: false 
        }))
      }
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : '网络错误', 
        loading: false 
      }))
    }
  }

    /**
   * 获取Webhook数据，没有加载状态
   */
  const fetchWebhookDataNoLoading = async () => {
    try {
      setState(prev => ({ ...prev, error: null }))
      const response = await apiService.fetchWebhookData(state.limit)
      
      if (response.success && response.data) {
        setState(prev => ({ 
          ...prev, 
          data: response.data, 
        }))
      } else {
        setState(prev => ({ 
          ...prev, 
          error: response.message || '获取数据失败', 
        }))
      }
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : '网络错误', 
      }))
    }
  }

  // 组件挂载时获取数据
  useEffect(() => {
    fetchWebhookData()
  }, [state.limit])

  // 每秒自动刷新数据
  useEffect(() => {
    const interval = setInterval(() => {
      fetchWebhookDataNoLoading()
    }, 3000) // 每3秒刷新一次

    return () => clearInterval(interval) // 清理定时器
  }, [state.limit])

  /**
   * 过滤数据
   */
  const filteredData = state.data.filter(item => {
    const matchesSearch = !state.searchTerm || 
      item.event.toLowerCase().includes(state.searchTerm.toLowerCase()) ||
      (item.message && item.message.toLowerCase().includes(state.searchTerm.toLowerCase())) ||
      (item.result && item.result.toLowerCase().includes(state.searchTerm.toLowerCase()))
    
    const matchesEvent = state.selectedEvent === 'all' || 
      item.event.toLowerCase() === state.selectedEvent.toLowerCase()
    
    return matchesSearch && matchesEvent
  })

  /**
   * 获取唯一的事件类型列表
   */
  const uniqueEvents = Array.from(new Set(state.data.map(item => item.event)))

  return (
    <main className="min-h-screen bg-background">
      {/* 主要内容区域 */}
      <div className="container mx-auto py-8 px-4">
        {/* 页面标题 */}
        <div className="mb-8 text-3xl font-bold text-center">
          BetterGI信息流
        </div>
        {/* 控制面板 */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row gap-4 items-center">
              {/* 搜索框 */}
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                <Input
                  placeholder="搜索事件、消息或结果..."
                  value={state.searchTerm}
                  onChange={(e) => setState(prev => ({ ...prev, searchTerm: e.target.value }))}
                  className="pl-10"
                />
              </div>

              {/* 事件类型筛选 */}
              <Select 
                value={state.selectedEvent} 
                onValueChange={(value) => setState(prev => ({ ...prev, selectedEvent: value }))}
              >
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="选择事件类型" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">所有事件</SelectItem>
                  {uniqueEvents.map(event => (
                    <SelectItem key={event} value={event.toLowerCase()}>
                      <div className="flex items-center gap-2">
                        {getEventIcon(event)}
                        {event}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* 数据量限制 */}
              <Select 
                value={state.limit.toString()} 
                onValueChange={(value) => setState(prev => ({ ...prev, limit: parseInt(value) }))}
              >
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="20">20条</SelectItem>
                  <SelectItem value="50">50条</SelectItem>
                  <SelectItem value="100">100条</SelectItem>
                  <SelectItem value="200">200条</SelectItem>
                </SelectContent>
              </Select>

              {/* 刷新按钮 */}
              <Button 
                onClick={fetchWebhookData} 
                disabled={state.loading}
                variant="outline"
              >
                {state.loading ? '加载中...' : '刷新'}
              </Button>
            </div>

            {/* 统计信息 */}
            <div className="flex gap-4 mt-4 text-sm text-muted-foreground">
              <span>总计: {state.data.length} 条</span>
              <span>筛选后: {filteredData.length} 条</span>
              {state.data.length > 0 && (
                <span>最新: {formatTimestamp(state.data[0]?.create_time)}</span>
              )}
              {/* 加载状态 */}
              {state.loading && (
                  <div className="inline-flex items-center gap-2 text-muted-foreground">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                    加载中...
                  </div>

              )}
            </div>


          </CardContent>
        </Card>

        {/* 错误提示 */}
        {state.error && (
          <ErrorCard
            type="error"
            message={state.error}
            showRefresh={true}
            onRefresh={fetchWebhookData}
            className="mb-6"
          />
        )}

        {/* 数据列表 */}
        {!state.loading && filteredData.length === 0 && !state.error && (
          <ErrorCard
            type="noData"
            message="暂无数据"
            className="mb-6"
          />
        )}

        {/* Webhook数据卡片列表 */}
        <div className="space-y-4">
          {filteredData.map((item, index) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  {/* 卡片头部 */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      {getEventIcon(item.event)}
                      <div>
                        <h3 className="text-lg font-semibold">
                          事件: {item.event}
                        </h3>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
                          {/* <Clock className="w-3 h-3" /> */}
                          <span>时间: {formatTimestamp(item.timestamp)}</span>
                        </div>
                      </div>
                    </div>
                    <Badge className={getEventColor(item.event)}>
                      ID: {item.id}
                    </Badge>
                  </div>

                  {/* 时间戳信息 */}
                  {/* {item.timestamp && (
                    <div className="mb-3">
                      <span className="text-sm font-medium text-muted-foreground">
                        执行时间: {formatTimestamp(item.timestamp)}
                      </span>
                    </div>
                  )} */}

                  {/* 结果信息 */}
                  {/* {item.result && (
                    <div className="mb-3">
                      <span className="text-sm font-medium text-muted-foreground">结果: </span>
                      <span className="text-sm">{item.result}</span>
                    </div>
                  )} */}

                  {/* 消息内容 */}
                  {item.message && (
                    <div className="mb-3">
                      <span className="text-sm font-medium text-muted-foreground">消息: </span>
                      <div className="mt-1 p-3 bg-muted rounded-md">
                        <pre className="text-sm whitespace-pre-wrap font-mono">
                          {item.message}
                        </pre>
                      </div>
                    </div>
                  )}

                  {/* 截图 */}
                  {item.screenshot && (
                    <div className="mt-4">
                      <span className="text-sm font-medium text-muted-foreground mb-2 block">
                        截图:
                      </span>
                      <img
                        src={`/image/${item.id}`}
                        alt="事件截图"
                        className="rounded-md object-cover w-full max-w-md border"
                        loading="lazy"
                      />
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </main>
  )
}