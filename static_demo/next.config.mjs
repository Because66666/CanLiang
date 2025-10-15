/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  distDir: 'output',
  output: 'export',
  basePath: '/CanLiang', // GitHub Pages 子路径
  assetPrefix: '/CanLiang/', // GitHub Pages 静态资源前缀，注意末尾的斜杠
  trailingSlash: true, // 确保URL以斜杠结尾
  
  // 忽略node_modules和某些目录的监听，提高开发性能
  experimental: {
    // 忽略文件监听，提高性能
    watchOptions: {
      ignored: [
        '**/node_modules/**',
        '**/.git/**',
        '**/output/**',
        '**/dist/**',
        '**/.next/**',
        '**/coverage/**',
        '**/.nyc_output/**',
        '**/logs/**',
        '**/*.log'
      ]
    }
  },
  
  // 配置webpack忽略某些目录
  webpack: (config, { isServer }) => {
    // 忽略node_modules的监听
    config.watchOptions = {
      ...config.watchOptions,
      ignored: [
        '**/node_modules/**',
        '**/.git/**',
        '**/output/**',
        '**/dist/**',
        '**/.next/**',
        '**/coverage/**',
        '**/.nyc_output/**',
        '**/logs/**',
        '**/*.log'
      ],
      // 增加监听延迟，减少CPU占用
      aggregateTimeout: 300,
      // 轮询间隔
      poll: 1000
    }
    
    return config
  }
}

export default nextConfig
