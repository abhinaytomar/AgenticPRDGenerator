import type { NextConfig } from "next";

const isDev = process.env.NODE_ENV === "development";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // In local development, proxy /api/* to the FastAPI server running on :8000.
  // `beforeFiles` makes this run before Next's own /api handling. This block is
  // dev-only; in production on Vercel, routing is handled by vercel.json.
  async rewrites() {
    if (!isDev) return [];
    return {
      beforeFiles: [
        { source: "/api/:path*", destination: "http://127.0.0.1:8000/api/:path*" },
      ],
    };
  },
};

export default nextConfig;
