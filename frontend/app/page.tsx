"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";

export default function Home() {
  const [url, setUrl] = useState("");
  const [pages, setPages] = useState(1);
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showSuccess, setShowSuccess] = useState(false);

  const handleScrape = async () => {
    if (!url || !pages) return;
    setLoading(true);
    setData([]);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/scrape", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, pages: Number(pages) }),
      });

      if (!response.ok) {
        throw new Error(`Failed with status ${response.status}`);
      }

      const result = await response.json();
      setData(result.data || []);
      if (result.data && result.data.length > 0) {
        setShowSuccess(true);
        setTimeout(() => setShowSuccess(false), 7000);
      }
    } catch (err) {
      console.error("Error scraping:", err);
      setError(
        "❌ This website cannot be scraped — it may be protected by security systems like Cloudflare or block automated requests."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setUrl("");
    setPages(1);
    setData([]);
    setError("");
    setShowSuccess(false);
  };

  const handleDownloadCSV = () => {
    if (!data.length) return;

    const headers = ["URL", "Title", "Date", "Summary"];
    const rows = data.map((row) => [
      row.url,
      row.title || "-",
      row.date || "-",
      row.summary || "-",
    ]);

    const csvContent = [headers, ...rows]
      .map((e) => e.map((v) => `"${String(v).replace(/"/g, '""')}"`).join(","))
      .join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.setAttribute("download", "scraped_data.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black pb-20 text-white relative overflow-hidden scroll-smooth">
      {/* Hero Title */}
      <motion.h1
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
        className="text-5xl font-extrabold mb-12 mt-12 text-center bg-gradient-to-r from-blue-500 via-teal-400 to-green-500 bg-clip-text text-transparent drop-shadow-xl"
      >
        Web Scraper
      </motion.h1>

      {/* Input + Button Section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="flex justify-center mb-12"
      >
        <div className="flex gap-4 items-center w-full max-w-3xl backdrop-blur-md bg-white/10 rounded-2xl shadow-xl p-4 border border-white/10">
          {/* URL Input */}
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="🔗 Enter a website URL"
            className="flex-1 bg-transparent text-white placeholder-gray-400 rounded-xl px-4 py-3"
          />

          {/* Pages Input */}
          <input
            type="number"
            min="1"
            value={pages}
            onChange={(e) => setPages(Number(e.target.value))}
            placeholder="Pages"
            className="w-24 bg-transparent text-white placeholder-gray-400 rounded-xl px-4 py-3 border border-white/20"
          />

          {/* Scrape Button */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            transition={{ type: "spring", stiffness: 200 }}
            className="relative"
          >
            <Button
              onClick={handleScrape}
              disabled={loading}
              className="bg-gradient-to-r from-blue-500 to-green-500 text-white font-semibold px-6 py-6 rounded-xl shadow-lg overflow-hidden group cursor-pointer disabled:opacity-50"
            >
              <span className="relative z-10">
                {loading ? "Scraping..." : "Scrape"}
              </span>
              <span className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition duration-500 blur-xl"></span>
            </Button>
          </motion.div>

          {/* Download Button (only if data exists) */}
          {/* Download Button (only if data exists) */}
          {data.length > 0 && (
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              transition={{ type: "spring", stiffness: 200 }}
              className="relative"
            >
              <Button
                onClick={handleDownloadCSV}
                className="bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold px-6 py-6 rounded-xl shadow-lg overflow-hidden group cursor-pointer"
              >
                <span className="relative z-10">Download CSV</span>
                <span className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition duration-500 blur-xl"></span>
              </Button>
            </motion.div>
          )}
          {data.length > 0 && (
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              transition={{ type: "spring", stiffness: 200 }}
              className="absolute -right-35"
            >
              <Button
                onClick={handleReset}
                className="bg-gradient-to-r from-red-600 to-red-400 text-white font-semibold px-6 py-6 rounded-xl shadow-lg overflow-hidden group cursor-pointer"
              >
                <span className="relative z-10">🔄 Reset</span>
                <span className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition duration-500 blur-xl"></span>
              </Button>
            </motion.div>
          )}
        </div>
      </motion.div>
          
      {/* Loading Animation */}
      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex justify-center items-center mt-20"
        >
          <div className="flex flex-col items-center gap-4">
            <motion.div
              className="w-16 h-16 border-4 border-t-transparent border-teal-400 rounded-full"
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
            />
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{
                duration: 0.8,
                repeat: Infinity,
                repeatType: "reverse",
              }}
              className="text-teal-300 text-lg"
            >
              Fetching Data...
            </motion.p>
          </div>
        </motion.div>
      )}

      {/* Data Table */}
      {!loading && data.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="max-w-[90%] mx-auto mt-12 backdrop-blur-lg bg-white/10 rounded-2xl shadow-2xl p-10 border border-white/10"
        >
          <h2 className="text-3xl font-semibold mb-6 text-center text-teal-300 drop-shadow-md">
            Scraped Data
          </h2>
          <div className="w-full overflow-x-auto rounded-lg shadow-xl border border-white/20">
            <table className="w-full table-fixed border-collapse">
              <thead>
                <tr className="bg-gradient-to-r from-blue-600 to-green-500 text-white text-lg">
                  <th className="px-4 py-3">URL</th>
                  <th className="px-4 py-3">Title</th>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">Summary</th>
                </tr>
              </thead>
            </table>

            {/* Scrollable tbody container */}
            <div className="max-h-[800px] overflow-y-auto text-center">
              <table className="w-full table-fixed border-collapse">
                <tbody>
                  {data.map((row, idx) => (
                    <tr
                      key={idx}
                      className="hover:bg-white/10 transition-colors"
                    >
                      <td className="px-4 py-3 break-words max-w-[300px]">
                        <a
                          href={row.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-300 hover:underline break-words"
                        >
                          {row.url}
                        </a>
                      </td>
                      <td className="px-4 py-3 break-words max-w-[300px] text-gray-200">
                        {row.title && row.title.trim() !== "" ? row.title : "-"}
                      </td>
                      <td className="px-4 py-3 break-words max-w-[200px] text-gray-200">
                        {row.date && row.date.trim() !== "" ? row.date : "-"}
                      </td>
                      <td className="px-4 py-3 break-words max-w-[500px] text-gray-300">
                        {row.summary && row.summary.trim() !== ""
                          ? row.summary.length > 150
                            ? row.summary.slice(0, 150) + "..."
                            : row.summary
                          : "-"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      )}

      {!loading && error && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-lg mx-auto mt-12 p-6 rounded-2xl bg-red-500/10 border border-red-400/30 text-center shadow-xl"
        >
          <h3 className="text-xl font-semibold text-red-400 mb-2">
            Unable to Fetch
          </h3>
          <p className="text-gray-300">{error}</p>
        </motion.div>
      )}

      {showSuccess && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.5 }}
          className="fixed top-6 right-6 max-w-xs px-6 py-4 rounded-xl bg-green-500/10 border border-green-400/30 text-center shadow-xl backdrop-blur-md z-50"
        >
          <h3 className="text-lg font-semibold text-green-400">✅ Success</h3>
          <p className="text-gray-300 text-sm mt-1">
            Scraped successfully. {data.length} results found.
          </p>
        </motion.div>
      )}

      {/* Decorative background glows */}
      <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse will-change-transform"></div>
      <div className="absolute bottom-20 right-10 w-72 h-72 bg-green-500 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse will-change-transform"></div>
    </div>
  );
}
