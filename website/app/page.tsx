"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Search, BarChart2, CalendarIcon } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { motion, AnimatePresence } from "framer-motion"

interface InventoryData {
  item_count: Record<string, number>
}

interface DateItem {
  value: string
  label: string
}

interface CategoryTotal {
  name: string
  count: number
  color: string
}

export default function InventoryPage() {
  const [dateList, setDateList] = useState<DateItem[]>([])
  const [selectedDate, setSelectedDate] = useState<string>("") 
  const [data, setData] = useState<InventoryData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [isChangingDate, setIsChangingDate] = useState(false)
  const [animationKey, setAnimationKey] = useState(0)

  // 定义颜色方案
  const colors = {
    primary: "#3498db", // 主色调：蓝色
    secondary: "#2c3e50", // 次要色调：深蓝
    accent1: "#4CAF50", // 强调色1：绿色
    accent2: "#f39c12", // 强调色2：橙色
    light: "#e6f2ff", // 浅色背景
    lightBorder: "#85b8e8", // 浅色边框
    lightGray: "#f5f5f5", // 浅灰色
    mediumGray: "#bdc3c7", // 中灰色
    darkText: "#003366", // 深色文字
  }

  // 定义类别颜色
  const categoryColors = {
    圣遗物: "#34495e", // 深蓝
    矿物: "#4CAF50", // 绿色
    食材: "#f39c12", // 橙色
    其他: "#bdc3c7", // 浅灰
  }

  // 定义排行榜颜色
  const rankingColors = [
    "#3498db", // 蓝色
    "#27ae60", // 绿色
    "#f39c12", // 橙色
    "#9b59b6", // 紫色
    "#e74c3c", // 红色
    "#1abc9c", // 青色
    "#d35400", // 深橙色
    "#2980b9", // 深蓝色
    "#8e44ad", // 深紫色
    "#c0392b", // 深红色
  ]

    // 处理日期变化
  const handleDateChange = (newDate: string) => {
      if (newDate !== selectedDate) {
        setIsChangingDate(true)
  
        // 短暂延迟以允许退出动画完成
        setTimeout(() => {
          setSelectedDate(newDate)
          setAnimationKey((prev) => prev + 1)
  
          // 模拟数据加载
          setLoading(true)
          setTimeout(() => {
            setLoading(false)
            setIsChangingDate(false)
          }, 600)
        }, 300)
      }
    }

  // 从API获取日期列表
  useEffect(() => {
    const fetchDateList = async () => {
      try {
        setLoading(true)
        const response = await fetch('/api/LogList')
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const responseData = await response.json()
        // 从返回的JSON中提取日期列表
        const dates = responseData.list || []
        // 将日期转换为Select组件需要的格式
        const formattedDates = Array.isArray(dates) ? dates.map(date => ({
          value: date,
          label: date
        })) : []
        
        setDateList(formattedDates)
        
        // 设置第一个日期为默认选中日期
        if (formattedDates.length > 0) {
          setSelectedDate(formattedDates[0].value)
        }
        
        setError(null)
      } catch (error) {
        console.error('Error fetching date list:', error)
        setError('获取日期列表失败，请稍后再试')
      } finally {
        setLoading(false)
      }
    }

    fetchDateList()
  }, [])

  // 获取物品数据
  useEffect(() => {
    const fetchData = async () => {
      if (!selectedDate) return
      
      try {
        setLoading(true)
        const response = await fetch(`/api/analyse?date=${selectedDate}`)
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        setData(data)
        setError(null)
      } catch (error) {
        console.error('Error fetching data:', error)
        setError('获取数据失败，请稍后再试')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [selectedDate])

  // 物品分类逻辑
  const getCategory = (name: string) => {
    if (
      name.includes("冒险家") ||
      name.includes("游医") ||
      name.includes("幸运儿") ||
      name.includes("险家") ||
      name.includes("医的") ||
      name.includes("运儿") ||
      name.includes("家") ||
      (name.includes("的") &&
        (name.includes("方巾") ||
          name.includes("枭羽") ||
          name.includes("怀钟") ||
          name.includes("药壶") ||
          name.includes("银莲") ||
          name.includes("怀表") ||
          name.includes("尾羽") ||
          name.includes("头带") ||
          name.includes("金杯") ||
          name.includes("之花") ||
          name.includes("之杯") ||
          name.includes("沙漏") ||
          name.includes("绿花") ||
          name.includes("银冠") ||
          name.includes("鹰羽")))
    ) {
      return "圣遗物"
    } else if (['铁块', '白铁块', '水晶块', '魔晶块', '星银矿石', '紫晶块', '萃凝晶'].includes(name)) {
      return "矿物"
    } else if (
      ['苹果', '蘑菇', '甜甜花', '胡萝卜', '白萝卜', '金鱼草', '薄荷',
         '松果', '树莓', '松茸', '鸟蛋', '海草', '堇瓜', '墩墩桃',
          '须弥蔷薇', '枣椰', '茉洁草', '沉玉仙茗', '颗粒果', '澄晶实',
           '红果果菇', '小灯草', '嘟嘟莲', '莲蓬', '绝云椒椒', '清心',
            '马尾', '琉璃袋', '竹笋', '绯樱绣球', '树王圣体菇', '帕蒂沙兰',
             '青蜜莓'].includes(name)
    ) {
      return "食材"
    } else {
      return "其他"
    }
  }

  // 对物品进行分类
  const categorizeItems = (items: Record<string, number>) => {
    const categories: Record<string, Record<string, number>> = {
      圣遗物: {},
      矿物: {},
      食材: {},
      其他: {},
    }

    Object.entries(items).forEach(([name, count]) => {
      let category = getCategory(name)
      categories[category][name] = count
    })

    return categories
  }

    // 计算每个分类的总数量
    const getCategoryTotals = (categories: Record<string, Record<string, number>>) => {
  
      const totals: CategoryTotal[] = []
  
      Object.entries(categories).forEach(([name, items]) => {
        const count = Object.values(items).reduce((sum, count) => sum + count, 0)
        totals.push({
          name,
          count,
          color: categoryColors[name as keyof typeof categoryColors],
        })
      })
  
      return totals
    }

  // 过滤和排序物品
  const getTop5Items = (items: Record<string, number>) => {
    return Object.entries(items)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
  }

  // 过滤和排序物品 (默认按数量排序)
  const filterAndSortItems = (items: Record<string, number>) => {
    return Object.entries(items)
      .filter(([name]) => name.toLowerCase().includes(searchTerm.toLowerCase()))
      .sort((a, b) => b[1] - a[1])
  }

  // 获取总物品数量
  const getTotalItemCount = (items: Record<string, number>) => {
    return Object.values(items).reduce((sum, count) => sum + count, 0)
  }

  // 获取物品种类数量
  const getUniqueItemCount = (items: Record<string, number>) => {
    return Object.keys(items).length
  }

    // 生成饼图SVG路径
  const generatePieChart = (data: CategoryTotal[]) => {
      const total = data.reduce((sum, item) => sum + item.count, 0)
      let currentAngle = 0
  
      return data.map((item, index) => {
        const percentage = item.count / total
        const startAngle = currentAngle
        const endAngle = currentAngle + percentage * 2 * Math.PI
  
        // 计算SVG路径
        const x1 = 100 + 80 * Math.cos(startAngle)
        const y1 = 100 + 80 * Math.sin(startAngle)
        const x2 = 100 + 80 * Math.cos(endAngle)
        const y2 = 100 + 80 * Math.sin(endAngle)
  
        // 大弧标志 (large-arc-flag)
        const largeArcFlag = percentage > 0.5 ? 1 : 0
  
        // 创建SVG路径
        const path = `M 100 100 L ${x1} ${y1} A 80 80 0 ${largeArcFlag} 1 ${x2} ${y2} Z`
  
        currentAngle = endAngle
  
        return {
          path,
          color: item.color,
          name: item.name,
          count: item.count,
          percentage: (percentage * 100).toFixed(1),
        }
      })
    }
      // 获取物品对应的颜色
  const getItemColor = (name: string) => {
    let category = getCategory(name)
    return categoryColors[category as keyof typeof categoryColors]
  }
 // 动画变体
 const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.5,
      when: "beforeChildren",
      staggerChildren: 0.1,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      duration: 0.3,
      when: "afterChildren",
      staggerChildren: 0.05,
      staggerDirection: -1,
    },
  },
}

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: { duration: 0.3 },
  },
  exit: {
    y: -20,
    opacity: 0,
    transition: { duration: 0.2 },
  },
}

