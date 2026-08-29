/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    unoptimized: true,
  },
  async rewrites() {
    const backendBase = process.env.NEXT_PUBLIC_API_URL
      ? process.env.NEXT_PUBLIC_API_URL.replace(/\/api\/?$/, '')
      : 'https://vedaai-assessment-f7ds.onrender.com';
    return [
      {
        source: '/api/assessments/:path*',
        destination: `${backendBase}/api/assessments/:path*`,
      },
    ];
  },
};

export default nextConfig;
