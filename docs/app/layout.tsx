import type React from "react"
import "@/app/globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { GlassSidebar } from "@/components/glass-sidebar"

export const metadata = {
  title: "参量质变仪",
  description: "关于游戏中交互和拾取物品的统计数据可视化",
    generator: 'v0.dev'
}

/**
 * 根布局组件
 * 包含磨砂玻璃侧边栏（悬浮显示）和主要内容区域
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body className="bg-white text-black min-h-screen">
        <ThemeProvider attribute="class" enableSystem={false} disableTransitionOnChange>
          {/* 磨砂玻璃侧边栏 - 悬浮显示，不影响布局 */}
          <GlassSidebar />
          
          {/* 主内容区域 - 占据全屏宽度 */}
          <main className="min-h-screen">
            {children}
          </main>
        </ThemeProvider>
      </body>
    </html>
  )
}
