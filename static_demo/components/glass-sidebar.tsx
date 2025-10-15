"use client"

import React, { useState, useEffect } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { colors } from "@/lib/utils-inventory"
import { 
  Home, 
  Globe, 
  MessageSquare,
  Menu, 
  X, 
  ChevronLeft,
  BarChart3,
  Settings,
  Info
} from "lucide-react"
import { Button } from "@/components/ui/button"

interface GlassSidebarProps {
  className?: string
}

/**
 * 磨砂玻璃质感侧边栏组件
 * 提供导航功能，支持悬浮显示/隐藏状态，具有60%透明度的磨砂玻璃效果
 * 置于顶层，不影响其他界面的布局
 */
export function GlassSidebar({ className }: GlassSidebarProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [isCollapsed, setIsCollapsed] = useState(false)
  const pathname = usePathname()

  // 导航菜单项配置
  const menuItems = [
    {
      title: "首页",
      href: "/home",
      icon: Home,
      description: "数据概览和统计"
    },
    {
      title: "BetterGI面板",
      href: "/webinfo", 
      icon: MessageSquare,
      description: "消息通知与实时屏看"
    },
    {
      title: "关于",
      href: "/about",
      icon: Info,
      description: "应用信息"
    }
  ]

  /**
   * 处理鼠标进入触发区域
   */
  const handleMouseEnter = () => {
    setIsVisible(true)
  }

  /**
   * 处理鼠标离开侧边栏
   */
  const handleMouseLeave = () => {
    setIsVisible(false)
  }

  /**
   * 切换侧边栏展开/收起状态
   */
  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed)
  }

  /**
   * 点击式打开侧边栏
   */
  const handleTabClick = () => {
    setIsVisible(true)
  }

  return (
    <>
      {/* 左侧触发区域 */}
      <div
        className="fixed left-0 top-0 w-4 h-full z-40 bg-transparent"
        onMouseEnter={handleMouseEnter}
      />
      
      {/* 侧边栏打开标签 - 仅在侧边栏隐藏时显示 */}
      {!isVisible && (
        <div
          className="fixed left-0 top-1/2 -translate-y-1/2 z-50 cursor-pointer group"
          onClick={handleTabClick}
        >
          <div 
            className="backdrop-blur-md border border-white/30 rounded-r-lg shadow-lg px-2 py-4 transition-all duration-300 hover:shadow-xl"
            style={{ backgroundColor: colors.light }}
          >
            <div className="flex flex-col items-center gap-1">
              <Menu 
                className="w-4 h-4 transition-colors" 
                style={{ 
                  color: colors.secondary,
                  transition: 'color 0.3s ease'
                }}
                onMouseEnter={(e) => e.currentTarget.style.color = colors.primary}
                onMouseLeave={(e) => e.currentTarget.style.color = colors.secondary}
              />
              <div 
                className="w-0.5 h-8 rounded-full opacity-60 group-hover:opacity-100 transition-opacity"
                style={{
                  background: `linear-gradient(to bottom, ${colors.primary}, ${colors.accent1})`
                }}
              />
            </div>
          </div>
        </div>
      )}
      
      {/* 侧边栏主体 */}
      <div
        className={cn(
          "fixed left-0 top-0 z-50 h-full transition-all duration-300 ease-in-out",
          "backdrop-blur-md bg-white/60 border-r border-white/20",
          "shadow-xl shadow-black/5",
          isVisible ? "translate-x-0" : "-translate-x-full",
          isCollapsed ? "w-16" : "w-64",
          className
        )}
        style={{
          backdropFilter: "blur(12px)",
          WebkitBackdropFilter: "blur(12px)",
        }}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
      {/* 侧边栏头部 */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-white/10">
        {!isCollapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg overflow-hidden">
              <img 
                src="/canliang.png" 
                alt="参量质变仪图标" 
                className="w-full h-full object-cover"
              />
            </div>
            <span className="font-semibold text-gray-800">参量质变仪</span>
          </div>
        )}
        
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleCollapse}
          className="h-8 w-8 p-0 hover:bg-white/20"
        >
          {isCollapsed ? (
            <Menu className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* 导航菜单 */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200",
                "hover:bg-white/30 hover:shadow-sm",
                "group relative",
                isActive && "bg-white/40 shadow-md border border-white/30",
                isCollapsed && "justify-center"
              )}
            >
              <Icon 
                className={cn(
                  "w-5 h-5 transition-colors",
                  isActive ? "text-blue-600" : "text-gray-600 group-hover:text-gray-800"
                )} 
              />
              
              {!isCollapsed && (
                <div className="flex-1 min-w-0">
                  <div className={cn(
                    "font-medium text-sm transition-colors",
                    isActive ? "text-blue-600" : "text-gray-700 group-hover:text-gray-900"
                  )}>
                    {item.title}
                  </div>
                  <div className="text-xs text-gray-500 truncate">
                    {item.description}
                  </div>
                </div>
              )}

              {/* 收起状态下的悬浮提示 */}
              {isCollapsed && (
                <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
                  {item.title}
                </div>
              )}
            </Link>
          )
        })}
      </nav>

      {/* 侧边栏底部 */}
      <div className="p-4 border-t border-white/10">
        {!isCollapsed && (
          <div className="text-xs text-gray-500 text-center">
            © 2025 Because66666
          </div>
        )}
      </div>
    </div>
    </>
  )
}