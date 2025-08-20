/** @type {import('next').NextConfig} */
const nextConfig = {
  // Desabilitar Next.js Dev Tools
  devIndicators: {
    buildActivity: false,
    buildActivityPosition: "bottom-right",
  },

  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/:path*",
      },
    ];
  },
};

module.exports = nextConfig;
