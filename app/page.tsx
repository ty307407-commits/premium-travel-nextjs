import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-50 to-white flex flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold text-indigo-900 mb-4">
        プレミアムトラベル
      </h1>
      <p className="text-gray-600 mb-8 text-center max-w-md">
        高級温泉旅館の厳選ガイド
      </p>
      <Link
        href="/preview"
        className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition"
      >
        記事プレビュー
      </Link>
    </main>
  );
}
