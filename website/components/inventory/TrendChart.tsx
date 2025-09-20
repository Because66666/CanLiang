import { motion } from "framer-motion"
import { Package, Clock, TrendingUp } from "lucide-react"
import { TrendChartProps } from "@/types/inventory"
import { max } from "date-fns"

/**
 * 趋势图表组件
 */
export function TrendChart({ data, title, colors, type }: TrendChartProps) {
  // console.log('data',data)
  const sortedData = Object.entries(data).sort(([a], [b]) => a.localeCompare(b))
  const maxValue = Math.max(...Object.values(data))
  const minValue = Math.min(...Object.values(data))

  const chartWidth = 600
  const chartHeight = 300
  const padding = 60
  const innerWidth = chartWidth - 2 * padding
  const innerHeight = chartHeight - 2 * padding

  // 格式化数值显示
  const formatValue = (value: number) => {
    // console.log('formatValue', value)
    if (type === "duration") {
      // 将秒数转换为时间格式
      const hours = Math.floor(value / 3600)
      const minutes = Math.floor((value % 3600) / 60)
      return hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`
    }
    return value.toString()
  }

  // 计算点的位置
  const points = sortedData.map(([date, value], index) => {
    const x = padding + (index / (sortedData.length - 1)) * innerWidth
    const y = padding + ((maxValue - value) / (maxValue - minValue || 1)) * innerHeight
    return { x, y, date, value }
  })

  // 生成路径字符串
  const pathData = points.reduce((path, point, index) => {
    const command = index === 0 ? "M" : "L"
    return `${path} ${command} ${point.x} ${point.y}`
  }, "")

  // 生成渐变区域路径
  const areaPath = `${pathData} L ${points[points.length - 1].x} ${padding + innerHeight} L ${padding} ${padding + innerHeight} Z`

  // 获取图标
  const getIcon = () => {
    switch (type) {
      case "totalItems":
        return <Package className="h-5 w-5" style={{ color: colors.primary }} />
      case "duration":
        return <Clock className="h-5 w-5" style={{ color: colors.primary }} />
      default:
        return <TrendingUp className="h-5 w-5" style={{ color: colors.primary }} />
    }
  }

  // 计算Y轴坐标和标签（去重）
  const yAxisLabels = (() => {
    // 第一步：根据ratios计算所有value值
    const ratios = [0, 0.25, 0.5, 0.75, 1]
    const values: number[] = []
    
    ratios.forEach((ratio) => {
      const value = Math.round(minValue + (maxValue - minValue) * (1-ratio))
      values.push(value)
    })
    
    // 第二步：生成标签并去重
    const uniqueLabels = new Map<string, number>() // key为标签，value为对应的数值
    
    values.forEach((value) => {
      let label: string
      if (type === "duration") {
        const hours = Math.floor(value / 3600)
        const totalMinutes = Math.floor(value / 60)
        if (maxValue >= 3600) {
          // 超过1小时，显示整数小时
          label = `${hours}h`
        } else {
          // 1小时内，显示整十分钟
          if (totalMinutes>10){
          const tenMinutes = Math.floor(totalMinutes / 10) * 10
          label = `${tenMinutes}m`
        }
        // 10分钟内，显示10m
        else if (60<=value && value<600){
          label = '10m'
          }
        // 1分钟内，显示1m
        else label = '1m'
        }
      } else {
        label = value.toString()
      }
      
      // 只保留第一个出现的标签
      if (!uniqueLabels.has(label)) {
        uniqueLabels.set(label, value)
      }
    })
    
    // 第三步：根据去重后的标签数量均匀分配y值
    const result: { y: number; label: string }[] = []
    const labelsArray = Array.from(uniqueLabels.entries())
    const step = innerHeight / (labelsArray.length - 1 || 1)
    
    labelsArray.forEach(([label, value], index) => {
      const y = padding + index * step
      result.push({ y, label })
    })
    
    // console.log('Y轴标签结果:', result)
    return result
  })()

  return (
    <div className="w-full">
      <div className="mb-4 flex items-center gap-2">
        {getIcon()}
        <span className="font-medium" style={{ color: colors.secondary }}>
          {type === "totalItems" ? "总物品数量变化趋势" : type === "duration" ? "运行时间变化趋势" : "数量变化趋势"}
        </span>
      </div>

      <div className="bg-gray-50 rounded-lg p-4">
        <svg width="100%" height="300" viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="overflow-visible">
          {/* 网格线 */}
          <defs>
            <pattern id="grid" width="40" height="30" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 30" fill="none" stroke="#e5e5e5" strokeWidth="1" />
            </pattern>
            <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={colors.primary} stopOpacity="0.3" />
              <stop offset="100%" stopColor={colors.primary} stopOpacity="0.05" />
            </linearGradient>
          </defs>

          <rect x={padding} y={padding} width={innerWidth} height={innerHeight} fill="url(#grid)" />

          {/* Y轴标签 */}
          {yAxisLabels.map((item, index) => (
            <g key={index}>
              <line x1={padding - 5} y1={item.y} x2={padding} y2={item.y} stroke="#666" strokeWidth="1" />
              <text x={padding - 10} y={item.y + 4} textAnchor="end" fontSize="12" fill="#666">
                {item.label}
              </text>
            </g>
          ))}

          {/* 渐变区域 */}
          <path d={areaPath} fill="url(#areaGradient)" />

          {/* 折线 */}
          <motion.path
            d={pathData}
            fill="none"
            stroke={colors.primary}
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1.5, ease: "easeInOut" }}
          />

          {/* 数据点 */}
          {points.map((point, index) => (
            <motion.g key={index}>
              <motion.circle
                cx={point.x}
                cy={point.y}
                r="4"
                fill="white"
                stroke={colors.primary}
                strokeWidth="3"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: index * 0.1 + 0.5, duration: 0.3 }}
                whileHover={{ scale: 1.5 }}
              />

              {/* X轴标签 */}
              <text
                x={point.x}
                y={padding + innerHeight + 20}
                textAnchor="middle"
                fontSize="11"
                fill="#666"
                transform={`rotate(-45, ${point.x}, ${padding + innerHeight + 20})`}
              >
                {point.date.slice(4)} {/* 只显示月-日 */}
              </text>

              {/* 悬停提示 */}
              <motion.g opacity={0} whileHover={{ opacity: 1 }} transition={{ duration: 0.2 }}>
                <rect x={point.x - 35} y={point.y - 35} width="70" height="25" fill="rgba(0,0,0,0.8)" rx="4" />
                <text x={point.x} y={point.y - 18} textAnchor="middle" fontSize="12" fill="white">
                  {formatValue(point.value)}
                </text>
              </motion.g>
            </motion.g>
          ))}

          {/* 坐标轴 */}
          <line x1={padding} y1={padding} x2={padding} y2={padding + innerHeight} stroke="#333" strokeWidth="2" />
          <line
            x1={padding}
            y1={padding + innerHeight}
            x2={padding + innerWidth}
            y2={padding + innerHeight}
            stroke="#333"
            strokeWidth="2"
          />
        </svg>
      </div>

      {/* 统计信息 */}
      <div className="mt-4 grid grid-cols-3 gap-4 text-center">
        <div className="p-3 rounded-lg" style={{ backgroundColor: colors.light }}>
          <div className="text-sm" style={{ color: colors.secondary }}>
            最大值
          </div>
          <div className="text-xl font-bold" style={{ color: colors.darkText }}>
            {formatValue(maxValue)}
          </div>
        </div>
        <div className="p-3 rounded-lg" style={{ backgroundColor: colors.light }}>
          <div className="text-sm" style={{ color: colors.secondary }}>
            最小值
          </div>
          <div className="text-xl font-bold" style={{ color: colors.darkText }}>
            {formatValue(minValue)}
          </div>
        </div>
        <div className="p-3 rounded-lg" style={{ backgroundColor: colors.light }}>
          <div className="text-sm" style={{ color: colors.secondary }}>
            平均值
          </div>
          <div className="text-xl font-bold" style={{ color: colors.darkText }}>
            {formatValue(Math.round(Object.values(data).reduce((a, b) => a + b, 0) / Object.values(data).length))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default TrendChart