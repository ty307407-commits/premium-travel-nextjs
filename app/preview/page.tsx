"use client";

import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import remarkGfm from "remark-gfm";
import { Button } from "@/components/ui/button";
import { ArrowLeft, FileText, Upload, Loader2, Database } from "lucide-react";

export default function PreviewPage() {
  const [content, setContent] = useState("");
  const [showPreview, setShowPreview] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [pageId, setPageId] = useState<number | null>(null);
  const [inputPageId, setInputPageId] = useState("");

  // TiDBからの記事取得（Serverless API経由）
  const fetchArticle = async (id: number) => {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`/api/article?id=${id}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "記事の取得に失敗しました");
      }

      setContent(data.content || "");
      setShowPreview(true);
    } catch (err: unknown) {
      setError(`記事が見つかりません (Page ID: ${id})`);
    } finally {
      setLoading(false);
    }
  };

  // URLパラメータからの自動読み込み
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const url = params.get("url");
    const id = params.get("id");

    // ?id= パラメータ: TiDBから取得
    if (id) {
      const numId = parseInt(id);
      if (!isNaN(numId)) {
        setPageId(numId);
        fetchArticle(numId);
      }
    }
    // ?url= パラメータ: 外部URLから取得
    else if (url) {
      setLoading(true);
      setError("");

      fetch(url)
        .then((res) => {
          if (!res.ok) throw new Error("ファイルの取得に失敗しました");
          return res.json();
        })
        .then((data) => {
          setContent(data.content || "");
          setShowPreview(true);
          setLoading(false);
        })
        .catch((err) => {
          setError(err.message);
          setLoading(false);
        });
    }
  }, []);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          if (file.name.endsWith(".json")) {
            const json = JSON.parse(event.target?.result as string);
            setContent(json.content || "");
          } else {
            setContent(event.target?.result as string);
          }
          setShowPreview(true);
        } catch {
          alert("ファイルの読み込みに失敗しました");
        }
      };
      reader.readAsText(file);
    }
  };

  const handleSearchById = () => {
    const numId = parseInt(inputPageId);
    if (!isNaN(numId)) {
      setPageId(numId);
      fetchArticle(numId);
    }
  };

  // ローディング画面
  if (loading) {
    return (
      <main className="min-h-screen bg-white flex flex-col items-center justify-center">
        <Loader2 className="w-12 h-12 animate-spin text-indigo-600 mb-4" />
        <p className="text-gray-600">
          {pageId
            ? `ページID ${pageId} の記事を読み込み中...`
            : "記事を読み込み中..."}
        </p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-white md:bg-gray-100">
      {!showPreview ? (
        <div className="flex flex-col items-center justify-center min-h-screen p-8">
          <h1 className="text-2xl font-bold mb-8 flex items-center gap-2">
            <FileText className="w-8 h-8" />
            V4記事プレビュー
          </h1>

          {error && (
            <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-4 max-w-md w-full">
              {error}
            </div>
          )}

          <div className="bg-white p-8 rounded-xl shadow-lg max-w-md w-full">
            {/* TiDBから取得 */}
            <div className="mb-6 pb-6 border-b">
              <span className="text-gray-700 font-medium flex items-center gap-2 mb-3">
                <Database className="w-4 h-4" />
                ページIDで検索
              </span>
              <div className="flex gap-2">
                <input
                  type="number"
                  placeholder="例: 897"
                  value={inputPageId}
                  className="flex-1 p-2 border rounded-lg text-sm"
                  onChange={(e) => setInputPageId(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearchById()}
                />
                <Button onClick={handleSearchById} disabled={!inputPageId}>
                  取得
                </Button>
              </div>
            </div>

            {/* ファイルアップロード */}
            <label className="block mb-4">
              <span className="text-gray-700 font-medium flex items-center gap-2">
                <Upload className="w-4 h-4" />
                JSONまたはMDファイルをアップロード
              </span>
              <input
                type="file"
                accept=".json,.md"
                onChange={handleFileUpload}
                className="mt-2 block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-full file:border-0
                  file:text-sm file:font-semibold
                  file:bg-indigo-50 file:text-indigo-700
                  hover:file:bg-indigo-100"
              />
            </label>

            <div className="mt-6 text-center text-gray-500 text-sm">または</div>

            <textarea
              placeholder="記事のMarkdown/HTMLをここに貼り付け..."
              className="mt-4 w-full h-32 p-3 border rounded-lg text-sm"
              onChange={(e) => setContent(e.target.value)}
            />

            <Button
              onClick={() => content && setShowPreview(true)}
              disabled={!content}
              className="mt-4 w-full"
            >
              プレビュー表示
            </Button>
          </div>
        </div>
      ) : (
        <div>
          <div className="fixed top-0 left-0 right-0 bg-white shadow z-50 px-4 py-3 flex justify-between items-center">
            <Button
              variant="ghost"
              onClick={() => {
                setShowPreview(false);
                setPageId(null);
                setInputPageId("");
              }}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              戻る
            </Button>
            <div className="flex items-center gap-4">
              {pageId && (
                <span className="text-sm text-indigo-600 font-medium">
                  Page ID: {pageId}
                </span>
              )}
              <span className="text-sm text-gray-500">
                文字数: {content.length.toLocaleString()}
              </span>
            </div>
          </div>

          <article className="pt-20 pb-12 px-4 md:px-8">
            <div className="max-w-3xl mx-auto article-content md:bg-white md:rounded-xl md:shadow-lg md:p-8 lg:p-12">
              <ReactMarkdown
                rehypePlugins={[rehypeRaw]}
                remarkPlugins={[remarkGfm]}
              >
                {content}
              </ReactMarkdown>
            </div>
          </article>
        </div>
      )}
    </main>
  );
}
