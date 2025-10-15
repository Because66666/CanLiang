"use client"

import { useState, useEffect, useRef } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Search, Clock, Globe, AlertCircle, CheckCircle, XCircle, Info, Play, Square, Monitor, RefreshCw } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ErrorCard } from "@/components/ErrorPage"
import { colors } from "@/lib/utils-inventory"
import { notify } from "@/lib/notification"

// 导入类型定义
import { WebhookDataItem, WebhookDataResponse, ProgramListResponse, VideoStreamConfig } from "@/types/inventory"

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
 * 视频推流状态接口
 */
interface VideoStreamState {
  programs: string[]
  selectedProgram: string
  isStreaming: boolean
  streamUrl: string
  loading: boolean
  error: string | null
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
  // 错误显示状态跟踪
  const errorShownRef = useRef({
    webhookData: false,
    programList: false,
    systemInfo: false,
    videoStream: false
  })

  const [state, setState] = useState<WebInfoPageState>({
    data: [],
    loading: true,
    error: null,
    searchTerm: '',
    selectedEvent: 'all',
    limit: 100
  })

  // 视频推流状态
  const [streamState, setStreamState] = useState<VideoStreamState>({
    programs: ['桌面'],
    selectedProgram: '',
    isStreaming: false,
    streamUrl: '',
    loading: false,
    error: null
  })

  // 系统信息状态
  const [systemInfo, setSystemInfo] = useState<{
    memory_usage: number
    cpu_usage: number
    loading: boolean
    error: string | null
  }>({
    memory_usage: 0,
    cpu_usage: 0,
    loading: true,
    error: null
  })

