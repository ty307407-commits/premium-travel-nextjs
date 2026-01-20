/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'pub-b953f613e39f4e5ea2f7b7a0e48c659b.r2.dev',
      },
      {
        protocol: 'https',
        hostname: 'img.travel.rakuten.co.jp',
      },
    ],
  },
}

module.exports = nextConfig
