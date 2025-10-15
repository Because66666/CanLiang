import { motion } from "framer-motion"
import { StatCardProps, ColorScheme } from "@/types/inventory"

interface StatCardComponentProps extends StatCardProps {
  colors: ColorScheme
}

/**
 * 统计卡片组件
 */
export function StatCard({ title, value, icon: Icon, color, onClick, colors }: StatCardComponentProps) {
  return (
    <div>
      <motion.div
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        transition={{ type: "spring", stiffness: 300, damping: 20 }}
      >
        <Card
          className="border-0 shadow-sm overflow-hidden cursor-pointer hover:shadow-md transition-shadow duration-200"
          style={{ backgroundColor: colors.light }}
          onClick={onClick}
        >
          <CardContent className="flex items-center justify-between p-6">
            <div>
              <p className="text-sm" style={{ color: colors.secondary }}>
                {title}
              </p>
              <p className="text-3xl font-bold" style={{ color: colors.darkText }}>
                {value}
              </p>
            </div>
            <Icon className="h-8 w-8" style={{ color: colors.primary }} />
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

// 导入必要的组件
import { Card, CardContent } from "@/components/ui/card"

export default StatCard