const chartVariants = {
  hidden: { scale: 0.9, opacity: 0 },
  visible: {
    scale: 1,
    opacity: 1,
    transition: { duration: 0.4, type: "spring", stiffness: 100 },
  },
  exit: {
    scale: 0.9,
    opacity: 0,
    transition: { duration: 0.3 },
  },
}
  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="text-xl flex flex-col items-center"
        >
          <div className="w-12 h-12 border-4 border-t-transparent border-primary rounded-full animate-spin mb-4"></div>
          <div>加载中...</div>
        </motion.div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-xl text-red-500">错误: {error}</div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-xl">无数据</div>
      </div>
    )
  }

  const categories = categorizeItems(data.item_count)
  const totalItems = getTotalItemCount(data.item_count)
  const uniqueItems = getUniqueItemCount(data.item_count)
  const duration = data.duration
  const top10Items = getTop5Items(data.item_count)
  const categoryTotals = getCategoryTotals(categories)
  const pieChartData = generatePieChart(categoryTotals)

  // 找出最大数量，用于计算条形图比例
  const maxCount = top10Items[0][1]
  return (
    <div className="container mx-auto px-4 py-8 bg-white">
      <h1 className="mb-8 text-3xl font-bold text-center" style={{ color: colors.secondary }}>
        参量质变仪
      </h1>

      {/* 统计卡片 */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-3"
      >
        <motion.div variants={itemVariants}>
          <Card className="border-0 shadow-sm overflow-hidden" style={{ backgroundColor: colors.light }}>
            <CardContent className="flex items-center justify-between p-6">
              <div>
                <p className="text-sm" style={{ color: colors.secondary }}>
                  总物品数量
                </p>
                <p className="text-3xl font-bold" style={{ color: colors.darkText }}>
                  {totalItems}
                </p>
              </div>
              <BarChart2 className="h-8 w-8" style={{ color: colors.primary }} />
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="border-0 shadow-sm overflow-hidden" style={{ backgroundColor: colors.light }}>
            <CardContent className="flex items-center justify-between p-6">
              <div>
                <p className="text-sm" style={{ color: colors.secondary }}>
                  运行时间
                </p>
                <p className="text-3xl font-bold" style={{ color: colors.darkText }}>
                  {duration}
                </p>
              </div>
              <BarChart2 className="h-8 w-8" style={{ color: colors.primary }} />
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="border-0 shadow-sm overflow-hidden" style={{ backgroundColor: colors.light }}>
            <CardContent className="flex items-center justify-between p-6">
              <div>
                <p className="text-sm" style={{ color: colors.secondary }}>
                  最多物品
                </p>
                <p className="text-3xl font-bold" style={{ color: colors.darkText }}>
                  {Object.entries(data.item_count).sort((a, b) => b[1] - a[1])[0][0]}
                </p>
              </div>
              <BarChart2 className="h-8 w-8" style={{ color: colors.primary }} />
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>

      {/* 主要内容区域 - 分为左侧条形图和右侧物品列表 */}
      <div className="flex flex-col lg:flex-row gap-8">
        {/* 左侧图表 */}
        <div className="w-full lg:w-1/3 space-y-8">
          {/* 条形图 */}
          <AnimatePresence mode="wait">
            <motion.div
              key={`bar-chart-${animationKey}`}
              variants={chartVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
            >
              <Card className="border-0 shadow-sm overflow-hidden">
                <CardContent className="p-6">
                  <h2 className="text-xl font-bold mb-4" style={{ color: colors.secondary }}>
                    物品数量排行（前五个）
                  </h2>
                  <div className="space-y-4">
                    {top10Items.slice(0, 5).map(([name, count], index) => (
                      <motion.div
                        key={index}
                        className="flex flex-col"
                        initial={{ x: -20, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        transition={{ delay: index * 0.1, duration: 0.3 }}
                      >
                        <div className="flex justify-between text-sm mb-1">
                          <span className="font-medium truncate">{name}</span>
                          <span style={{ color: colors.secondary }}>{count}</span>
                        </div>
                        <div className="w-full bg-gray-100 rounded-full h-3">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${(count / maxCount) * 100}%` }}
                            transition={{ duration: 0.8, delay: 0.2 + index * 0.1 }}
                            className="h-3 rounded-full"
                            style={{
                              backgroundColor: rankingColors[index % rankingColors.length],
                            }}
                          ></motion.div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </AnimatePresence>

          {/* 饼状图 */}
          <AnimatePresence mode="wait">
            <motion.div
              key={`pie-chart-${animationKey}`}
              variants={chartVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
            >
              <Card className="border-0 shadow-sm overflow-hidden">
                <CardContent className="p-6">
                  <h2 className="text-xl font-bold mb-4" style={{ color: colors.secondary }}>
                    物品类别分布
                  </h2>
                  <div className="flex flex-col items-center">
                    <motion.div
                      className="relative w-[200px] h-[200px]"
                      initial={{ rotate: -90, opacity: 0 }}
                      animate={{ rotate: 0, opacity: 1 }}
                      transition={{ duration: 0.8, type: "spring" }}
                    >
                      <svg viewBox="0 0 200 200" className="w-full h-full">
                        {pieChartData.map((segment, index) => (
                          <motion.path
                            key={index}
                            d={segment.path}
                            fill={segment.color}
                            stroke="white"
                            strokeWidth="1"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.1 * index, duration: 0.5 }}
                          />
                        ))}
                      </svg>
                    </motion.div>
                    <div className="mt-6 grid grid-cols-2 gap-x-4 gap-y-3 w-full">
                      {categoryTotals.map((category, index) => (
                        <motion.div
                          key={index}
                          className="flex items-center"
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.3 + 0.1 * index, duration: 0.3 }}
                        >
                          <div
                            className="w-4 h-4 mr-2 flex-shrink-0 rounded-sm"
                            style={{ backgroundColor: category.color }}
                          ></div>
                          <div className="flex justify-between w-full">
                            <span className="text-sm font-medium">{category.name}</span>
                            <span className="text-sm" style={{ color: colors.secondary }}>
                              {category.count} ({pieChartData[index].percentage}%)
                            </span>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* 右侧物品列表 */}
        <div className="w-full lg:w-2/3">
          {/* 搜索和日期选择区域 */}
          <div className="mb-8 p-6 rounded-lg" style={{ backgroundColor: colors.light }}>

            {/* 搜索 */}
            <div className="mb-6 flex flex-col items-center gap-4">
              <div className="relative w-full max-w-md">
                <Search className="absolute left-3 top-3 h-4 w-4" style={{ color: colors.primary }} />
                <Input
                  placeholder="搜索物品..."
                  className="pl-10 py-6 border-0 shadow-sm focus:ring-2"
                  style={{
                    borderColor: colors.lightBorder,
                    boxShadow: `0 0 0 1px ${colors.lightBorder}`,
                  }}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            {/* 日期选择 */}
            <div className="flex flex-col items-center gap-4">
              <div className="flex items-center gap-2">
                <CalendarIcon className="h-4 w-4" style={{ color: colors.primary }} />
                <span className="text-sm" style={{ color: colors.secondary }}>
                  选择日期:
                </span>
              </div>
              <Select value={selectedDate} onValueChange={handleDateChange}>
                <SelectTrigger
                  className="w-[240px] border-0 shadow-sm focus:ring-2"
                  style={{
                    borderColor: colors.lightBorder,
                    boxShadow: `0 0 0 1px ${colors.lightBorder}`,
                  }}
                >
                  <SelectValue placeholder="选择日期" />
                </SelectTrigger>
                <SelectContent>
                  {dateList.map((date) => (
                    <SelectItem key={date.value} value={date.value}>
                      {date.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* 物品列表 */}
          <Tabs defaultValue="all" className="flex flex-col items-center">
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
              <TabsList className="mb-6 p-1 rounded-md" style={{ backgroundColor: colors.lightGray }}>
                <TabsTrigger
                  value="all"
                  className="data-[state=active]:text-white"
                  style={{
                    backgroundColor: "transparent",
                    color: colors.secondary,
                    ["--tw-data-state-active-bg" as any]: colors.primary,
                  }}
                >
                  全部
                </TabsTrigger>
                {Object.keys(categories).map((category) => (
                  <TabsTrigger
                    key={category}
                    value={category}
                    className="data-[state=active]:text-white"
                    style={{
                      backgroundColor: "transparent",
                      color: colors.secondary,
                      ["--tw-data-state-active-bg" as any]: colors.primary,
                    }}
                  >
                    {category}
                  </TabsTrigger>
                ))}
              </TabsList>
            </motion.div>

            <div className="w-full">
              <AnimatePresence mode="wait">
                <TabsContent value="all">
                  <motion.div
                    key={`all-items-${animationKey}`}
                    variants={containerVariants}
                    initial="hidden"
                    animate="visible"
                    exit="exit"
                    className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3"
                  >
                    {filterAndSortItems(data.item_count).map(([name, count], index) => (
                      <motion.div key={name} variants={itemVariants}>
                        <ItemCard name={name} count={count} color={getItemColor(name)} />
                      </motion.div>
                    ))}
                  </motion.div>
                </TabsContent>

                {Object.entries(categories).map(([category, items]) => (
                  <TabsContent key={category} value={category}>
                    <motion.div
                      key={`${category}-items-${animationKey}`}
                      variants={containerVariants}
                      initial="hidden"
                      animate="visible"
                      exit="exit"
                      className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3"
                    >
                      {filterAndSortItems(items).map(([name, count], index) => (
                        <motion.div key={name} variants={itemVariants}>
                          <ItemCard
                            name={name}
                            count={count}
                            color={categoryColors[category as keyof typeof categoryColors]}
                          />
                        </motion.div>
                      ))}
                    </motion.div>
                  </TabsContent>
                ))}
              </AnimatePresence>
            </div>
          </Tabs>
        </div>
      </div>
    </div>
  )
}

function ItemCard({ name, count, color }: { name: string; count: number; color: string }) {
  return (
    <Card className="border border-gray-100 hover:shadow-md transition-shadow duration-200">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="truncate font-medium">{name}</div>
          <div
            className="ml-2 rounded-full px-2 py-1 text-xs font-semibold text-white"
            style={{ backgroundColor: color }}
          >
            {count}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
