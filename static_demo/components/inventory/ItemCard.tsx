import { motion } from "framer-motion"
import { Card, CardContent } from "@/components/ui/card"
import { ItemCardProps } from "@/types/inventory"

/**
 * 物品卡片组件
 */
export function ItemCard({ name, count, color, onClick }: ItemCardProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      <Card
        className="border border-gray-100 hover:shadow-md transition-shadow duration-200 cursor-pointer"
        onClick={onClick}
      >
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
    </motion.div>
  )
}

export default ItemCard