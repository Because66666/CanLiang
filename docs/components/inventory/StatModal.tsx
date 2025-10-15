import { motion } from "framer-motion"
import { X } from "lucide-react"
import { TrendChart } from "./TrendChart"
import { StatModalData, ColorScheme } from "@/types/inventory"

interface StatModalProps {
  statModal: StatModalData | null
  colors: ColorScheme
  onClose: () => void
}

/**
 * 统计趋势模态框组件
 */
export function StatModal({ statModal, colors, onClose }: StatModalProps) {
  if (!statModal) return null

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.8, opacity: 0 }}
        transition={{ type: "spring", stiffness: 200, damping: 20 }}
        className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold" style={{ color: colors.secondary }}>
            {statModal.title}
          </h2>
          <button 
            onClick={onClose} 
            className="p-2 rounded-full hover:bg-gray-100 transition-colors"
          >
            <X className="h-6 w-6" style={{ color: colors.secondary }} />
          </button>
        </div>

        {statModal.loading ? (
          <div className="flex items-center justify-center h-64">
            <div
              className="w-8 h-8 border-4 border-t-transparent rounded-full animate-spin"
              style={{ borderColor: colors.primary, borderTopColor: "transparent" }}
            ></div>
          </div>
        ) : statModal.data ? (
          <TrendChart 
            data={statModal.data} 
            title={statModal.title} 
            colors={colors} 
            type={statModal.type as "totalItems" | "duration" | "item"} 
          />
        ) : (
          <div className="text-center text-gray-500 h-64 flex items-center justify-center">
            暂无趋势数据
          </div>
        )}
      </motion.div>
    </motion.div>
  )
}

export default StatModal