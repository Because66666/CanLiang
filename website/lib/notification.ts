import { Notyf } from 'notyf'
import 'notyf/notyf.min.css'

/**
 * 通知类型枚举
 */
export enum NotificationType {
  SUCCESS = 'success',
  ERROR = 'error',
  WARNING = 'warning',
  INFO = 'info'
}

/**
 * 通知配置接口
 */
interface NotificationConfig {
  message: string
  type: NotificationType
  duration?: number
  dismissible?: boolean
}

/**
 * 统一的通知管理器类
 */
class NotificationManager {
  private notyf: Notyf | null = null

  constructor() {
    // 只在客户端环境中初始化Notyf实例
    if (typeof window !== 'undefined') {
      this.notyf = new Notyf({
        duration: 4000, // 默认显示4秒
        position: {
          x: 'right',
          y: 'top'
        },
        dismissible: true,
        types: [
          {
            type: 'warning',
            background: 'orange',
            icon: {
              className: 'material-icons',
              tagName: 'i',
              text: 'warning'
            }
          },
          {
            type: 'info',
            background: 'blue',
            icon: {
              className: 'material-icons',
              tagName: 'i',
              text: 'info'
            }
          }
        ]
      })
    }
  }

  /**
   * 显示成功通知
   * @param message 消息内容
   * @param duration 显示时长（毫秒）
   */
  success(message: string, duration?: number): void {
    if (!this.notyf) return
    this.notyf.success({
      message,
      duration: duration || 4000
    })
  }

  /**
   * 显示错误通知
   * @param message 错误消息
   * @param duration 显示时长（毫秒）
   */
  error(message: string, duration?: number): void {
    if (!this.notyf) return
    this.notyf.error({
      message,
      duration: duration || 5000 // 错误消息显示时间稍长
    })
  }

  /**
   * 显示警告通知
   * @param message 警告消息
   * @param duration 显示时长（毫秒）
   */
  warning(message: string, duration?: number): void {
    if (!this.notyf) return
    this.notyf.open({
      type: 'warning',
      message,
      duration: duration || 4000
    })
  }

  /**
   * 显示信息通知
   * @param message 信息消息
   * @param duration 显示时长（毫秒）
   */
  info(message: string, duration?: number): void {
    if (!this.notyf) return
    this.notyf.open({
      type: 'info',
      message,
      duration: duration || 3000
    })
  }

  /**
   * 通用通知方法
   * @param config 通知配置
   */
  notify(config: NotificationConfig): void {
    switch (config.type) {
      case NotificationType.SUCCESS:
        this.success(config.message, config.duration)
        break
      case NotificationType.ERROR:
        this.error(config.message, config.duration)
        break
      case NotificationType.WARNING:
        this.warning(config.message, config.duration)
        break
      case NotificationType.INFO:
        this.info(config.message, config.duration)
        break
      default:
        this.info(config.message, config.duration)
    }
  }

  /**
   * 清除所有通知
   */
  dismissAll(): void {
    if (!this.notyf) return
    this.notyf.dismissAll()
  }
}

// 创建全局通知管理器实例
export const notificationManager = new NotificationManager()

/**
 * 便捷的通知函数
 */
export const notify = {
  /**
   * 显示成功通知
   * @param message 消息内容
   * @param duration 显示时长（毫秒）
   */
  success: (message: string, duration?: number) => {
    notificationManager.success(message, duration)
  },

  /**
   * 显示错误通知
   * @param message 错误消息
   * @param duration 显示时长（毫秒）
   */
  error: (message: string, duration?: number) => {
    notificationManager.error(message, duration)
  },

  /**
   * 显示警告通知
   * @param message 警告消息
   * @param duration 显示时长（毫秒）
   */
  warning: (message: string, duration?: number) => {
    notificationManager.warning(message, duration)
  },

  /**
   * 显示信息通知
   * @param message 信息消息
   * @param duration 显示时长（毫秒）
   */
  info: (message: string, duration?: number) => {
    notificationManager.info(message, duration)
  },

  /**
   * 清除所有通知
   */
  dismissAll: () => {
    notificationManager.dismissAll()
  }
}

export default notify