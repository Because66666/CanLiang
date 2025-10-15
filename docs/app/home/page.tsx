"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Search, BarChart2, CalendarIcon, Github, TrendingUp, Clock, Package } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { motion } from "framer-motion"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Download, X } from "lucide-react"
import { analysistools } from "@/lib/functions"

// 导入类型定义
import { 
  InventoryData, 
  DateItem, 
  CategoryTotal, 
  ItemTrendData, 
  StatModalData,
  PageState, 
  ItemDataDict,
  DurationDict
} from "@/types/inventory"

// 导入API服务
import { apiService } from "@/lib/api"

// 导入工具函数
import {
  categorizeItems,
  getCategoryTotals,
  getTopItems,
  filterAndSortItems,
  getTotalItemCount,
  getUniqueItemCount,
  generatePieChart,
  getItemColor,
  colors,
  categoryColors,
  rankingColors
} from "@/lib/utils-inventory"

// 导入UI组件
import { ItemCard } from "@/components/inventory/ItemCard"
import { StatCard } from "@/components/inventory/StatCard"
import { ItemModal } from "@/components/inventory/ItemModal"
import { StatModal } from "@/components/inventory/StatModal"
import { DownloadDialog } from "@/components/inventory/DownloadDialog"
import { ErrorPage } from "@/components/ErrorPage"

