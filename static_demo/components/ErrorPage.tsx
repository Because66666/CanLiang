"use client"

import { motion } from "framer-motion"
import { Card, CardContent } from "@/components/ui/card"
import { XCircle, Globe, AlertTriangle, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"

/**
 * 错误页面组件的属性接口
 */
interface ErrorPageProps {
  /** 错误类型 */
  type?: 'error' | 'noData' | 'networkError'
  /** 错误消息 */
  message?: string
  /** 是否显示刷新按钮 */
  showRefresh?: boolean
  /** 刷新按钮点击事件 */
  onRefresh?: () => void
  /** 自定义样式类名 */
  className?: string
  /** 颜色主题配置 */
  colors?: {
    primary: string
    secondary: string
    lightBorder: string
  }
}

/**
 * 获取错误类型对应的图标和配置
 * @param type 错误类型
 * @returns 图标组件和配置信息
 */
const getErrorConfig = (type: ErrorPageProps['type']) => {
  switch (type) {
    case 'error':
      return {
        icon: XCircle,
        title: '加载失败',
        defaultMessage: '数据加载失败，请稍后再试',
        iconColor: 'text-red-500',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200'
      }
    case 'noData':
      return {
        icon: Globe,
        title: '暂无数据',
        defaultMessage: '当前没有可显示的数据',
        iconColor: 'text-gray-400',
        bgColor: 'bg-gray-50',
        borderColor: 'border-gray-200'
      }
    case 'networkError':
      return {
        icon: AlertTriangle,
        title: '网络错误',
        defaultMessage: '网络连接失败，请检查网络设置',
        iconColor: 'text-orange-500',
        bgColor: 'bg-orange-50',
        borderColor: 'border-orange-200'
      }
    default:
      return {
        icon: XCircle,
        title: '出现错误',
        defaultMessage: '发生未知错误，请稍后再试',
        iconColor: 'text-red-500',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200'
      }
  }
}

/**
 * 通用错误页面组件
 * 用于显示各种错误状态，包括加载失败、无数据、网络错误等
 */
export function ErrorPage({
  type = 'error',
  message,
  showRefresh = false,
  onRefresh,
  className = '',
  colors = {
    primary: '#3b82f6',
    secondary: '#64748b',
    lightBorder: '#e2e8f0'
  }
}: ErrorPageProps) {
  const config = getErrorConfig(type)

  return (
    <div className={`flex h-screen items-center justify-center ${className}`}>
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="w-full max-w-md mx-4 text-center"
      >
        {/* 错误图片 */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-4"
        >
          <img 
            src="/error.jpg" 
            alt="错误提示图片"
            className="w-64 h-64 mx-auto object-contain"
          />
        </motion.div>
        
        <motion.h2
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="text-2xl font-bold mb-4 text-center"
          style={{ color: colors.secondary }}
        >
          {config.title}
        </motion.h2>
        
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="text-gray-600 mb-6 text-center"
        >
          {message || config.defaultMessage}
        </motion.p>
        
        {showRefresh && onRefresh && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="flex justify-center"
          >
            <Button
              onClick={onRefresh}
              variant="outline"
              className="flex items-center gap-2"
              style={{ 
                borderColor: colors.lightBorder,
                color: colors.primary
              }}
            >
              <RefreshCw className="w-4 h-4" />
              重新加载
            </Button>
          </motion.div>
        )}
      </motion.div>
    </div>
  )
}

/**
 * 简化版错误显示组件
 * 用于在现有页面中显示错误信息，不占用全屏
 */
export function ErrorCard({
  type = 'error',
  message,
  showRefresh = false,
  onRefresh,
  className = '',
  colors = {
    primary: '#3b82f6',
    secondary: '#64748b',
    lightBorder: '#e2e8f0'
  }
}: ErrorPageProps) {
  const config = getErrorConfig(type)
  const IconComponent = config.icon

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={className}
    >
      <Card className={`${config.bgColor} ${config.borderColor} border`}>
        <CardContent className="p-6">
          <div className="flex items-center gap-3">
            <IconComponent className={`w-5 h-5 ${config.iconColor} flex-shrink-0`} />
            <div className="flex-1">
              <p className="font-medium" style={{ color: colors.secondary }}>
                {config.title}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                {message || config.defaultMessage}
              </p>
            </div>
            {showRefresh && onRefresh && (
              <Button
                onClick={onRefresh}
                variant="ghost"
                size="sm"
                className="flex-shrink-0"
              >
                <RefreshCw className="w-4 h-4" />
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

export default ErrorPage