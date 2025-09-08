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
  // basePath: '/CanLiang', // 根据bgi本体做出的改编.
  // assetPrefix: '/CanLiang', // 根据bgi本体做出的改编
}

export default nextConfig
