"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function Home() {
  const [url, setUrl] = useState("");
  const [data, setData] = useState<any[]>([]);

  const handleScrape = async () => {
    if (!url) return;
    const response = await fetch("http://127.0.0.1:8000/scrape", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const result = await response.json();
    setData(result);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white relative overflow-hidden">
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
        <div className="flex gap-4 items-center w-full max-w-2xl backdrop-blur-md bg-white/10 rounded-2xl shadow-xl p-4 border border-white/10">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="🔗 Enter a website URL to scrape"
            className="flex-1 bg-transparent text-white placeholder-gray-400 rounded-xl px-4 py-3"
          />

          {/* Button with shimmer hover */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            transition={{ type: "spring", stiffness: 200 }}
            className="relative"
          >
            <Button
              onClick={handleScrape}
              className="bg-gradient-to-r from-blue-500 to-green-500 text-white font-semibold px-6 py-6 rounded-xl shadow-lg overflow-hidden group cursor-pointer"
            >
              <span className="relative z-10">Scrape</span>
              <span className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition duration-500 blur-xl"></span>
            </Button>
          </motion.div>
        </div>
      </motion.div>

      {/* Results Section */}
      {data.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="max-w-6xl mx-auto mt-12 backdrop-blur-lg bg-white/10 rounded-2xl shadow-2xl p-10 border border-white/10"
        >
          <h2 className="text-3xl font-semibold mb-6 text-center text-teal-300 drop-shadow-md">
            Scraped Data
          </h2>
          <div className="overflow-x-auto rounded-lg shadow-inner">
            <Table>
              <TableHeader>
                <TableRow className="bg-gradient-to-r from-blue-600 to-green-500 text-white text-lg">
                  <TableHead className="text-white">URL</TableHead>
                  <TableHead className="text-white">Title</TableHead>
                  <TableHead className="text-white">Date</TableHead>
                  <TableHead className="text-white">Summary</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.map((row, idx) => (
                  <TableRow
                    key={idx}
                    className="hover:bg-white/10 transition-colors"
                  >
                    <TableCell>
                      <a
                        href={row.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-300 hover:underline"
                      >
                        {row.url}
                      </a>
                    </TableCell>
                    <TableCell className="text-gray-200">{row.title}</TableCell>
                    <TableCell className="text-gray-200">{row.date}</TableCell>
                    <TableCell className="text-gray-300">
                      {row.summary}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </motion.div>
      )}

      {/* Decorative background glows */}
      <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse"></div>
      <div className="absolute bottom-20 right-10 w-72 h-72 bg-green-500 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse"></div>
    </div>
  );
}
