/** @type {import('next').NextConfig} */

// Add your ngrok tunnel URL to allowedDevOrigins for CORS support if needed
const allowedDevOrigins = [
  // Example: "https://your-ngrok-url.ngrok.io"
];

const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  turbo: false,
}

export default nextConfig
