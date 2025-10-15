import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"
import { Download } from "lucide-react"
import { DownloadDialogProps, ColorScheme } from "@/types/inventory"

interface DownloadDialogComponentProps extends DownloadDialogProps {
  colors: ColorScheme
}

/**
 * 下载对话框组件
 */
export function DownloadDialog({ 
  isOpen, 
  onOpenChange, 
  onDownload, 
  loading, 
  colors 
}: DownloadDialogComponentProps) {
  return (
    <>
      <motion.button
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
        onClick={() => onOpenChange(true)}
      >
        <motion.div
          whileHover={{
            color: "#ffffff",
          }}
          transition={{ duration: 0.2 }}
        >
          <Download className="h-6 w-6" style={{ color: colors.secondary }} />
        </motion.div>
      </motion.button>
      
      <Dialog open={isOpen} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>选择数据导出格式</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-2 gap-3 py-4">
            {['csv', 'excel', 'json', 'html', 'xml'].map((type) => (
              <Button
                key={type}
                variant="outline"
                onClick={() => onDownload(type)}
                disabled={loading}
                className="h-12 text-sm transition-all duration-200 hover:scale-105"
                style={{
                  borderColor: colors.lightBorder,
                  color: colors.secondary,
                }}
              >
                {loading ? (
                  <div className="w-4 h-4 border-2 border-t-transparent rounded-full animate-spin" />
                ) : (
                  type.toUpperCase()
                )}
              </Button>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}

export default DownloadDialog