"use client";

import { useState, useRef, FormEvent } from "react";
import Link from "next/link";
import Script from "next/script";

// reCAPTCHA v2 サイトキー（Vercel環境変数から取得）
const RECAPTCHA_SITE_KEY = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY || "";

declare global {
  interface Window {
    grecaptcha: {
      ready: (callback: () => void) => void;
      render: (
        container: string | HTMLElement,
        parameters: {
          sitekey: string;
          callback?: (token: string) => void;
          "expired-callback"?: () => void;
        }
      ) => number;
      reset: (widgetId?: number) => void;
      getResponse: (widgetId?: number) => string;
    };
  }
}

type FormStatus = "idle" | "submitting" | "success" | "error";

export default function ContactPage() {
  const [formStatus, setFormStatus] = useState<FormStatus>("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [recaptchaLoaded, setRecaptchaLoaded] = useState(false);
  const formRef = useRef<HTMLFormElement>(null);

  const handleRecaptchaLoad = () => {
    setRecaptchaLoaded(true);
    if (window.grecaptcha && RECAPTCHA_SITE_KEY) {
      window.grecaptcha.ready(() => {
        window.grecaptcha.render("recaptcha-container", {
          sitekey: RECAPTCHA_SITE_KEY,
        });
      });
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setFormStatus("submitting");
    setErrorMessage("");

    const formData = new FormData(e.currentTarget);
    const name = formData.get("name") as string;
    const email = formData.get("email") as string;
    const subject = formData.get("subject") as string;
    const message = formData.get("message") as string;

    // reCAPTCHA トークン取得
    const recaptchaToken = window.grecaptcha?.getResponse() || "";

    if (!recaptchaToken) {
      setFormStatus("error");
      setErrorMessage("reCAPTCHAの認証を完了してください。");
      return;
    }

    try {
      const response = await fetch("/api/contact", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          email,
          subject,
          message,
          recaptchaToken,
        }),
      });

      if (response.ok) {
        setFormStatus("success");
        formRef.current?.reset();
        window.grecaptcha?.reset();
      } else {
        const data = await response.json();
        setFormStatus("error");
        setErrorMessage(data.error || "送信に失敗しました。");
      }
    } catch {
      setFormStatus("error");
      setErrorMessage("通信エラーが発生しました。");
    }
  };

  return (
    <>
      {/* reCAPTCHA スクリプト */}
      <Script
        src="https://www.google.com/recaptcha/api.js"
        strategy="lazyOnload"
        onLoad={handleRecaptchaLoad}
      />

      <main className="min-h-screen bg-gradient-to-b from-indigo-50 via-white to-white">
        {/* ヘッダー */}
        <section className="py-12 px-4 text-center bg-gradient-to-br from-indigo-600 to-purple-700 text-white">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-2xl md:text-3xl font-bold mb-2">
              お問い合わせ
            </h1>
            <p className="text-sm md:text-base opacity-90">
              ご質問・ご要望などお気軽にお問い合わせください
            </p>
          </div>
        </section>

        {/* フォームセクション */}
        <section className="py-12 px-4">
          <div className="max-w-xl mx-auto">
            {formStatus === "success" ? (
              <div className="bg-green-50 border border-green-200 rounded-xl p-8 text-center">
                <div className="text-4xl mb-4">✅</div>
                <h2 className="text-xl font-bold text-green-800 mb-2">
                  送信完了
                </h2>
                <p className="text-green-700 mb-6">
                  お問い合わせありがとうございます。
                  <br />
                  内容を確認の上、ご連絡いたします。
                </p>
                <Link
                  href="/"
                  className="inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition"
                >
                  トップページへ
                </Link>
              </div>
            ) : (
              <form
                ref={formRef}
                onSubmit={handleSubmit}
                className="bg-white rounded-xl p-6 md:p-8 shadow-sm border border-gray-100"
              >
                {/* エラーメッセージ */}
                {formStatus === "error" && (
                  <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                    {errorMessage}
                  </div>
                )}

                {/* お名前 */}
                <div className="mb-6">
                  <label
                    htmlFor="name"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    お名前 <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
                    placeholder="山田 太郎"
                  />
                </div>

                {/* メールアドレス */}
                <div className="mb-6">
                  <label
                    htmlFor="email"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    メールアドレス <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
                    placeholder="example@email.com"
                  />
                </div>

                {/* 件名 */}
                <div className="mb-6">
                  <label
                    htmlFor="subject"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    件名 <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    id="subject"
                    name="subject"
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition"
                    placeholder="お問い合わせ内容の件名"
                  />
                </div>

                {/* メッセージ */}
                <div className="mb-6">
                  <label
                    htmlFor="message"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    メッセージ <span className="text-red-500">*</span>
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    required
                    rows={6}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition resize-none"
                    placeholder="お問い合わせ内容をご記入ください"
                  />
                </div>

                {/* reCAPTCHA */}
                <div className="mb-6">
                  <div
                    id="recaptcha-container"
                    className="flex justify-center"
                  />
                  {!recaptchaLoaded && RECAPTCHA_SITE_KEY && (
                    <p className="text-sm text-gray-500 text-center mt-2">
                      reCAPTCHAを読み込み中...
                    </p>
                  )}
                  {!RECAPTCHA_SITE_KEY && (
                    <p className="text-sm text-amber-600 text-center mt-2">
                      ※reCAPTCHAが設定されていません
                    </p>
                  )}
                </div>

                {/* 送信ボタン */}
                <button
                  type="submit"
                  disabled={formStatus === "submitting"}
                  className="w-full bg-indigo-600 text-white py-4 rounded-lg font-medium hover:bg-indigo-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {formStatus === "submitting" ? "送信中..." : "送信する"}
                </button>

                <p className="mt-4 text-xs text-gray-500 text-center">
                  送信いただいた内容は、お問い合わせへの回答のみに使用いたします。
                </p>
              </form>
            )}

            {/* 戻るリンク */}
            <div className="mt-8 text-center">
              <Link
                href="/about"
                className="text-indigo-600 hover:underline text-sm"
              >
                ← 編集部についてに戻る
              </Link>
            </div>
          </div>
        </section>
      </main>
    </>
  );
}
