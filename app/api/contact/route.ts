import { NextRequest, NextResponse } from "next/server";

// reCAPTCHA シークレットキー
const RECAPTCHA_SECRET_KEY = process.env.RECAPTCHA_SECRET_KEY || "";

// 送信先メールアドレス
const CONTACT_EMAIL = process.env.CONTACT_EMAIL || "tabi@premium-travel-japan.com";

interface ContactFormData {
  name: string;
  email: string;
  subject: string;
  message: string;
  recaptchaToken: string;
}

// reCAPTCHA 検証
async function verifyRecaptcha(token: string): Promise<boolean> {
  if (!RECAPTCHA_SECRET_KEY) {
    console.warn("RECAPTCHA_SECRET_KEY is not set");
    return true; // 開発環境用: キーがない場合はスキップ
  }

  try {
    const response = await fetch(
      "https://www.google.com/recaptcha/api/siteverify",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `secret=${RECAPTCHA_SECRET_KEY}&response=${token}`,
      }
    );

    const data = await response.json();
    return data.success === true;
  } catch (error) {
    console.error("reCAPTCHA verification failed:", error);
    return false;
  }
}

export async function POST(request: NextRequest) {
  try {
    const body: ContactFormData = await request.json();
    const { name, email, subject, message, recaptchaToken } = body;

    // バリデーション
    if (!name || !email || !subject || !message) {
      return NextResponse.json(
        { error: "必須項目が入力されていません。" },
        { status: 400 }
      );
    }

    // メールアドレス形式チェック
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: "メールアドレスの形式が正しくありません。" },
        { status: 400 }
      );
    }

    // reCAPTCHA 検証
    const isValidRecaptcha = await verifyRecaptcha(recaptchaToken);
    if (!isValidRecaptcha) {
      return NextResponse.json(
        { error: "reCAPTCHAの認証に失敗しました。" },
        { status: 400 }
      );
    }

    // メール送信（ここではログに出力 + 簡易保存）
    // 実際の運用では、Resend, SendGrid, Nodemailer などを使用
    console.log("=== New Contact Form Submission ===");
    console.log(`To: ${CONTACT_EMAIL}`);
    console.log(`From: ${name} <${email}>`);
    console.log(`Subject: ${subject}`);
    console.log(`Message: ${message}`);
    console.log("===================================");

    // TiDB Data Service を使ってお問い合わせを保存（オプション）
    // 後で確認できるようにDBに保存することも可能

    // Webhook通知（Slack, Discord, etc.）を使う場合はここに追加
    // await sendSlackNotification({ name, email, subject, message });

    // 成功レスポンス
    return NextResponse.json(
      { success: true, message: "お問い合わせを受け付けました。" },
      { status: 200 }
    );
  } catch (error) {
    console.error("Contact form error:", error);
    return NextResponse.json(
      { error: "サーバーエラーが発生しました。" },
      { status: 500 }
    );
  }
}
