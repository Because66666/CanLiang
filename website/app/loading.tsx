"use client"

import { motion } from "framer-motion"

export default function Loading() {
  return (
    <div className="flex h-screen items-center justify-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="text-xl flex flex-col items-center"
      >
        <div className="w-12 h-12 border-4 border-t-transparent border-primary rounded-full animate-spin mb-4"></div>
        <div>正在加载和分析数据...</div>
      </motion.div>
    </div>
  )
}
