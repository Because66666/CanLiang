// 函数工具层 - 处理所有的统计分析的方法
import { InventoryData, DateItem, ItemTrendData, ItemDataDict, DurationDict } from '../types/inventory'
import * as XLSX from 'xlsx'

class AnalysisFunctions {
  // 将时间长度格式化为时间字符串
  formatDuration(totalDuration: number): string {
    const hours = Math.floor(totalDuration / 3600)
    const minutes = Math.floor((totalDuration % 3600) / 60)
    const formattedDuration = `${hours}小时${minutes}分钟`
    return formattedDuration
  }

  // 筛选指定日期和指定配置组的物品数据和时长数据
  // 返回的数据类型：
  /* 
  const processedData: InventoryData = {
      item_count: filteredItemCount,
      duration: formattedDuration
    }
  export interface ItemDataDict {
    ItemName: string[]
    Task:string[]
    TimeStamp: string[]
    Date: string[]
}
  */
  calculateItemTrend(itemData: ItemDataDict,
    durationData: DurationDict,
    selectedDate: string,
    selectedTask: string): { processedData: InventoryData; filteredData: ItemDataDict } {
    let filteredItemCount: Record<string, number> = {}
    let totalDuration = 0

    // 创建临时的ItemDataDict存储筛选数据
    let tempItemData: ItemDataDict = {
      ItemName: [],
      Task: [],
      TimeStamp: [],
      Date: []
    }

    // 第一步：用selectedDate筛选数据
    if (selectedDate === 'all') {
      // 如果是'all'，复制所有数据
      tempItemData = {
        ItemName: [...itemData.ItemName],
        Task: [...itemData.Task],
        TimeStamp: [...itemData.TimeStamp],
        Date: [...itemData.Date]
      }
    } else {
      // 筛选指定日期的数据
      itemData.Date.forEach((date, index) => {
        if (date === selectedDate) {
          tempItemData.ItemName.push(itemData.ItemName[index])
          tempItemData.Task.push(itemData.Task[index])
          tempItemData.TimeStamp.push(itemData.TimeStamp[index])
          tempItemData.Date.push(itemData.Date[index])
        }
      })
    }

    // 第二步：用selectedTask筛选数据
    let finalItemData: ItemDataDict = {
      ItemName: [],
      Task: [],
      TimeStamp: [],
      Date: []
    }

    if (selectedTask === 'all') {
      // 如果是'all'，使用第一步筛选的所有数据
      finalItemData = tempItemData
    } else {
      // 筛选指定任务的数据
      tempItemData.Task.forEach((taskName, index) => {
        if (taskName === selectedTask) {
          finalItemData.ItemName.push(tempItemData.ItemName[index])
          finalItemData.Task.push(tempItemData.Task[index])
          finalItemData.TimeStamp.push(tempItemData.TimeStamp[index])
          finalItemData.Date.push(tempItemData.Date[index])
        }
      })
    }
    // console.log('finalItemData',finalItemData)
    // 统计物品数量
    finalItemData.ItemName.forEach((itemName) => {
      filteredItemCount[itemName] = (filteredItemCount[itemName] || 0) + 1
    })

    // 计算duration
    if (selectedTask === 'all') {
      // selectedTask为all，按照原有方式计算
      if (selectedDate === 'all') {
        totalDuration = durationData.Duration.reduce((sum, duration) => sum + duration, 0)
      } else {
        durationData.Date.forEach((date, index) => {
          if (date === selectedDate) {
            totalDuration += durationData.Duration[index]
          }
        })
      }
    } else {
      // selectedTask不为all，计算时间差
      if (finalItemData.TimeStamp.length > 0) {
        // 按日期聚类每天的timestamp
        const dailyTimeRanges: { [key: string]: { min: number, max: number } } = {}
        
        finalItemData.TimeStamp.forEach((timeStr, index) => {
          const date = finalItemData.Date[index]
          
          // 解析时间字符串为秒数
          const [hours, minutes, seconds] = timeStr.split(':')
          const [sec, ms] = seconds.split('.')
          const timeInSeconds = parseInt(hours) * 3600 + parseInt(minutes) * 60 + parseInt(sec)
          
          // 初始化日期的数据结构
          if (!dailyTimeRanges[date]) {
            dailyTimeRanges[date] = { min: timeInSeconds, max: timeInSeconds }
          }
          
          // 更新最小值和最大值
          dailyTimeRanges[date].min = Math.min(dailyTimeRanges[date].min, timeInSeconds)
          dailyTimeRanges[date].max = Math.max(dailyTimeRanges[date].max, timeInSeconds)
        })
        
        // 分别计算每天的duration，然后累加得到totalDuration
        totalDuration = 0
        Object.values(dailyTimeRanges).forEach(timeRange => {
          const dailyDuration = timeRange.max - timeRange.min
          totalDuration += dailyDuration
        })
      }
    }

    // 格式化时长为"x小时y分钟"
    const formattedDuration = this.formatDuration(totalDuration)

    const processedData: InventoryData = {
      item_count: filteredItemCount,
      duration: formattedDuration
    }
    // console.log('filteredData', finalItemData)
    // console.log('processedData', processedData)
    return { processedData, filteredData: finalItemData }
  }