export default function InventoryPage() {
  // 页面状态管理
  const [dateList, setDateList] = useState<DateItem[]>([])
  const [taskList, setTaskList] = useState<string[]>([])
  const [itemData, setItemData] = useState<ItemDataDict>()
  const [durationData, setDurationData] = useState<DurationDict>()
  const [selectedDate, setSelectedDate] = useState<string>("") 
  const [selectedTask, setSelectedTask] = useState<string>("")
  const [data, setData] = useState<InventoryData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [isChangingDate, setIsChangingDate] = useState(false)
  const [animationKey, setAnimationKey] = useState(0)
  const [hoverIndex, setHoverIndex] = useState<number | null>(null)
  const [selectedItem, setSelectedItem] = useState<string | null>(null)
  const [itemTrendData, setItemTrendData] = useState<ItemTrendData | null>(null)
  const [loadingTrend, setLoadingTrend] = useState(false)
  const [statModal, setStatModal] = useState<StatModalData | null>(null)
  const [downloadDialogOpen, setDownloadDialogOpen] = useState(false)
  const [downloadLoading, setDownloadLoading] = useState(false)

  // 使用导入的颜色常量
  // colors, categoryColors, rankingColors 已经从 utils-inventory 导入

  // 处理统计卡片点击
  const handleStatClick = async (type: "totalItems" | "duration") => {
    const titles = {
      totalItems: "物品数量趋势",
      duration: "运行时间趋势",
    }

    if (selectedTask !== 'all'){
      setStatModal({
      type,
      title: `【${selectedTask}】${titles[type]}`,
      data: null,
      loading: true,
    })
    }
    else{
      setStatModal({
        type,
        title: `总${titles[type]}`,
        data: null,
        loading: true,
      })
    }

    try {
      const trendData = analysistools.calculateTrendData(type, itemData!, durationData!, selectedTask)
      setStatModal((prev) => (prev ? { ...prev, data: trendData, loading: false } : null))
    } catch (error) {
      console.error(`获取${titles[type]}数据失败:`, error)
      setStatModal((prev) => (prev ? { ...prev, data: {}, loading: false } : null))
    }
  }

  // 处理物品点击
  const handleItemClick = async (itemName: string) => {
    setSelectedItem(itemName)
    setLoadingTrend(true)
    setItemTrendData(null)

    try {
      const trendData = analysistools.calculateAnItemTrend(itemName, itemData!, selectedTask)
      setItemTrendData(trendData)
    } catch (error) {
      console.error("获取物品趋势数据失败:", error)
      setItemTrendData({})
    } finally {
      setLoadingTrend(false)
    }
  }

  // 关闭物品详情模态框
  const closeItemModal = () => {
    setSelectedItem(null)
    setItemTrendData(null)
  }
    // 关闭统计模态框
  const closeStatModal = () => {
    setStatModal(null)
  }

  // 处理数据下载
  const handleDataDownload = async (dataType: string) => {
    setDownloadLoading(true)
    try {
      const downloadData = await analysistools.saveAllData(dataType, itemData!, durationData!)     
      setDownloadDialogOpen(false)
    } catch (error) {
      console.error('下载失败:', error)
      alert('下载失败，请稍后再试')
    } finally {
      setDownloadLoading(false)
    }
  }

    // 处理日期变化
  const handleDateChange = (newDate: string) => {
      if (newDate !== selectedDate) {
        setSelectedDate(newDate)
        setAnimationKey((prev) => prev + 1) // 更新动画key以触发饼状图重新动画
      }
    }
  const handleTaskChange = (newTask: string) => {
    if (newTask !== selectedTask) {
      setSelectedTask(newTask)
      setAnimationKey((prev) => prev + 1) // 更新动画key以触发饼状图重新动画
    }
  }

  // 从API获取日期列表 和 数据表
  useEffect(() => {
    const fetchDateList = async () => {
      try {
        // 关于/api/LogList
        setLoading(true)
        const result = await apiService.fetchDateList()
        // 确保日期列表是倒序排列（大的日期在前面）
        result.sort((a, b) => b.value.localeCompare(a.value))
        setDateList(result)
        
        
        // 关于/api/LogData
        const {itemData,durationData} = await apiService.fetchAllData()
        setItemData(itemData)
        setDurationData(durationData)

        // 设置第一个日期为默认选中日期
        if (result.length > 0) {
          setSelectedDate(result[0].value)
          setSelectedTask('all')
          // 对应日期下的配置组列表筛选
          let {processedData, filteredData} = analysistools.calculateItemTrend(itemData, durationData,result[0].value,'all')
          let task_list = [...new Set(filteredData.Task)]
          task_list.unshift('all')
          setTaskList(task_list)
        }

        setError(null)
      } catch (error) {
        console.error('获取日期列表失败:', error)
        setError('获取日期列表失败，请稍后再试')
      } finally {
        setLoading(false)
      }
    }

    fetchDateList()
  }, [])

  const handleSelectAll = () => {
    setSelectedDate('all')  // 设定一个特殊值来表示“全部”
    setSelectedTask('all')
    setAnimationKey((prev) => prev + 1) // 更新动画key以触发饼状图重新动画
  }

  // 当发生筛选的时候，获取物品数据
  useEffect(() => {
    const fetchData = async () => {
      if (!selectedDate ||!itemData || !durationData) return

      try {
        // console.log('selectedDate',selectedDate,'selectedTask',selectedTask)
        setLoading(true)
        // 根据初始条件进行尝试筛选
        let {processedData, filteredData} = 
        analysistools.calculateItemTrend(itemData, durationData, selectedDate, selectedTask)      
        // 检查item_count是否为空
        if (!processedData.item_count || Object.keys(processedData.item_count).length === 0) {
          console.log('警告：processedData的item_count记录为空')
          // 指的是当前日期下，没有对应的配置组数据。需要将配置组的筛选条件改为all，并且设置SelectedTask为all
          let {processedData, filteredData} = 
        analysistools.calculateItemTrend(itemData, durationData, selectedDate, 'all')
        setSelectedTask('all')
        setData(processedData)
        }
        else setData(processedData)

        // 根据当前日期，来刷新当前日期条件下配置组有哪些选项
        if (selectedDate != 'all') {
          let {processedData, filteredData} = 
        analysistools.calculateItemTrend(itemData, durationData, selectedDate, 'all')
          let task_list = [...new Set(filteredData.Task)]
          task_list.unshift('all')
          setTaskList(task_list)
        }
        else {
          // 全部日期情况下，配置组应当包含所有可能的配置组
          let task_list = [...new Set(itemData.Task)].filter(task => task !== '')
          console.log('task_list',task_list)
          task_list.unshift('all')
          setTaskList(task_list)
        }
        setError(null)
      } catch (error) {
        console.error('处理数据失败:', error)
        setError('处理数据失败，请稍后再试')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [selectedDate, selectedTask, itemData, durationData])



  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-white">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="text-xl flex flex-col items-center"
        >
          <motion.div
            className="w-16 h-16 border-4 border-t-transparent rounded-full mb-6"
            style={{ borderColor: `${colors.lightBorder} transparent ${colors.lightBorder} ${colors.lightBorder}` }}
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          />
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.5 }}
            style={{ color: colors.secondary }}
            className="font-medium"
          >
            正在加载和分析数据...
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.5 }}
            style={{ color: colors.primary }}
            className="text-sm mt-2"
          >
            请稍候片刻
          </motion.div>
        </motion.div>
      </div>
    )
  }

  if (error) {
    return (
      <ErrorPage
        type="error"
        message={error}
        showRefresh={true}
        onRefresh={() => window.location.reload()}
        colors={colors}
      />
    )
  }

  if (!data) {
    return (
      <ErrorPage
        type="noData"
        message="当前没有可显示的数据"
        colors={colors}
      />
    )
  }

  const categories = categorizeItems(data.item_count)
  const totalItems = getTotalItemCount(data.item_count)
  const uniqueItems = getUniqueItemCount(data.item_count)
  const duration = data.duration
  const top10Items = getTopItems(data.item_count)
  const categoryTotals = getCategoryTotals(categories)
  const pieChartData = generatePieChart(categoryTotals)

   // 新增：处理扇形区域悬停
  const handleSegmentHover = (index: number | null) => {
    setHoverIndex(index)
  }

  // 找出最大数量，用于计算条形图比例
  const maxCount = top10Items.length > 0 ? top10Items[0][1] : 0
  return (
    <div className="container mx-auto px-4 py-8 bg-white relative">
      {/* GitHub 图标 */}
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="fixed top-6 right-6 z-50"
      >
        <motion.a
          href="https://github.com/Because66666/CanLiang"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center w-12 h-12 rounded-full shadow-lg transition-all duration-300 hover:shadow-xl"
          style={{
            backgroundColor: colors.light,
            border: `2px solid ${colors.lightBorder}`,
          }}
          whileHover={{
            scale: 1.1,
            backgroundColor: colors.primary,
            borderColor: colors.primary,
          }}
          whileTap={{ scale: 0.95 }}
        >
          <motion.div
            whileHover={{
              color: "#ffffff",
            }}
            transition={{ duration: 0.2 }}
          >
            <Github className="h-6 w-6" style={{ color: colors.secondary }} />
          </motion.div>
        </motion.a>
      </motion.div>

      {/* 下载图标 */}
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="fixed top-20 right-6 z-50"
      >
        <DownloadDialog
          isOpen={downloadDialogOpen}
          onOpenChange={setDownloadDialogOpen}
          onDownload={handleDataDownload}
          loading={downloadLoading}
          colors={colors}
        />
      </motion.div>

      {/* 物品详情模态框 */}
      <ItemModal
        selectedItem={selectedItem}
        itemTrendData={itemTrendData}
        loadingTrend={loadingTrend}
        colors={colors}
        onClose={closeItemModal}
      />

      {/* 统计趋势模态框 */}
      <StatModal
        statModal={statModal}
        colors={colors}
        onClose={closeStatModal}
      />

      <div
        className="mb-8 text-3xl font-bold text-center flex items-center justify-center gap-3"
        style={{ color: colors.secondary }}
      >        
        <img 
          src="/canliang.png" 
          alt="参量质变仪图标" 
          className="w-10 h-10 object-cover rounded-lg"
        />
        参量质变仪（模拟数据）
      </div>

      {/* 统计卡片 */}
      <div
        className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-3"
      >
        <StatCard
          title="物品数量"
          value={totalItems.toString()}
          icon={Package}
          color={colors.primary}
          colors={colors}
          onClick={() => handleStatClick("totalItems")}
        />
        
        <StatCard
          title="运行时间"
          value={duration}
          icon={Clock}
          color={colors.primary}
          colors={colors}
          onClick={() => handleStatClick("duration")}
        />
        
        <StatCard
          title="最多物品"
          value={(() => {
            const sortedEntries = Object.entries(data.item_count).sort((a, b) => b[1] - a[1]);
            return sortedEntries.length > 0 ? sortedEntries[0][0] : "暂无数据";
          })()}
          icon={BarChart2}
          color={colors.primary}
          colors={colors}
        />
      </div>

      {/* 主要内容区域 - 分为左侧条形图和右侧物品列表 */}
      <div className="flex flex-col lg:flex-row gap-8">
        {/* 左侧图表 */}
        <div className="w-full lg:w-1/3 space-y-8">
          {/* 饼状图 */}
          <motion.div
              key={`pie-chart-${animationKey}`}
            >
              <Card className="border-0 shadow-sm overflow-hidden">
                <CardContent className="p-6">
                  <h2 className="text-xl font-bold mb-4" style={{ color: colors.secondary }}>
                    物品类别分布
                  </h2>
                  <div className="flex flex-col items-center">
                    <motion.div
                      className="relative w-[200px] h-[200px]"
                      initial={{ rotate: -90 }}
                      animate={{ rotate: 0}}
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
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.1 * index, duration: 0.5 }}
                            onMouseEnter={() => handleSegmentHover(index)}
                            onMouseLeave={() => handleSegmentHover(null)}
                            whileHover={{
                              scale: 1.15,
                              transformOrigin: "center",
                              transition: { type: "spring", stiffness: 300 },
                            }}
                          />
                        ))}
                      </svg>
                    </motion.div>
                    {/* 图例部分修改 */}
                    <div className="mt-6 grid grid-cols-2 gap-x-4 gap-y-3 w-full">
                      {pieChartData.map((segment, index) => (
                        <motion.div
                          key={index}
                          className="flex items-center"
                          style={{
                            backgroundColor: hoverIndex === index ? "#f0f4ff" : "transparent",
                            borderRadius: 6,
                            padding: "4px 8px",
                          }}
                          onMouseEnter={() => handleSegmentHover(index)}
                          onMouseLeave={() => handleSegmentHover(null)}
                          transition={{ duration: 0.2 }}
                        >
                          <div
                            className="w-4 h-4 mr-2 flex-shrink-0 rounded-sm"
                            style={{ backgroundColor: segment.color }}
                          ></div>
                          <div className="flex justify-between w-full">
                            <motion.span
                              className="text-sm font-medium"
                              animate={{
                                fontWeight: hoverIndex === index ? 700 : 500,
                                scale: hoverIndex === index ? 1.05 : 1,
                                color: hoverIndex === index ? colors.primary : colors.secondary,
                              }}
                              transition={{ duration: 0.2 }}
                            >
                              {segment.name}
                            </motion.span>
                            <motion.span
                              className="text-sm"
                              animate={{
                                scale: hoverIndex === index ? 1.1 : 1,
                                color: hoverIndex === index ? colors.primary : colors.secondary,
                              }}
                              transition={{ duration: 0.2 }}
                            >
                              {segment.percentage}%
                            </motion.span>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
          </motion.div>

          {/* 条形图 */}
          <motion.div
              key={`bar-chart-${animationKey}`}
            >
              <Card className="border-0 shadow-sm overflow-hidden">
                <CardContent className="p-6">
                  <h2 className="text-xl font-bold mb-4" style={{ color: colors.secondary }}>
                    物品数量排行（前十五）
                  </h2>
                  <div className="space-y-4">
                    {top10Items.slice(0, 15).map(([name, count], index) => (
                      <motion.div
                        key={index}
                        className="flex flex-col cursor-pointer"
                        animate={{ x: 0}}
                        transition={{ delay: index * 0.1, duration: 0.3 }}
                        onClick={() => handleItemClick(name)}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
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
        </div>

        {/* 右侧物品列表 */}
        <div className="w-full lg:w-2/3">
          {/* 搜索和日期选择区域 */}
          <motion.div
            className="mb-8 p-6 rounded-lg"
            style={{ backgroundColor: colors.light }}
          >
            {/* 响应式网格布局：小屏单列，中屏2x2，大屏单行 */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 items-center justify-items-center">
              {/* 搜索 */}
              <div className="flex flex-col items-center gap-2 w-full max-w-[200px]">
                <div className="flex items-center gap-2">
                  <Search className="h-4 w-4" style={{ color: colors.primary }} />
                  <span className="text-sm" style={{ color: colors.secondary }}>
                    搜索物品:
                  </span>
                </div>
                <div className="relative w-full">
                  <Input
                    placeholder="搜索物品..."
                    className="pl-4 py-3 border-0 shadow-sm focus:ring-2 w-full"
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
              <div className="flex flex-col items-center gap-2 w-full max-w-[200px]">
                <div className="flex items-center gap-2">
                    <CalendarIcon className="h-4 w-4" style={{ color: colors.primary }} />
                    <span className="text-sm" style={{ color: colors.secondary }}>
                      选择日期:
                    </span>
                  </div>
                  <Select value={selectedDate} onValueChange={handleDateChange}>
                    <SelectTrigger
                      className="w-full border-0 shadow-sm focus:ring-2"
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

              {/* 配置组选择 */}
              <div className="flex flex-col items-center gap-2 w-full max-w-[200px]">
                <div className="flex items-center gap-2">
                    <CalendarIcon className="h-4 w-4" style={{ color: colors.primary }} />
                    <span className="text-sm" style={{ color: colors.secondary }}>
                      选择配置组:
                    </span>
                  </div>
                  <Select value={selectedTask} onValueChange={handleTaskChange}>
                    <SelectTrigger
                      className="w-full border-0 shadow-sm focus:ring-2"
                      style={{
                        borderColor: colors.lightBorder,
                        boxShadow: `0 0 0 1px ${colors.lightBorder}`,
                      }}
                    >
                      <SelectValue placeholder="all" />
                    </SelectTrigger>
                    <SelectContent>
                      {taskList.map((task) => (
                        <SelectItem key={task} value={task}>
                          {task}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
              </div>

              {/* "全部"按钮 */}
              <div className="flex flex-col items-center gap-2 w-full max-w-[200px]">
                <div className="h-6"></div> {/* 占位符，保持对齐 */}
                <button
                  onClick={handleSelectAll}
                  className="px-4 py-3 rounded-md text-sm font-medium shadow-sm w-full"
                  style={{
                    backgroundColor: selectedDate === "all" ? colors.primary : "#fff",
                    color: selectedDate === "all" ? "#fff" : colors.secondary,
                    boxShadow: `0 0 0 1px ${colors.lightBorder}`,
                  }}
                >
                  全部
                </button>
              </div>
            </div>
          </motion.div>

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
              <TabsContent value="all">
                  <div
                    key={`all-items-${animationKey}`}
                    className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3"
                  >
                    {filterAndSortItems(data.item_count, searchTerm).map(([name, count], index) => (
                      <ItemCard
                        key={name}
                        name={name}
                        count={count}
                        color={getItemColor(name)}
                        onClick={() => handleItemClick(name)}
                      />
                    ))}
                  </div>
                </TabsContent>

                {Object.entries(categories).map(([category, items]) => (
                  <TabsContent key={category} value={category}>
                    <div
                      key={`${category}-items-${animationKey}`}
                      className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3"
                    >
                      {filterAndSortItems(items, searchTerm).map(([name, count], index) => (
                        <ItemCard
                          key={name}
                          name={name}
                          count={count}
                          color={categoryColors[category as keyof typeof categoryColors]}
                          onClick={() => handleItemClick(name)}
                        />
                      ))}
                    </div>
                  </TabsContent>
                ))}
            </div>
          </Tabs>
        </div>
      </div>
    </div>
  )
}



// TrendChart组件已移动到独立文件
