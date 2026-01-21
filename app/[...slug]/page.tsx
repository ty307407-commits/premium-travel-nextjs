"use client";

import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import remarkGfm from "remark-gfm";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";

export default function ArticlePage() {
  const params = useParams();
  const [content, setContent] = useState("");
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // URLからslugを取得
  const slugArray = params.slug as string[];
  const fullSlug = slugArray ? slugArray.join("/") : "";

  useEffect(() => {
    if (!fullSlug) return;

    const fetchArticle = async () => {
      setLoading(true);
      setError("");
      try {
        const response = await fetch(
          `/api/article-by-slug?slug=${encodeURIComponent(fullSlug)}`
        );
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || "記事の取得に失敗しました");
        }

        setContent(data.content || "");
        setTitle(data.title || "");
      } catch (err: unknown) {
        const errorMessage =
          err instanceof Error ? err.message : "記事が見つかりません";
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchArticle();
  }, [fullSlug]);

  // ローディング画面
  if (loading) {
    return (
      <main className="min-h-screen bg-white flex flex-col items-center justify-center">
        <Loader2 className="w-12 h-12 animate-spin text-indigo-600 mb-4" />
        <p className="text-gray-600">記事を読み込み中...</p>
      </main>
    );
  }

  // エラー画面
  if (error) {
    return (
      <main className="min-h-screen bg-white flex flex-col items-center justify-center p-8">
        <div className="bg-red-50 text-red-600 p-6 rounded-lg mb-6 max-w-md w-full text-center">
          <p className="font-medium mb-2">エラー</p>
          <p>{error}</p>
          <p className="text-sm mt-2 text-gray-500">URL: /{fullSlug}</p>
        </div>
        <Link href="/">
          <Button variant="outline">
            <ArrowLeft className="w-4 h-4 mr-2" />
            ホームに戻る
          </Button>
        </Link>
      </main>
    );
  }

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
            /{fullSlug}
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