  // 计算趋势数据
  calculateTrendData(type: string,
    itemData: ItemDataDict,
    durationData: DurationDict,
    selectedTask: string): ItemTrendData {
    const trendData: ItemTrendData = {}

    if (type === 'totalItems') {
      // 从itemData中按日期聚合物品数量
      if (selectedTask == 'all') {
        itemData.Date.forEach((date, index) => {
          if (trendData[date]) {
            trendData[date] += 1
          } else {
            trendData[date] = 1
          }
        })
      }
      else {
        // 筛选selectedTask下的物品数量
        itemData.Date.forEach((date, index) => {
          if (itemData.Task[index] === selectedTask) {
            if (trendData[date]) {
              trendData[date] += 1
            } else {
              trendData[date] = 1
            }
          }
        })
      }
    } else if (type === 'duration') {
      // 从durationData中按日期聚合时长
      if (selectedTask == 'all') {
        durationData.Date.forEach((date, index) => {
          const duration = durationData.Duration[index]
          if (trendData[date]) {
            trendData[date] += duration
          } else {
            trendData[date] = duration
          }
        })
      }
      else {
        // 筛选selectedTask下的时长
        const taskTimeRanges: { [key: string]: { min: number, max: number } } = {}

        // 第一步：只收集指定selectedTask的时间范围
        itemData.Date.forEach((date, index) => {
          const task = itemData.Task[index]
          
          // 只处理selectedTask的数据
          if (task === selectedTask) {
            const timeStr = itemData.TimeStamp[index]

            // 解析时间字符串为秒数
            const [hours, minutes, seconds] = timeStr.split(':')
            const [sec, ms] = seconds.split('.')
            const timeInSeconds = parseInt(hours) * 3600 + parseInt(minutes) * 60 + parseInt(sec)

            // 初始化日期的数据结构
            if (!taskTimeRanges[date]) {
              taskTimeRanges[date] = { min: timeInSeconds, max: timeInSeconds }
            }

            // 更新最小值和最大值
            taskTimeRanges[date].min = Math.min(taskTimeRanges[date].min, timeInSeconds)
            taskTimeRanges[date].max = Math.max(taskTimeRanges[date].max, timeInSeconds)
          }
        })

        // 第二步：计算每天指定任务的时长
        Object.entries(taskTimeRanges).forEach(([date, timeRange]) => {
          trendData[date] = timeRange.max - timeRange.min
        })
        
      }
    }

    return trendData
  }
  calculateAnItemTrend(itemName: string, itemData: ItemDataDict, selectedTask: string): ItemTrendData {
    const trendData: ItemTrendData = {}
    if (selectedTask !== 'all') {
      itemData.Date.forEach((date, index) => {
        if (itemData.ItemName[index] === itemName && itemData.Task[index] === selectedTask) {
          trendData[date] = (trendData[date] || 0) + 1
        }
      })
    }
    else {
      itemData.Date.forEach((date, index) => {
        if (itemData.ItemName[index] === itemName) {
          trendData[date] = (trendData[date] || 0) + 1
        }
      })
    }

    return trendData
  }
  saveAllData(type: string, itemData: ItemDataDict, durationData: DurationDict) {
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')

    switch (type) {
      case 'csv':
        this.downloadCSV(itemData, durationData, timestamp)
        break
      case 'excel':
        this.downloadExcel(itemData, durationData, timestamp)
        break
      case 'html':
        this.downloadHTML(itemData, durationData, timestamp)
        break
      case 'json':
        this.downloadJSON(itemData, durationData, timestamp)
        break
      case 'xml':
        this.downloadXML(itemData, durationData, timestamp)
        break
      default:
        console.error('不支持的文件格式:', type)
    }
  }

  private downloadCSV(itemData: ItemDataDict, durationData: DurationDict, timestamp: string) {
    // 物品数据CSV
    const itemCSV = [
      'ItemName,Task,TimeStamp,Date',
      ...itemData.ItemName.map((name, index) =>
        `"${name}",${itemData.Task[index]},${itemData.TimeStamp[index]},${itemData.Date[index]}`
      )
    ].join('\n')

    // 时长数据CSV
    const durationCSV = [
      'Date,Duration',
      ...durationData.Date.map((date, index) =>
        `${date},${itemData.Task[index]},${durationData.Duration[index]}`
      )
    ].join('\n')

    this.downloadFile(itemCSV, `物品数据_${timestamp}.csv`, 'text/csv')
    this.downloadFile(durationCSV, `时长数据_${timestamp}.csv`, 'text/csv')
  }

