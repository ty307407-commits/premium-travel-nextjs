"use client";

// Article content component - displays markdown content
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import remarkGfm from "remark-gfm";

interface ArticleContentProps {
  content: string;
  slug: string;
}

export default function ArticleContent({ content, slug }: ArticleContentProps) {
  return (
    <main className="min-h-screen bg-white md:bg-gray-100">
      <article className="py-12 px-4 md:px-8">
        <div className="max-w-3xl mx-auto article-content md:bg-white md:rounded-xl md:shadow-lg md:p-8 lg:p-12">
          <ReactMarkdown rehypePlugins={[rehypeRaw]} remarkPlugins={[remarkGfm]}>
            {content}
          </ReactMarkdown>
        </div>
      </article>
    </main>
  );
}
