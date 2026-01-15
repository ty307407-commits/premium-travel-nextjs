import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';
import { Button } from "@/components/ui/button";
import { ArrowLeft, FileText, Upload } from "lucide-react";

export default function Preview() {
  const [content, setContent] = useState('');
  const [showPreview, setShowPreview] = useState(false);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          if (file.name.endsWith('.json')) {
            const json = JSON.parse(event.target?.result as string);
            setContent(json.content || '');
          } else {
            setContent(event.target?.result as string);
          }
          setShowPreview(true);
        } catch (error) {
          alert('ファイルの読み込みに失敗しました');
        }
      };
      reader.readAsText(file);
    }
  };

  return (
    <main className="min-h-screen bg-gray-100">
      {!showPreview ? (
        <div className="flex flex-col items-center justify-center min-h-screen p-8">
          <h1 className="text-2xl font-bold mb-8 flex items-center gap-2">
            <FileText className="w-8 h-8" />
            V4記事プレビュー
          </h1>

          <div className="bg-white p-8 rounded-xl shadow-lg max-w-md w-full">
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

            <div className="mt-6 text-center text-gray-500 text-sm">
              または
            </div>

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
              onClick={() => setShowPreview(false)}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              戻る
            </Button>
            <span className="text-sm text-gray-500">
              文字数: {content.length.toLocaleString()}
            </span>
          </div>

          <article className="pt-20 pb-12 px-4">
            <div className="max-w-3xl mx-auto bg-white rounded-xl shadow-lg p-8 md:p-12 article-content">
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
