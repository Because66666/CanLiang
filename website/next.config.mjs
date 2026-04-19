/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_APP_VERSION: process.env.npm_package_version,
  },
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
  // basePath: '/CanLiang', // 根据 bgi 本体做出的改编.
  // assetPrefix: '/CanLiang', // 根据 bgi 本体做出的改编
  
  // 配置 webpack 忽略某些目录
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
