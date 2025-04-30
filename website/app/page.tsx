"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Search, BarChart2, CalendarIcon } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"


interface InventoryData {
  item_count: Record<string, number>
}

interface DateItem {
  value: string
  label: string
}

export default function InventoryPage() {
  const [dateList, setDateList] = useState<DateItem[]>([])
  const [selectedDate, setSelectedDate] = useState<string>("") 
  const [data, setData] = useState<InventoryData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [sortBy, setSortBy] = useState<"name" | "count">("name")

  // 从API获取日期列表
  useEffect(() => {
    const fetchDateList = async () => {
      try {
        setLoading(true)
        const response = await fetch('http://127.0.0.1:5000/api/LogList')
        
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
        const response = await fetch(`http://127.0.0.1:5000/api/analyse?date=${selectedDate}`)
        
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

  // 对物品进行分类
  const categorizeItems = (items: Record<string, number>) => {
    const categories: Record<string, Record<string, number>> = {
      冒险家系列: {},
      游医系列: {},
      幸运儿系列: {},
      矿物材料: {},
      食材: {},
      其他: {},
    }

    Object.entries(items).forEach(([name, count]) => {
      if (name.includes("冒险家")) {
        categories["冒险家系列"][name] = count
      } else if (name.includes("游医")) {
        categories["游医系列"][name] = count
      } else if (name.includes("幸运儿")) {
        categories["幸运儿系列"][name] = count
      } else if (["紫晶块", "白铁块", "铁块", "魔晶块"].includes(name)) {
        categories["矿物材料"][name] = count
      } else if (
        [
          "卷心菜",
          "甜甜花",
          "白萝",
          "白萝卜",
          "树莓",
          "日落果",
          "薄荷",
          "鸟蛋",
          "禽肉",
          "太阳蟹",
          "薄红蟹",
          "晴天鳅鳅",
        ].includes(name)
      ) {
        categories["食材"][name] = count
      } else {
        categories["其他"][name] = count
      }
    })

    return categories
  }

  // 过滤和排序物品
  const filterAndSortItems = (items: Record<string, number>) => {
    return Object.entries(items)
      .filter(([name]) => name.toLowerCase().includes(searchTerm.toLowerCase()))
      .sort((a, b) => {
        if (sortBy === "name") {
          return a[0].localeCompare(b[0])
        } else {
          return b[1] - a[1]
        }
      })
  }

  // 获取总物品数量
  const getTotalItemCount = (items: Record<string, number>) => {
    return Object.values(items).reduce((sum, count) => sum + count, 0)
  }

  // 获取物品种类数量
  const getUniqueItemCount = (items: Record<string, number>) => {
    return Object.keys(items).length
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-xl">加载中...</div>
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

  return (
    <div className="container mx-auto px-4 py-8 bg-white">
      <h1 className="mb-8 text-3xl font-bold text-center text-black">参量质变仪</h1>

      {/* 统计卡片 */}
      <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-3">
        <Card className="border border-gray-200 shadow-sm">
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm text-gray-500">总物品数量</p>
              <p className="text-3xl font-bold text-black">{totalItems}</p>
            </div>
            <BarChart2 className="h-8 w-8 text-gray-400" />
          </CardContent>
        </Card>
        <Card className="border border-gray-200 shadow-sm">
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm text-gray-500">物品种类</p>
              <p className="text-3xl font-bold text-black">{uniqueItems}</p>
            </div>
            <BarChart2 className="h-8 w-8 text-gray-400" />
          </CardContent>
        </Card>
        <Card className="border border-gray-200 shadow-sm">
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm text-gray-500">最多物品</p>
              <p className="text-3xl font-bold text-black">
                {Object.entries(data.item_count).sort((a, b) => b[1] - a[1])[0][0]}
              </p>
            </div>
            <BarChart2 className="h-8 w-8 text-gray-400" />
          </CardContent>
        </Card>
      </div>

      {/* 搜索和排序 */}
      <div className="mb-8 flex flex-col items-center gap-4">
        <div className="relative w-full max-w-md">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-gray-400" />
          <Input
            placeholder="搜索物品..."
            className="pl-8 border-gray-300 focus:border-black focus:ring-black"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="flex gap-2">
          <Button
            variant={sortBy === "name" ? "default" : "outline"}
            onClick={() => setSortBy("name")}
            className={
              sortBy === "name"
                ? "bg-black hover:bg-gray-800 text-white"
                : "text-black border-gray-300 hover:bg-gray-100"
            }
          >
            按名称排序
          </Button>
          <Button
            variant={sortBy === "count" ? "default" : "outline"}
            onClick={() => setSortBy("count")}
            className={
              sortBy === "count"
                ? "bg-black hover:bg-gray-800 text-white"
                : "text-black border-gray-300 hover:bg-gray-100"
            }
          >
            按数量排序
          </Button>
        </div>
      </div>

      {/* 日期选择 */}
      <div className="mb-8 flex flex-col items-center gap-4">
        <div className="flex items-center gap-2">
          <CalendarIcon className="h-4 w-4 text-gray-400" />
          <span className="text-sm text-gray-500">选择日期:</span>
        </div>
        <Select value={selectedDate} onValueChange={setSelectedDate}>
          <SelectTrigger className="w-[240px] border-gray-300 focus:border-black focus:ring-black">
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

      {/* 物品列表 */}
      <Tabs defaultValue="all" className="flex flex-col items-center">
        <TabsList className="mb-6 bg-gray-100 p-1 rounded-md">
          <TabsTrigger value="all" className="data-[state=active]:bg-white data-[state=active]:text-black">
            全部
          </TabsTrigger>
          {Object.keys(categories).map((category) => (
            <TabsTrigger
              key={category}
              value={category}
              className="data-[state=active]:bg-white data-[state=active]:text-black"
            >
              {category}
            </TabsTrigger>
          ))}
        </TabsList>

        <div className="w-full">
          <TabsContent value="all">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
              {filterAndSortItems(data.item_count).map(([name, count]) => (
                <ItemCard key={name} name={name} count={count} />
              ))}
            </div>
          </TabsContent>

          {Object.entries(categories).map(([category, items]) => (
            <TabsContent key={category} value={category}>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
                {filterAndSortItems(items).map(([name, count]) => (
                  <ItemCard key={name} name={name} count={count} />
                ))}
              </div>
            </TabsContent>
          ))}
        </div>
      </Tabs>
    </div>
  )
}

function ItemCard({ name, count }: { name: string; count: number }) {
  return (
    <Card className="border border-gray-200 hover:shadow-md transition-shadow duration-200">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div className="truncate font-medium text-black">{name}</div>
          <div className="ml-2 rounded-full bg-black px-2 py-1 text-xs font-semibold text-white">{count}</div>
        </div>
      </CardContent>
    </Card>
  )
}
