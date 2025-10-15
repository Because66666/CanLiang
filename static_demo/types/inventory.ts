// 库存系统类型定义

/**
 * 库存数据接口
 */
export interface InventoryData {
  item_count: Record<string, number>
  duration: string
}
/**
 * 物品数据接口获得的数据结构，/api/LogData
 */
export interface ItemDataDict {
  ItemName: string[]
  Task:string[]
  TimeStamp: string[]
  Date: string[]
}
export interface DurationDict {
  Date: string[]
  Duration: number[]
}

/**
 * 日期项接口,api/LogList
 */
export interface DateItem {
  value: string
  label: string
}

/**
 * 分类总计接口
 */
export interface CategoryTotal {
  name: string
  count: number
  color: string
}

/**
 * 物品趋势数据接口
 */
export interface ItemTrendData {
  [date: string]: number
}

/**
 * 统计模态框数据接口
 */
export interface StatModalData {
  type: "totalItems" | "duration" | "item"
  title: string
  data: ItemTrendData | null
  loading: boolean
}

/**
 * 饼图片段接口
 */
export interface PieChartSegment {
  path?: string
  color: string
  name: string
  count: number
  percentage: string
  isFullCircle?: boolean
}

/**
 * 趋势图表属性接口
 */
export interface TrendChartProps {
  data: ItemTrendData
  title: string
  colors: ColorScheme
  type: "totalItems" | "duration" | "item"
}

/**
 * 物品卡片属性接口
 */
export interface ItemCardProps {
  name: string
  count: number
  color: string
  onClick: () => void
}

/**
 * 颜色方案接口
 */
export interface ColorScheme {
  primary: string
  secondary: string
  accent1: string
  accent2: string
  light: string
  lightBorder: string
  lightGray: string
  mediumGray: string
  darkText: string
}

/**
 * 分类颜色映射接口
 */
export interface CategoryColors {
  圣遗物: string
  矿物: string
  食材: string
  其他: string
}

/**
 * 统计卡片属性接口
 */
export interface StatCardProps {
  title: string
  value: string | number
  icon: React.ComponentType<any>
  color: string
  onClick?: () => void
}

/**
 * 模态框属性接口
 */
export interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
}

/**
 * 下载对话框属性接口
 */
export interface DownloadDialogProps {
  isOpen: boolean
  onOpenChange: (open: boolean) => void
  onDownload: (type: string) => Promise<void>
  loading: boolean
}

/**
 * 搜索栏属性接口
 */
export interface SearchBarProps {
  searchTerm: string
  onSearchChange: (term: string) => void
  placeholder?: string
}

/**
 * 日期选择器属性接口
 */
export interface DateSelectorProps {
  dateList: DateItem[]
  selectedDate: string
  onDateChange: (date: string) => void
  loading?: boolean
}

/**
 * 物品列表属性接口
 */
export interface ItemListProps {
  items: [string, number][]
  onItemClick: (itemName: string) => void
  maxCount: number
}

/**
 * 分类图表属性接口
 */
export interface CategoryChartProps {
  categoryTotals: CategoryTotal[]
  pieChartData: PieChartSegment[]
  hoverIndex: number | null
  onSegmentHover: (index: number | null) => void
}

/**
 * 页面状态接口
 */
export interface PageState {
  dateList: DateItem[]
  selectedDate: string
  data: InventoryData | null
  loading: boolean
  error: string | null
  searchTerm: string
  isChangingDate: boolean
  animationKey: number
  hoverIndex: number | null
  selectedItem: string | null
  itemTrendData: ItemTrendData | null
  loadingTrend: boolean
  statModal: StatModalData | null
  downloadDialogOpen: boolean
  downloadLoading: boolean
}

/**
 * API响应基础接口
 */
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

/**
 * 日期列表API响应接口
 */
export interface DateListResponse {
  list: string[]
}

/**
 * 趋势数据API响应接口
 */
export interface TrendDataResponse {
  data: ItemTrendData
}

/**
 * 下载数据API响应接口
 */
export interface DownloadDataResponse {
  [key: string]: string
}

/**
 * Webhook数据项接口
 */
export interface WebhookDataItem {
  id: number
  event: string
  result?: string
  timestamp?: string
  screenshot?: string | null
  create_time: string
  message?: string
}

/**
 * Webhook数据响应接口
 */
export interface WebhookDataResponse {
  success: boolean
  data: WebhookDataItem[]
  count: number
  message?: string
}


/**
 * 程序列表响应接口
 */
export interface ProgramListResponse {
  success: boolean
  data: string[]
  count: number
  message?: string
}

/**
 * 视频流配置接口
 */
export interface VideoStreamConfig {
  app: string  // 目标应用程序名称，如 'yuanshen.exe'
}

/**
 * 视频流错误响应接口
 */
export interface VideoStreamErrorResponse {
  error: string
  message: string
  provided?: string
  example?: string
}