/** @type {import('next').NextConfig} */
const backend = process.env.BACKEND_URL || "http://127.0.0.1:8000";

const nextConfig = {
  reactStrictMode: true,
  output: process.env.NEXT_OUTPUT === "standalone" ? "standalone" : undefined,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${backend.replace(/\/$/, "")}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
