/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/assessments/:path*',
        destination: 'http://localhost:8000/api/assessments/:path*',
      },
    ];
  },
};

export default nextConfig;
