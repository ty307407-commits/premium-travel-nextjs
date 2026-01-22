"use client";

import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import remarkGfm from "remark-gfm";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

interface ArticleContentProps {
  content: string;
  slug: string;
}

export default function ArticleContent({ content, slug }: ArticleContentProps) {
  return (
    <main className="min-h-screen bg-white md:bg-gray-100">
      <div className="fixed top-0 left-0 right-0 bg-white shadow z-50 px-4 py-3 flex justify-between items-center">
        <Link href="/">
          <Button variant="ghost" className="flex items-center gap-2">
            <ArrowLeft className="w-4 h-4" />
            ホーム
          </Button>
        </Link>
        <div className="flex items-center gap-4">
          <span className="text-sm text-indigo-600 font-medium truncate max-w-[200px]">
            /{slug}
          </span>
          <span className="text-sm text-gray-500">
            文字数: {content.length.toLocaleString()}
          </span>
        </div>
      </div>

      <article className="pt-20 pb-12 px-4 md:px-8">
        <div className="max-w-3xl mx-auto article-content md:bg-white md:rounded-xl md:shadow-lg md:p-8 lg:p-12">
          <ReactMarkdown rehypePlugins={[rehypeRaw]} remarkPlugins={[remarkGfm]}>
            {content}
          </ReactMarkdown>
        </div>
      </article>
    </main>
  );
}
