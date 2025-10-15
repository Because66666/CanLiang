"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

/**
 * 根页面组件 - 自动跳转到/home
 * 这个页面会在访问根路径时自动重定向到/home路由
 */
export default function RootPage() {
  const router = useRouter()

  useEffect(() => {
    // 页面加载时自动跳转到/home
    router.replace('/home')
  }, [router])

  // 显示加载状态，防止闪烁
  return (
    <div className="flex h-screen items-center justify-center bg-background">
      <div className="text-center">
        <div className="inline-flex items-center gap-2 text-muted-foreground">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
          <span>正在跳转到主页...</span>
        </div>
      </div>
    </div>
  )
}