  /**
   * 获取程序列表
   */
  const fetchProgramList = async () => {
    try {
      setStreamState(prev => ({ ...prev, loading: true, error: null }))
      const response = await apiService.fetchProgramList()
      
      if (response.success && response.data && response.data.length > 0) {
        const firstProgram = response.data[0]
        setStreamState(prev => ({ 
          ...prev, 
          programs: response.data, 
          selectedProgram: firstProgram,
          loading: false 
        }))
        
        // 自动开始第一项的推流
        await startVideoStreamAuto(firstProgram)
      } else {
        setStreamState(prev => ({ 
          ...prev, 
          programs: response.data || [],
          error: response.message || '获取程序列表失败', 
          loading: false 
        }))
        
        // 显示错误通知（只显示一次）
        if (!errorShownRef.current.programList) {
          notify.error('网络错误，请刷新后重试')
          errorShownRef.current.programList = true
        }
      }
    } catch (error) {
      setStreamState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : '网络错误', 
        loading: false 
      }))
      
      // 显示错误通知（只显示一次）
      if (!errorShownRef.current.programList) {
        notify.error('网络错误，请刷新后重试')
        errorShownRef.current.programList = true
      }
    }
  }

  /**
   * 自动开始视频推流（内部使用）
   * @param programName 程序名称
   */
  const startVideoStreamAuto = async (programName: string) => {
    try {
      setStreamState(prev => ({ ...prev, error: null }))
      
      const config: VideoStreamConfig = {
        app: programName
      }
      
      const responseUrl: string = await apiService.getVideoStreamUrl(config)
      
      if (responseUrl) {
        setStreamState(prev => ({ 
          ...prev, 
          isStreaming: true,
          streamUrl: responseUrl
        }))
      } else {
        setStreamState(prev => ({ 
          ...prev, 
          error: '启动推流失败'
        }))
        
        // 显示错误通知（只显示一次）
        if (!errorShownRef.current.videoStream) {
          notify.error('网络错误，请刷新后重试')
          errorShownRef.current.videoStream = true
        }
      }
    } catch (error) {
      setStreamState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : '网络错误'
      }))
      
      // 显示错误通知（只显示一次）
      if (!errorShownRef.current.videoStream) {
        notify.error('网络错误，请刷新后重试')
        errorShownRef.current.videoStream = true
      }
    }
  }


  /**
   * 停止视频推流
   */
  const stopVideoStream = () => {
    setStreamState(prev => ({ 
      ...prev, 
      isStreaming: false,
      streamUrl: '',
      error: null
    }))
    
    // 关闭视频流
    apiService.closeVideoStream()
  }



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
        
        // 显示错误通知（只显示一次）
        if (!errorShownRef.current.webhookData) {
          notify.error('网络错误，请刷新后重试')
          errorShownRef.current.webhookData = true
        }
      }
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : '网络错误', 
        loading: false 
      }))
      
      // 显示错误通知（只显示一次）
      if (!errorShownRef.current.webhookData) {
        notify.error('网络错误，请刷新后重试')
        errorShownRef.current.webhookData = true
      }
    }
  }

  /**
   * 获取系统信息
   */
  const fetchSystemInfo = async () => {
    try {
      setSystemInfo(prev => ({ ...prev, error: null }))
      const response = await apiService.fetchSystemInfo()
      
      if (response.success && response.data) {
        setSystemInfo(prev => ({ 
          ...prev, 
          memory_usage: response.data.memory_usage,
          cpu_usage: response.data.cpu_usage,
          loading: false 
        }))
      } else {
        setSystemInfo(prev => ({ 
          ...prev, 
          error: response.message || '获取系统信息失败', 
          loading: false 
        }))
        
        // 显示错误通知（只显示一次）
        if (!errorShownRef.current.systemInfo) {
          notify.error('网络错误，请刷新后重试')
          errorShownRef.current.systemInfo = true
        }
      }
    } catch (error) {
      setSystemInfo(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : '网络错误', 
        loading: false 
      }))
      
      // 显示错误通知（只显示一次）
      if (!errorShownRef.current.systemInfo) {
        notify.error('网络错误，请刷新后重试')
        errorShownRef.current.systemInfo = true
      }
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
        
        // 显示错误通知（只显示一次）
        if (!errorShownRef.current.webhookData) {
          notify.error('网络错误，请刷新后重试')
          errorShownRef.current.webhookData = true
        }
      }
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        error: error instanceof Error ? error.message : '网络错误', 
      }))
      
      // 显示错误通知（只显示一次）
      if (!errorShownRef.current.webhookData) {
        notify.error('网络错误，请刷新后重试')
        errorShownRef.current.webhookData = true
      }
    }
  }

  // 组件挂载时获取数据
  useEffect(() => {
    fetchWebhookData()
    fetchProgramList() // 获取程序列表
    fetchSystemInfo() // 获取系统信息
  }, [state.limit])

  // 每秒自动刷新数据
  useEffect(() => {
    const interval = setInterval(() => {
      fetchWebhookDataNoLoading()
      fetchSystemInfo() // 定时刷新系统信息
    }, 3000) // 每3秒刷新一次

    return () => clearInterval(interval) // 清理定时器
  }, [state.limit])

  /**
   * 组件卸载时清理资源
   * 当用户切换界面时主动断开视频流连接
   */
  useEffect(() => {
    return () => {
      // 组件卸载时停止视频流
      // 使用ref来获取最新的状态，避免闭包问题
      console.log('组件卸载，主动断开视频流连接')
      stopVideoStream()
    }
  }, [])

  /**
   * 页面可见性检测
   * 当用户切换标签页时暂停/恢复视频流
   */
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        // 页面隐藏时暂停视频流
        if (streamState.isStreaming) {
          console.log('页面隐藏，暂停视频流')
          stopVideoStream()
        }
      } else {
        // 页面显示时恢复视频流（如果之前有选中的程序）
        if (!streamState.isStreaming && streamState.selectedProgram) {
          console.log('页面显示，恢复视频流')
          startVideoStreamAuto(streamState.selectedProgram)
        }
      }
    }

    // 添加页面可见性变化监听器
    document.addEventListener('visibilitychange', handleVisibilityChange)

    // 清理监听器
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [streamState.isStreaming, streamState.selectedProgram])

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
        <div className="mb-8 text-3xl font-bold text-center flex items-center justify-center">
          <div 
            className="flex items-center gap-3"
            style={{ color: colors.secondary }}
          >  
            BetterGI面板
          </div>
        </div>
        
        {/* 主布局：左侧3/4 + 右侧1/4 */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">

        {/* 左侧：视频推流和程序选择区域 (3/4) */}
          <div className="lg:col-span-3">
            <div className="grid grid-rows-2 gap-6 h-full">
              {/* 上半部分：视频推流区域 */}
              <Card className="h-full">
                <CardContent className="p-6 h-full">
                  <div className="mb-4">
                    <h2 className="text-xl font-semibold flex items-center gap-2">
                      <Monitor className="w-5 h-5" />
                      实时屏看
                    </h2>
                  </div>

                  {/* 推流状态 */}
                  <div className="mb-4">
                    <div className="flex items-center gap-2 text-sm">
                      <span className="font-medium">状态:</span>
                      <Badge 
                        variant={streamState.isStreaming ? "default" : "secondary"}
                        style={{
                          backgroundColor: streamState.isStreaming ? '#1e40af' : '#93c5fd',
                          color: streamState.isStreaming ? 'white' : '#1e40af'
                        }}
                      >
                        {streamState.isStreaming ? "观看中" : "无信号"}
                      </Badge>
                    {/* 系统信息 */}
                    <div className="flex items-center gap-4 text-sm">
                      {systemInfo.loading ? (
                        <div className="text-gray-500">加载中...</div>
                      ) : systemInfo.error ? (
                        <div className="text-red-500">系统信息获取失败</div>
                      ) : (
                        <>
                          <div className="flex items-center gap-2">
                            <span className="text-gray-600">内存:</span>
                            <Badge 
                              variant="outline" 
                              className={`${systemInfo.memory_usage > 80 ? 'bg-red-100 text-red-800 border-red-200' : 
                                systemInfo.memory_usage > 60 ? 'bg-yellow-100 text-yellow-800 border-yellow-200' : 
                                'bg-green-100 text-green-800 border-green-200'}`}
                            >
                              {systemInfo.memory_usage.toFixed(1)}%
                            </Badge>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className="text-gray-600">CPU:</span>
                            <Badge 
                              variant="outline" 
                              className={`${systemInfo.cpu_usage > 80 ? 'bg-red-100 text-red-800 border-red-200' : 
                                systemInfo.cpu_usage > 60 ? 'bg-yellow-100 text-yellow-800 border-yellow-200' : 
                                'bg-green-100 text-green-800 border-green-200'}`}
                            >
                              {systemInfo.cpu_usage.toFixed(1)}%
                            </Badge>
                          </div>
                        </>
                      )}
                    </div>
                      {/* {streamState.selectedProgram && (
                        <>
                          <span className="font-medium ml-4">目标程序:</span>
                          <span className="text-muted-foreground">{streamState.selectedProgram}</span>
                        </>
                      )} */}
                      
                      {/* 程序选择下拉框 */}
                      <div className="ml-auto flex items-center gap-2">
                        <Select
                          value={streamState.selectedProgram}
                          onValueChange={(value) => {
                            setStreamState(prev => ({ 
                              ...prev, 
                              selectedProgram: value, 
                              error: null 
                            }))
                            // 选择程序后自动开始推流（无论当前是否在推流）
                            if (value) {
                              startVideoStreamAuto(value)
                            }
                          }}
                        >
                          <SelectTrigger className="w-[200px]">
                            <SelectValue placeholder="选择程序" />
                          </SelectTrigger>
                          <SelectContent>
                            {streamState.programs.length === 0 ? (
                              <SelectItem value="" disabled>
                                暂无可用程序
                              </SelectItem>
                            ) : (
                              streamState.programs.map((program, index) => (
                                <SelectItem key={index} value={program}>
                                  <div className="flex items-center gap-2">
                                    <Monitor className="w-4 h-4" />
                                    {program}
                                  </div>
                                </SelectItem>
                              ))
                            )}
                          </SelectContent>
                        </Select>
                        
                        {/* 刷新按钮 */}
                        <Button
                          onClick={fetchProgramList}
                          disabled={streamState.loading}
                          variant="outline"
                          size="sm"
                        >
                          {streamState.loading ? '加载中...' : '刷新'}
                        </Button>
                      </div>
                      
                      {streamState.loading && (
                        <>
                          <span className="font-medium ml-4">正在:</span>
                          <span className="text-muted-foreground">自动连接中...</span>
                        </>
                      )}
                    </div>
                  </div>

                  {/* 推流错误提示 */}
                  {streamState.error && (
                    <ErrorCard
                      type="error"
                      message={streamState.error}
                      className="mb-4"
                    />
                  )}

                  {/* 视频显示区域 */}
                  <div className="flex-1 bg-black rounded-lg flex items-center justify-center min-h-[300px]">
                    {streamState.isStreaming && streamState.streamUrl ? (
                      <img
                        src={streamState.streamUrl}
                        alt="实时视频流"
                        className="w-full h-full rounded-lg object-contain"
                        onError={(e) => {
                          console.error('视频流加载失败:', e)
                          setStreamState(prev => ({ 
                            ...prev, 
                            error: '视频流连接失败，请检查网络连接' 
                          }))
                          
                          // 显示错误通知（只显示一次）
                          if (!errorShownRef.current.videoStream) {
                            notify.error('网络错误，请刷新后重试')
                            errorShownRef.current.videoStream = true
                          }
                        }}
                        onLoad={() => {
                          console.log('视频流连接成功')
                        }}
                      />
                    ) : (
                      <div className="text-center text-muted-foreground">
                        <Monitor className="w-16 h-16 mx-auto mb-4 opacity-50" />
                        {streamState.loading ? (
                          <p>正在自动连接推流...</p>
                        ) : streamState.programs.length === 0 ? (
                          <p>暂无可用程序，请确保有程序正在运行</p>
                        ) : (
                          <p>等待自动推流连接</p>
                        )}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>


            </div>
          </div>

          {/* 右侧：原有内容区域 (1/4) */}
          <div className="lg:col-span-1">
            {/* 控制面板 */}
            <Card className="mb-4">
              <CardContent className="p-4">
                <div className="flex flex-col gap-3">
                  {/* 当前状态 */}
                  <div className="flex flex-col items-center gap-2 w-full">
                    <div className="flex items-center gap-2">
                      <Play className="h-4 w-4" style={{ color: colors.primary }} />
                      <span className="text-sm" style={{ color: colors.secondary }}>
                        当前状态:
                      </span>
                    </div>
                    <div className="w-full text-center">
                      <span className="text-sm font-medium px-3 py-2 rounded-md" style={{ 
                        color: colors.primary,
                        backgroundColor: `${colors.primary}15`
                      }}>
                        {filteredData.length > 0 ? filteredData[0].message : '正在运行'}
                      </span>
                    </div>
                  </div>

                  {/* 事件类型筛选 */}
                  <div className="flex flex-col items-center gap-2 w-full">
                    <div className="flex items-center gap-2">
                      <Info className="h-4 w-4" style={{ color: colors.primary }} />
                      <span className="text-sm" style={{ color: colors.secondary }}>
                        事件类型:
                      </span>
                    </div>
                    <Select 
                      value={state.selectedEvent} 
                      onValueChange={(value) => setState(prev => ({ ...prev, selectedEvent: value }))}
                    >
                      <SelectTrigger
                        className="w-full border-0 shadow-sm focus:ring-2"
                        style={{
                          borderColor: colors.lightBorder,
                          boxShadow: `0 0 0 1px ${colors.lightBorder}`,
                        }}
                      >
                        <SelectValue placeholder="事件类型" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">所有事件</SelectItem>
                        {uniqueEvents.map(event => (
                          <SelectItem key={event} value={event.toLowerCase()}>
                            <div className="flex items-center gap-2">
                              {getEventIcon(event)}
                              <span className="text-xs">{event}</span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* 刷新按钮 */}
                  {/* <div className="flex flex-col items-center gap-2 w-full">
                    <button
                      onClick={fetchWebhookData}
                      disabled={state.loading}
                      className="px-4 py-3 rounded-md text-sm font-medium shadow-sm w-full"
                      style={{
                        backgroundColor: state.loading ? colors.mediumGray : colors.primary,
                        color: "#fff",
                        boxShadow: `0 0 0 1px ${colors.lightBorder}`,
                        opacity: state.loading ? 0.6 : 1,
                        cursor: state.loading ? 'not-allowed' : 'pointer'
                      }}
                    >
                      {state.loading ? '加载中...' : '刷新'}
                    </button>
                  </div> */}

                </div>
              </CardContent>
            </Card>
            
            {/* 统计信息 */}
            <div className="flex flex-col gap-1 mt-3 text-xs text-muted-foreground">
              {/* <span>总计: {state.data.length}</span>
              <span>筛选: {filteredData.length}</span>
              {state.data.length > 0 && (
                <span className="truncate">最新: {formatTimestamp(state.data[0]?.create_time)}</span>
              )} */}
              {/* 加载状态 */}
              {state.loading && (
                <div className="inline-flex items-center gap-2 text-muted-foreground">
                  <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-primary"></div>
                  <span className="text-xs">加载中...</span>
                </div>
              )}
            </div>

            {/* 错误提示 */}
            {/* {state.error && (
              <ErrorCard
                type="error"
                message={state.error}
                showRefresh={true}
                onRefresh={fetchWebhookData}
                className="mt-4"
              />
            )} */}

            {/* 数据列表 */}
            {!state.loading && filteredData.length === 0 && !state.error && (
              <ErrorCard
                type="noData"
                message="暂无数据"
                className="mt-4"
              />
            )}

            {/* Webhook数据卡片列表 */}
            <div className="space-y-4 mt-3 max-h-[600px] overflow-y-auto">
              {filteredData.map((item, index) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Card className="hover:shadow-md transition-shadow">
                    <CardContent className="p-4">
                      {/* 卡片头部 */}
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          {getEventIcon(item.event)}
                          <div>
                            <h3 className="text-sm font-semibold">
                              {item.event}
                            </h3>
                            <div className="text-xs text-muted-foreground mt-1">
                              {formatTimestamp(item.timestamp)}
                            </div>
                          </div>
                        </div>
                        <Badge className={getEventColor(item.event)} variant="outline">
                          {item.id}
                        </Badge>
                      </div>

                      {/* 消息内容 */}
                      {item.message && (
                        <div className="mb-3">
                          <div className="p-2 bg-muted rounded-md">
                            <pre className="text-xs whitespace-pre-wrap font-mono">
                              {item.message}
                            </pre>
                          </div>
                        </div>
                      )}

                      {/* 截图 */}
                      {item.screenshot && (
                        <div className="mt-3">
                          <img
                            src={`/image/${item.id}`}
                            alt="事件截图"
                            className="rounded-md object-cover w-full border"
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


        </div>
      </div>
    </main>
  )
}