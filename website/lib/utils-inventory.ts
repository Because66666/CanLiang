// 库存数据处理工具函数

export interface CategoryTotal {
  name: string
  count: number
  color: string
}

export interface PieChartSegment {
  path?: string
  color: string
  name: string
  count: number
  percentage: string
  isFullCircle?: boolean
}

// 定义类别颜色
export const categoryColors = {
  圣遗物: "#34495e", // 深蓝
  矿物: "#4CAF50", // 绿色
  食材: "#f39c12", // 橙色
  其他: "#bdc3c7", // 浅灰
}

// 定义排行榜颜色
export const rankingColors = [
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

// 定义颜色方案
export const colors = {
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

/**
 * 物品分类逻辑
 * @param name 物品名称
 * @returns 物品类别
 */
export const getCategory = (name: string): string => {
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

/**
 * 对物品进行分类
 * @param items 物品数据
 * @returns 分类后的物品数据
 */
export const categorizeItems = (items: Record<string, number>): Record<string, Record<string, number>> => {
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

/**
 * 计算每个分类的总数量
 * @param categories 分类数据
 * @returns 分类总数数组
 */
export const getCategoryTotals = (categories: Record<string, Record<string, number>>): CategoryTotal[] => {
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

/**
 * 获取前N名物品
 * @param items 物品数据
 * @param limit 限制数量，默认15
 * @returns 排序后的物品数组
 */
export const getTopItems = (items: Record<string, number>, limit: number = 15): [string, number][] => {
  return Object.entries(items)
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
}

/**
 * 过滤和排序物品
 * @param items 物品数据
 * @param searchTerm 搜索关键词
 * @returns 过滤排序后的物品数组
 */
export const filterAndSortItems = (items: Record<string, number>, searchTerm: string): [string, number][] => {
  return Object.entries(items)
    .filter(([name]) => name.toLowerCase().includes(searchTerm.toLowerCase()))
    .sort((a, b) => b[1] - a[1])
}

/**
 * 获取总物品数量
 * @param items 物品数据
 * @returns 总数量
 */
export const getTotalItemCount = (items: Record<string, number>): number => {
  return Object.values(items).reduce((sum, count) => sum + count, 0)
}

/**
 * 获取物品种类数量
 * @param items 物品数据
 * @returns 种类数量
 */
export const getUniqueItemCount = (items: Record<string, number>): number => {
  return Object.keys(items).length
}

/**
 * 生成饼图数据
 * @param data 分类总数数据
 * @returns 饼图片段数组
 */
export const generatePieChart = (data: CategoryTotal[]): PieChartSegment[] => {
  const total = data.reduce((sum, item) => sum + item.count, 0)

  // 检查是否只有一个非 0 数据项
  const nonZeroItems = data.filter(item => item.count > 0)
  if (nonZeroItems.length === 1) {
    const item = nonZeroItems[0]
    return [{
      isFullCircle: true,
      color: item.color,
      name: item.name,
      count: item.count,
      percentage: '100.0',
      path: "", // 添加空路径属性以满足类型要求
    }]
  }

  let currentAngle = 0

  return data.map((item) => {
    const percentage = item.count / total
    const startAngle = currentAngle
    const endAngle = currentAngle + percentage * 2 * Math.PI

    const x1 = 100 + 80 * Math.cos(startAngle)
    const y1 = 100 + 80 * Math.sin(startAngle)
    const x2 = 100 + 80 * Math.cos(endAngle)
    const y2 = 100 + 80 * Math.sin(endAngle)

    const largeArcFlag = percentage > 0.5 ? 1 : 0

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

/**
 * 获取物品颜色
 * @param name 物品名称
 * @returns 颜色值
 */
export const getItemColor = (name: string): string => {
  let category = getCategory(name)
  return categoryColors[category as keyof typeof categoryColors]
}