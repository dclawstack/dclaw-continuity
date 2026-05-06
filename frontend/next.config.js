/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://dclaw-continuity-backend:8138/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
