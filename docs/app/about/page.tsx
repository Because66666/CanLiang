"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { motion } from "framer-motion"
import { 
  Zap, 
  FileText, 
  BarChart3, 
  Globe, 
  User, 
  Scale, 
  Heart,
  CheckCircle,
  Settings,
  Database,
  MessageSquare,
  Github,
  ExternalLink
} from "lucide-react"

/**
 * 关于页面主组件
 * 展示参量质变仪：BetterGI日志分析工具的详细信息
 */
export default function AboutPage() {
  /**
   * 功能特性列表
   */
  const features = [
    {
      icon: <Settings className="w-5 h-5 text-blue-500" />,
      title: "自动检测BetterGI安装路径",
      description: "智能识别并定位BetterGI的安装目录"
    },
    {
      icon: <FileText className="w-5 h-5 text-green-500" />,
      title: "分析BetterGI日志文件",
      description: "深度解析日志文件中的各类型事件信息"
    },
    {
      icon: <BarChart3 className="w-5 h-5 text-purple-500" />,
      title: "统计交互拾取数据",
      description: "统计交互或拾取物品的出现次数和频率"
    },
    {
      icon: <Database className="w-5 h-5 text-orange-500" />,
      title: "REST API接口",
      description: "提供完整的API接口进行日志分析"
    },
    {
      icon: <Globe className="w-5 h-5 text-cyan-500" />,
      title: "Web界面展示",
      description: "通过直观的Web界面展示分析结果"
    },
    {
      icon: <MessageSquare className="w-5 h-5 text-cyan-500" />,
      title: "实时信息流",
      description: "通过实时Webhook支持，及时获取游戏事件信息"
    },
  ]

  return (
    <main className="min-h-screen bg-background">
      {/* 主要内容区域 */}
      <div className="container mx-auto py-8 px-4 max-w-4xl">
        {/* 页面标题 */}
        <motion.div 
          className="mb-8 text-center"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-800 to-blue-400 bg-clip-text text-transparent">
            参量质变仪：BetterGI日志分析工具
          </h1>
          <p className="text-lg text-muted-foreground">
            专业的BetterGI日志分析与数据统计工具
          </p>
        </motion.div>

        {/* 项目介绍 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.5 }}
        >
          <Card className="mb-8">
            <CardContent className="p-8">
              <div className="flex items-center gap-3 mb-6">
                <Zap className="w-6 h-6 text-yellow-500" />
                <h2 className="text-2xl font-bold">项目介绍</h2>
              </div>
              <div className="prose prose-gray dark:prose-invert max-w-none">
                <p className="text-base leading-relaxed mb-4">
                  参量质变仪：BetterGI日志分析工具是一个专门用于分析BetterGI（Better Genshin Impact）日志文件的应用程序。
                  该工具提供了直观的Web界面，帮助用户查看和分析BetterGI生成的日志信息，特别是关于游戏中交互和拾取物品的统计数据。
                  此外还提供了Webhook信息流界面，可以几乎实时地查看BGI提供的事件信息。
                </p>
                <p className="text-base leading-relaxed">
                  通过先进的日志解析技术和现代化的Web界面设计，为用户提供全面、准确、易用的日志分析体验。
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* 主要功能 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.5 }}
        >
          <Card className="mb-8">
            <CardContent className="p-8">
              <div className="flex items-center gap-3 mb-6">
                <CheckCircle className="w-6 h-6 text-green-500" />
                <h2 className="text-2xl font-bold">主要功能</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {features.map((feature, index) => (
                  <motion.div
                    key={index}
                    className="flex items-start gap-4 p-4 rounded-lg bg-muted/50 hover:bg-muted/80 transition-colors"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + index * 0.1, duration: 0.3 }}
                  >
                    <div className="flex-shrink-0 mt-1">
                      {feature.icon}
                    </div>
                    <div>
                      <h3 className="font-semibold mb-2">{feature.title}</h3>
                      <p className="text-sm text-muted-foreground">{feature.description}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* 开发者信息 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.5 }}
        >
          <Card className="mb-8">
            <CardContent className="p-8">
              <div className="flex items-center gap-3 mb-6">
                <User className="w-6 h-6 text-blue-500" />
                <h2 className="text-2xl font-bold">开发者信息</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <span className="font-medium text-muted-foreground">作者:</span>
                    <Badge variant="secondary" className="text-base px-3 py-1">
                      Because66666
                    </Badge>
                  </div>
                  <div className="flex items-center gap-3">
                    <Github className="w-5 h-5 text-gray-700 dark:text-gray-300" />
                    <div>
                      <h3 className="font-semibold mb-1">GitHub项目</h3>
                      <a 
                        href="https://github.com/Because66666/CanLiang" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 transition-colors flex items-center gap-1"
                      >
                        Because66666/CanLiang
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Scale className="w-5 h-5 text-gray-500" />
                  <div>
                    <h3 className="font-semibold mb-1">许可证</h3>
                    <p className="text-sm text-muted-foreground">
                      本项目遵循Apache-2.0 License许可证
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>


        {/* 页面底部 */}
        <motion.div
          className="text-center text-sm text-muted-foreground"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.5 }}
        >
          <p>感谢您使用参量质变仪：BetterGI日志分析工具</p>
        </motion.div>
      </div>
    </main>
  )
}