  private downloadJSON(itemData: ItemDataDict, durationData: DurationDict, timestamp: string) {
    const data = {
      itemData,
      durationData,
      exportTime: new Date().toISOString()
    }

    const jsonString = JSON.stringify(data, null, 2)
    this.downloadFile(jsonString, `数据导出_${timestamp}.json`, 'application/json')
  }

  private downloadHTML(itemData: ItemDataDict, durationData: DurationDict, timestamp: string) {
    const html = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>数据导出报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        h2 { color: #333; }
    </style>
</head>
<body>
    <h1>数据导出报告</h1>
    <p>导出时间: ${new Date().toLocaleString('zh-CN')}</p>
    
    <h2>物品数据</h2>
    <table>
        <thead>
            <tr><th>物品名称</th><th>时间戳</th><th>日期</th></tr>
        </thead>
        <tbody>
            ${itemData.ItemName.map((name, index) =>
      `<tr><td>${name}</td><td>${itemData.Task[index]}</td><td>${itemData.TimeStamp[index]}</td><td>${itemData.Date[index]}</td></tr>`
    ).join('')}
        </tbody>
    </table>
    
    <h2>时长数据</h2>
    <table>
        <thead>
            <tr><th>日期</th><th>时长(秒)</th></tr>
        </thead>
        <tbody>
            ${durationData.Date.map((date, index) =>
      `<tr><td>${date}</td><td>${durationData.Duration[index]}</td></tr>`
    ).join('')}
        </tbody>
    </table>
</body>
</html>`

    this.downloadFile(html, `数据报告_${timestamp}.html`, 'text/html')
  }

  private downloadXML(itemData: ItemDataDict, durationData: DurationDict, timestamp: string) {
    const xml = `<?xml version="1.0" encoding="UTF-8"?>
<DataExport>
    <ExportInfo>
        <Timestamp>${new Date().toISOString()}</Timestamp>
    </ExportInfo>
    <ItemData>
        ${itemData.ItemName.map((name, index) =>
      `<Item>
            <Name>${this.escapeXML(name)}</Name>
            <TimeStamp>${itemData.TimeStamp[index]}</TimeStamp>
            <Date>${itemData.Date[index]}</Date>
        </Item>`
    ).join('\n        ')}
    </ItemData>
    <TaskData>
        ${itemData.Task.map((task, index) =>
      `<Task>
            <Name>${this.escapeXML(task)}</Name>
        </Task>`
    ).join('\n        ')}
    </TaskData>
    <DurationData>
        ${durationData.Date.map((date, index) =>
      `<Duration>
            <Date>${date}</Date>
            <Seconds>${durationData.Duration[index]}</Seconds>
        </Duration>`
    ).join('\n        ')}
    </DurationData>
</DataExport>`

    this.downloadFile(xml, `数据导出_${timestamp}.xml`, 'application/xml')
  }

  private downloadExcel(itemData: ItemDataDict, durationData: DurationDict, timestamp: string) {
    // 使用xlsx库生成真正的Excel文件

    // 创建工作簿
    const workbook = XLSX.utils.book_new()

    // 准备物品数据
    const itemSheetData = [
      ['物品名称', '归属配置组', '时间戳', '日期'],
      ...itemData.ItemName.map((name, index) => [
        name,
        itemData.Task[index],
        itemData.TimeStamp[index],
        itemData.Date[index]
      ])
    ]

    // 准备时长数据
    const durationSheetData = [
      ['日期', '时长(秒)'],
      ...durationData.Date.map((date, index) => [
        date,
        durationData.Duration[index]
      ])
    ]

    // 创建工作表
    const itemSheet = XLSX.utils.aoa_to_sheet(itemSheetData)
    const durationSheet = XLSX.utils.aoa_to_sheet(durationSheetData)

    // 添加工作表到工作簿
    XLSX.utils.book_append_sheet(workbook, itemSheet, '物品数据')
    XLSX.utils.book_append_sheet(workbook, durationSheet, '时长数据')

    // 生成Excel文件的二进制数据
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })

    // 创建Blob并下载
    const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `数据报告_${timestamp}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  private downloadFile(content: string, filename: string, mimeType: string) {
    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  private escapeXML(str: string): string {
    return str.replace(/[<>&"']/g, (match) => {
      switch (match) {
        case '<': return '&lt;'
        case '>': return '&gt;'
        case '&': return '&amp;'
        case '"': return '&quot;'
        case "'": return '&apos;'
        default: return match
      }
    })
  }
}
// 导出API服务实例
export const analysistools = new AnalysisFunctions()

// 导出默认实例
export default analysistools