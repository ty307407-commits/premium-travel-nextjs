#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ピラーコンテンツ（ガイドページ）挿入スクリプト

結婚記念日温泉ガイドなど、特別なピラーコンテンツをDBに挿入
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Optional, Dict
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

# Cloudflare R2 画像ベースURL
CLOUDFLARE_BASE_URL = "https://pub-b953f613e39f4e5ea2f7b7a0e48c659b.r2.dev"
IMAGE_PATH = "Wedding anniversary onsen guide"


class PillarContentInserter:
    """ピラーコンテンツ挿入クラス"""

    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        """データベース接続"""
        self.conn = mysql.connector.connect(
            host=os.getenv('TIDB_HOST', 'gateway01.ap-northeast-1.prod.aws.tidbcloud.com'),
            port=int(os.getenv('TIDB_PORT', 4000)),
            user=os.getenv('TIDB_USER', '4VWXcjUowH2PPCE.root'),
            password=os.getenv('TIDB_PASSWORD', '6KcooGBdpDcmeIGI'),
            database=os.getenv('TIDB_DATABASE', 'test'),
            ssl_ca=os.getenv('TIDB_SSL_CA', '/etc/ssl/certs/ca-certificates.crt')
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def close(self):
        """接続を閉じる"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def get_next_page_id(self) -> int:
        """次に使用可能なpage_idを取得"""
        self.cursor.execute("SELECT MAX(page_id) as max_id FROM page_data")
        result = self.cursor.fetchone()
        return (result['max_id'] or 0) + 1

    def insert_pillar_page(
        self,
        url_slug: str,
        page_title: str,
        content: str,
        meta_description: str,
        hero_image_url: str = None,
        theme_id: int = 30005,  # ピラーコンテンツ用デフォルトテーマ
        author_id: int = 1
    ) -> Dict:
        """
        ピラーコンテンツページを挿入

        Args:
            url_slug: URLスラッグ（例: guides/wedding-anniversary-working-couples）
            page_title: ページタイトル
            content: Markdownコンテンツ
            meta_description: メタディスクリプション
            hero_image_url: ヒーロー画像URL
            theme_id: テーマID
            author_id: 著者ID

        Returns:
            挿入結果情報
        """
        # 次のpage_idを取得
        page_id = self.get_next_page_id()

        # url_slugの正規化（先頭のスラッシュを追加）
        if not url_slug.startswith('/'):
            url_slug = '/' + url_slug

        # page_dataに挿入
        self.cursor.execute("""
            INSERT INTO page_data (
                page_id, theme_id, theme_title, page_title, url_slug,
                meta_description, author_id, hero_image_url,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
            )
        """, (
            page_id, theme_id, 'ピラーコンテンツ', page_title, url_slug,
            meta_description, author_id, hero_image_url
        ))

        page_data_id = self.cursor.lastrowid

        # タイトルをコンテンツから抽出
        import re
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else page_title

        # articlesに挿入
        word_count = len(content)
        self.cursor.execute("""
            INSERT INTO articles (
                page_id, status, title, content, meta_description,
                word_count, generated_at
            ) VALUES (
                %s, 'published', %s, %s, %s, %s, NOW()
            )
        """, (page_data_id, title, content, meta_description, word_count))

        article_id = self.cursor.lastrowid

        self.conn.commit()

        return {
            'page_data_id': page_data_id,
            'page_id': page_id,
            'article_id': article_id,
            'url_slug': url_slug,
            'title': title
        }

    def update_pillar_page(
        self,
        url_slug: str,
        page_title: str,
        content: str,
        meta_description: str,
        hero_image_url: str = None
    ) -> Dict:
        """
        既存のピラーコンテンツページを更新

        Args:
            url_slug: URLスラッグ（例: guides/wedding-anniversary-working-couples）
            page_title: ページタイトル
            content: Markdownコンテンツ
            meta_description: メタディスクリプション
            hero_image_url: ヒーロー画像URL

        Returns:
            更新結果情報
        """
        # url_slugの正規化
        if not url_slug.startswith('/'):
            url_slug = '/' + url_slug

        # page_dataを検索
        self.cursor.execute(
            "SELECT id, page_id FROM page_data WHERE url_slug = %s",
            (url_slug,)
        )
        result = self.cursor.fetchone()

        if not result:
            raise ValueError(f"ページが見つかりません: {url_slug}")

        page_data_id = result['id']
        page_id = result['page_id']

        # page_dataを更新
        self.cursor.execute("""
            UPDATE page_data SET
                page_title = %s,
                meta_description = %s,
                hero_image_url = %s,
                updated_at = NOW()
            WHERE id = %s
        """, (page_title, meta_description, hero_image_url, page_data_id))

        # タイトルをコンテンツから抽出
        import re
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else page_title

        # articlesを更新
        word_count = len(content)
        self.cursor.execute("""
            UPDATE articles SET
                title = %s,
                content = %s,
                meta_description = %s,
                word_count = %s,
                generated_at = NOW()
            WHERE page_id = %s
        """, (title, content, meta_description, word_count, page_data_id))

        self.conn.commit()

        return {
            'page_data_id': page_data_id,
            'page_id': page_id,
            'url_slug': url_slug,
            'title': title,
            'action': 'updated'
        }


def get_image_url(folder: str, filename: str) -> str:
    """Cloudflare R2の画像URLを生成"""
    # スペースを%20にエンコード
    encoded_path = IMAGE_PATH.replace(' ', '%20')
    return f"{CLOUDFLARE_BASE_URL}/{encoded_path}/{folder}/{filename}"


# =====================================================
# 結婚記念日温泉ガイド - 働いている世代向け (30-50代)
# =====================================================

GUIDE_WORKING_COUPLES = """# 結婚記念日は温泉旅行で特別な時間を｜忙しい30〜50代夫婦のための完全ガイド

## はじめに：忙しい毎日だからこそ、ふたりだけの時間を

![温泉で過ごす夫婦の時間]({img_A01_main})

「今年の結婚記念日、何かしたいけど時間がない...」
「子どもの世話や仕事で、夫婦でゆっくり過ごすことなんて難しい...」

そんな風に感じている30〜50代のご夫婦は多いのではないでしょうか。

仕事、育児、家事、介護——現代の夫婦は、まさに人生で最も忙しい時期を駆け抜けています。気がつけば、ふたりでゆっくり話す時間すら取れていないことも。

でも、だからこそ。
**結婚記念日という節目に、思い切って「ふたりの時間」を取り戻しませんか？**

温泉旅行には、忙しい夫婦のための魔法があります。

- スマホの通知を気にせず、湯船でぼんやりできる贅沢
- 美味しい料理を前に「おいしいね」と笑い合える幸せ
- 何も予定を入れず、ただそばにいるだけの安らぎ

この記事では、**限られた時間と予算の中でも、最高の結婚記念日を過ごすための温泉旅行ガイド**をお届けします。

---

## 第1章：なぜ結婚記念日に「温泉旅行」がおすすめなのか

### 1-1. 温泉には「夫婦の会話」を自然に生み出す力がある

普段の生活では、夫婦の会話といえば「今日の晩ごはん何にする？」「子どもの学校のプリント見た？」など、事務的なものになりがちです。

ところが温泉旅館に着いた瞬間から、会話の質が変わります。

- 「この旅館、いい雰囲気だね」
- 「お湯が気持ちいいね」
- 「この料理、どうやって作るんだろう？」

**非日常の空間は、ふたりを「家族」から「夫婦」に戻してくれます。**

心理学的にも、新しい環境は脳を活性化させ、ポジティブな感情を生みやすくすることが分かっています。温泉旅行は、まさに「夫婦の関係をリフレッシュする」絶好の機会なのです。

### 1-2. 「露天風呂付き客室」という選択

![露天風呂付き客室でくつろぐ夫婦]({img_A02_rotenburo})

結婚記念日の温泉旅行で、特におすすめしたいのが**露天風呂付き客室**です。

大浴場も素晴らしいのですが、夫婦ふたりでゆっくり過ごすなら、プライベートな空間のある客室露天風呂がベスト。

**露天風呂付き客室のメリット：**
- 好きな時間に、好きなだけ温泉を楽しめる
- 周りを気にせず、ふたりで会話できる
- チェックインからチェックアウトまで、部屋で完結できる
- 子連れでないからこそ味わえる「大人だけの贅沢」

### 1-3. 「特別なことをしない」という贅沢

温泉旅行の魅力は、**「何もしなくていい」こと**かもしれません。

普段は「あれもしなきゃ、これもしなきゃ」と追われる毎日。でも温泉旅館では、やることといえば——

1. チェックインして、お茶を飲む
2. 温泉に入る
3. 食事をする
4. また温泉に入る
5. ゆっくり眠る

これだけ。この「何もしない時間」こそが、忙しい夫婦への最高のご褒美なのです。

---

## 第2章：結婚記念日におすすめの温泉地ガイド

![温泉街を散策する夫婦]({img_A06_sanpo})

日本全国には3,000以上の温泉地があると言われています。その中から、「結婚記念日」にふさわしい温泉地をご紹介します。

### 2-1. 関東から気軽にアクセスできる温泉地

#### 箱根（神奈川県）
**東京から約1時間30分のアクセス抜群のリゾート**

箱根は、仕事終わりにそのまま行ける手軽さが魅力。金曜の夜にチェックインして、土曜をゆっくり過ごし、日曜の午前中に帰宅——そんな「弾丸記念日旅行」も可能です。

**箱根のおすすめポイント：**
- 多彩な泉質（強羅、仙石原、湯本など）
- 美術館やカフェなど観光スポットも充実
- 高級旅館からカジュアルな宿まで選択肢が豊富

[箱根の露天風呂付き客室を探す →](/kanto/hakone)

#### 伊豆・熱海（静岡県）
**海と山の両方を楽しめる、癒しの温泉郷**

伊豆半島には、海を望む絶景露天風呂を持つ宿が数多くあります。特に**東伊豆**は、朝日が昇る海を眺めながらの温泉が格別。

**伊豆・熱海のおすすめポイント：**
- オーシャンビューの露天風呂が豊富
- 新鮮な海の幸（金目鯛、伊勢エビなど）
- レトロな温泉街の散策も楽しい

[伊豆の露天風呂付き客室を探す →](/kanto/izu)
[熱海の露天風呂付き客室を探す →](/kanto/atami)

### 2-2. 関西から行きやすい温泉地

#### 有馬温泉（兵庫県）
**日本最古の温泉で、特別な一日を**

有馬温泉は、日本書紀にも登場する歴史ある温泉地。大阪・神戸から1時間以内というアクセスの良さも魅力です。

**有馬温泉のおすすめポイント：**
- 「金泉」「銀泉」という2種類の泉質
- 神戸牛など美食も充実
- 温泉街の散策が楽しい

[有馬温泉の露天風呂付き客室を探す →](/kinki/arima)

#### 城崎温泉（兵庫県）
**7つの外湯巡りを楽しむ、浴衣デートの聖地**

城崎温泉は、浴衣姿で温泉街を歩く——そんな「THE・温泉旅行」を楽しめる温泉地。外湯巡りはまさに夫婦のデートにぴったりです。

**城崎温泉のおすすめポイント：**
- 7つの外湯を巡るワクワク感
- 浴衣姿で歩ける風情ある温泉街
- 冬のカニ料理は絶品

[城崎温泉の露天風呂付き客室を探す →](/kinki/kinosaki)

### 2-3. 特別な記念日にふさわしい「隠れ家」的温泉地

#### 由布院（大分県）
**女性人気No.1の、おしゃれな温泉リゾート**

由布院は、「温泉地」というより「リゾート」という表現がぴったり。おしゃれなカフェやギャラリーが点在し、大人のふたり旅にぴったりです。

**由布院のおすすめポイント：**
- 由布岳を望む絶景露天風呂
- アート＆グルメが充実
- 「ふたりの時間」を大切にする宿が多い

[由布院の露天風呂付き客室を探す →](/kyushu/yufuin)

#### 黒川温泉（熊本県）
**「入湯手形」で巡る、情緒あふれる温泉郷**

黒川温泉は、渓谷沿いに佇む小さな温泉地。「入湯手形」を使って3つの露天風呂を巡れるシステムが人気です。

**黒川温泉のおすすめポイント：**
- 自然に囲まれた風情ある温泉街
- 全体が「一つの旅館」のようなコンセプト
- 夫婦でゆっくり散策できる規模感

[黒川温泉の露天風呂付き客室を探す →](/kyushu/kurokawa)

---

## 第3章：予算別・温泉旅行プランニング

「温泉旅行は高い」というイメージがあるかもしれません。でも実は、工夫次第でさまざまな予算で楽しめます。

### 3-1. 【お手頃プラン】1泊2万円台〜

**平日を狙えば、露天風呂付き客室も夢じゃない**

週末は料金が高くなりがちですが、平日なら同じ宿でもかなりお得に泊まれます。有給を1日取って、月〜火曜日や火〜水曜日の宿泊がおすすめ。

**お得に泊まるコツ：**
- 記念日特典のあるプランを探す
- 食事の品数を控えめにしたプランを選ぶ
- 直前割引やタイムセールをチェック

### 3-2. 【スタンダードプラン】1泊4万円台〜

**「ちょっと贅沢」を叶える、記念日らしいプラン**

せっかくの結婚記念日なら、少し背伸びした宿を選んでみませんか？1泊4万円台からであれば、**夕食は部屋食・客室に露天風呂付き**という、プライベート感たっぷりの滞在が可能です。

**このクラスの宿の特徴：**
- 料理のクオリティが高い
- 接客がきめ細やか
- 記念日のサプライズ対応あり

### 3-3. 【プレミアムプラン】1泊7万円台〜

![記念日ディナーを楽しむ夫婦]({img_A05_dinner})

**一生の思い出に残る、最高の一日を**

節目の記念日（銀婚式、10周年など）や、「今年は特別に」という年には、思い切って高級旅館を選んでみてはいかがでしょう。

**プレミアムプランの魅力：**
- すべてにおいて「最高」のおもてなし
- 食材・器・空間すべてにこだわり
- 夫婦の大切な記念日を特別に演出

---

## 第4章：結婚記念日を「もっと特別」にする過ごし方

### 4-1. 記念日サプライズのアイデア

温泉旅行そのものが素敵なプレゼントですが、ちょっとした工夫で、さらに思い出深い一日になります。

**サプライズアイデア：**

#### 1. ケーキや花束を事前に手配
多くの旅館では、事前にお願いすれば記念日ケーキや花束を用意してくれます。夕食後にサプライズで登場させれば、感動間違いなし。

#### 2. 手紙を書いて渡す

![手紙を書くシーン]({img_A09_letter})

普段は照れくさくて言えない感謝の気持ち。手紙にして渡せば、きっと一生の宝物になります。

#### 3. 「思い出の写真」をアルバムに

![記念日のサプライズ演出]({img_A04_surprise})

スマホに眠っている夫婦の写真をアルバムにまとめて、旅先で一緒に見返す——これだけで会話が弾みます。

### 4-2. 「結婚○周年」の数え方と、各記念日の意味

結婚記念日には、年数ごとに名前がついているのをご存じですか？

| 年数 | 記念日名 | 意味・由来 |
|------|----------|------------|
| 1年 | 紙婚式 | まだ白紙のようにこれから描いていく |
| 5年 | 木婚式 | 木のように根を張り始めた |
| 10年 | 錫婚式（アルミ婚式） | 錫のように美しく、柔軟に |
| 15年 | 水晶婚式 | 透明で曇りのない信頼 |
| 20年 | 磁器婚式 | 年月をかけて価値が増す |
| 25年 | 銀婚式 | いぶし銀の深い味わい |
| 30年 | 真珠婚式 | 富と健康の象徴 |
| 40年 | ルビー婚式 | 深紅の情熱 |
| 50年 | 金婚式 | 金色に輝く尊い絆 |

「今年は○婚式だね」と話すだけでも、記念日に特別な意味が生まれます。

### 4-3. 旅行中に「ふたりの未来」について話してみる

非日常の空間は、普段話しにくいことを話すのにも最適です。

- 「5年後、どんな風になっていたい？」
- 「いつか行ってみたい場所は？」
- 「これからも続けていきたいことは？」

こうした会話は、夫婦の絆を深めるきっかけになります。

---

## 第5章：忙しい夫婦のための「予約から当日まで」完全ガイド

![週末旅行に出発する夫婦]({img_A07_departure})

### 5-1. いつ予約すべき？

**結論：人気の宿は2〜3ヶ月前がベスト**

特に土日や連休の露天風呂付き客室は、早めに埋まってしまいます。記念日の日程が決まったら、早めの予約をおすすめします。

**予約タイミングの目安：**
- 人気宿・繁忙期：2〜3ヶ月前
- 平日・オフシーズン：1ヶ月前でもOK
- 直前割引狙い：1週間前〜当日（運次第）

### 5-2. 子どもの預け先は早めに確保

![子連れでも楽しめる温泉旅行]({img_A03_kodure})

小さなお子さんがいるご家庭では、預け先の確保が最大の関門かもしれません。

**預け先のアイデア：**
- 祖父母にお願いする
- 一時保育サービスを利用する
- 信頼できるママ友と「預け合い」する

「子どもを預けてまで…」と罪悪感を感じる方もいるかもしれません。でも、**夫婦が仲良しでいることは、子どもにとっても幸せなこと**。たまには自分たちを優先しても、きっと大丈夫です。

### 5-3. 持ち物チェックリスト

温泉旅行の持ち物は、意外とシンプル。多くの旅館ではアメニティが充実しているので、最低限で大丈夫です。

**基本の持ち物：**
- [ ] 着替え（下着、部屋着用の服）
- [ ] スキンケア用品（こだわりがあれば）
- [ ] スマホ・充電器
- [ ] 財布・保険証
- [ ] 記念日用のプレゼント（あれば）

**あると便利なもの：**
- [ ] 本や雑誌（デジタルデトックスのお供に）
- [ ] カメラ（スマホでOK）
- [ ] 薄手の羽織（館内移動用）

---

## 第6章：よくある質問（Q&A）

### Q1. 露天風呂付き客室って、本当に必要？

**A. 夫婦の記念日なら、強くおすすめします。**

大浴場も素晴らしいのですが、「ふたりでゆっくり」を実現するなら、やはりプライベートな露天風呂がベスト。時間を気にせず、会話を楽しみながら湯浴みできるのは、露天風呂付き客室ならではの魅力です。

### Q2. 1泊だけでも満足できる？

![朝風呂を楽しむ風景]({img_A08_asaburo})

**A. はい、十分満足できます。**

「2泊しないと意味がない」なんてことはありません。1泊でも、チェックインから翌朝のチェックアウトまで、たっぷり18時間以上。温泉と食事を堪能し、ゆっくり眠るには十分な時間です。

### Q3. 記念日に旅行に行く余裕がない場合は？

**A. 「近場の日帰り温泉」でもOK。**

1泊旅行が難しければ、近場の日帰り温泉という選択肢もあります。最近は、個室休憩付きや貸切風呂のある日帰りプランも充実しています。

### Q4. 旅行嫌いのパートナーを誘うコツは？

**A. 「行きたい」ではなく「連れて行ってほしい」と伝える。**

「○○温泉に行きたいんだけど」より、「結婚記念日に、あなたと温泉に行きたい。連れて行ってほしい」と伝える方が、相手も嬉しいはず。主語を「ふたり」にすることがポイントです。

---

## おわりに：結婚記念日は「夫婦のメンテナンス日」

![温泉旅行を楽しむ夫婦]({img_A10_outro})

車は定期的にオイル交換をしないと、調子が悪くなります。
庭の木は、剪定をしないと、形が崩れてしまいます。

**夫婦関係も、同じかもしれません。**

忙しい毎日の中で、いつの間にか「家族」としての関係ばかりが前面に出て、「恋人」としての関係が薄れていく——そんな経験、ありませんか？

結婚記念日の温泉旅行は、**夫婦関係のメンテナンス日**。

年に一度、ふたりだけの時間を取って、改めて「一緒にいられてよかった」と感じる。そんな時間が、また次の一年を支える力になります。

今年の結婚記念日、温泉旅行を計画してみませんか？

きっと、最高の思い出になるはずです。

---

## 関連記事

温泉地別の詳しい情報は、こちらからご覧ください。

- [箱根の露天風呂付き客室｜おすすめ宿厳選](/kanto/hakone)
- [熱海の露天風呂付き客室｜おすすめ宿厳選](/kanto/atami)
- [伊豆の露天風呂付き客室｜おすすめ宿厳選](/kanto/izu)
- [有馬温泉の露天風呂付き客室｜おすすめ宿厳選](/kinki/arima)
- [城崎温泉の露天風呂付き客室｜おすすめ宿厳選](/kinki/kinosaki)
- [由布院の露天風呂付き客室｜おすすめ宿厳選](/kyushu/yufuin)
- [黒川温泉の露天風呂付き客室｜おすすめ宿厳選](/kyushu/kurokawa)

---

## この記事の監修者

<div class="supervisors-section" style="display:flex; flex-direction:column; gap:24px; margin:30px 0;">

<div class="supervisor-card" style="display:flex; gap:16px; padding:20px; background:#fafafa; border-radius:12px; border-left:4px solid #667eea;">
<img src="{img_author_fujiwara}" alt="藤原 美湯" style="width:80px; height:80px; border-radius:50%; object-fit:cover; flex-shrink:0;">
<div>
<h4 style="margin:0 0 4px 0; font-size:1.1em; color:#333;">藤原 美湯（ふじわら みゆ）</h4>
<p style="margin:0 0 8px 0; font-size:0.9em; color:#667eea; font-weight:500;">温泉ソムリエマスター / 温泉観光士</p>
<p style="margin:0 0 8px 0; font-size:0.9em; color:#555; line-height:1.6;">群馬県草津町の温泉旅館に生まれ、幼少期から温泉に親しむ。温泉ソムリエマスター取得後、全国500箇所以上の温泉地を訪問。泉質と健康効果の専門家として、メディア出演・執筆活動を行う。</p>
<p style="margin:0; font-size:0.85em; color:#888; font-style:italic;">「温泉は日本が誇る天然の薬湯。正しい知識で、もっと健康に美しく」</p>
</div>
</div>

<div class="supervisor-card" style="display:flex; gap:16px; padding:20px; background:#fafafa; border-radius:12px; border-left:4px solid #667eea;">
<img src="{img_author_tanaka}" alt="田中 誠一" style="width:80px; height:80px; border-radius:50%; object-fit:cover; flex-shrink:0;">
<div>
<h4 style="margin:0 0 4px 0; font-size:1.1em; color:#333;">田中 誠一（たなか せいいち）</h4>
<p style="margin:0 0 8px 0; font-size:0.9em; color:#667eea; font-weight:500;">大手旅行会社 国内旅行事業部 シニアマネージャー</p>
<p style="margin:0 0 8px 0; font-size:0.9em; color:#555; line-height:1.6;">旅行業界30年以上のキャリアを持ち、記念日旅行・シニア向け旅行の企画を得意とする。年間3,000組以上の夫婦旅行をプロデュースし、きめ細やかな提案力で高いリピート率を誇る。</p>
<p style="margin:0; font-size:0.85em; color:#888; font-style:italic;">「旅は人生を豊かにする投資。大切な記念日を最高の思い出に」</p>
</div>
</div>

<div class="supervisor-card" style="display:flex; gap:16px; padding:20px; background:#fafafa; border-radius:12px; border-left:4px solid #667eea;">
<img src="{img_author_kobayashi}" alt="小林 香織" style="width:80px; height:80px; border-radius:50%; object-fit:cover; flex-shrink:0;">
<div>
<h4 style="margin:0 0 4px 0; font-size:1.1em; color:#333;">小林 香織（こばやし かおり）</h4>
<p style="margin:0 0 8px 0; font-size:0.9em; color:#667eea; font-weight:500;">トラベルライター / 元旅行情報誌編集長</p>
<p style="margin:0 0 8px 0; font-size:0.9em; color:#555; line-height:1.6;">大手出版社で旅行情報誌の編集長を務めた後、独立。年間100軒以上の宿に宿泊取材し、女性ならではの視点で旅の魅力を伝える。自身も結婚25年、毎年の記念日温泉旅行が夫婦円満の秘訣。</p>
<p style="margin:0; font-size:0.85em; color:#888; font-style:italic;">「良い旅は、良い情報から。『行ってみたい』を『行ってよかった』に」</p>
</div>
</div>

</div>

---

【メタディスクリプション】
結婚記念日に温泉旅行を計画中の30〜50代夫婦へ。露天風呂付き客室の選び方、おすすめ温泉地、予算別プラン、サプライズアイデアまで完全ガイド。忙しい毎日だからこそ、ふたりだけの特別な時間を。
"""


# =====================================================
# 結婚記念日温泉ガイド - シニア世代向け (60代以上)
# =====================================================

GUIDE_SENIORS = """# 60代からの結婚記念日温泉旅行｜ゆとりある時間を楽しむ大人の宿選びと過ごし方

## はじめに：人生の節目を、ふたりで祝う喜び

![ゆったりと温泉を楽しむシニア夫婦]({img_B01_main})

子育てを終え、仕事も一段落。
60代からの人生は、まさに「自分たちのための時間」が戻ってくる季節です。

**結婚30年、40年、そして金婚式——**

長い年月を共に歩んできた夫婦だからこそ、記念日には特別な意味があります。

「若い頃のように、旅行なんて疲れるだけ…」
そんな風に思っていませんか？

でも実は、**60代からの温泉旅行には、若い頃とは違う深い味わい**があります。

- 時間を気にせず、ゆっくりと湯に浸かる贅沢
- 「おいしいね」と何度でも言い合える、穏やかな食事の時間
- 静かな部屋で、昔話に花を咲かせる夜

この記事では、**60代以上のご夫婦が、心から安らげる結婚記念日の温泉旅行**をご提案します。

---

## 第1章：60代からの温泉旅行は「量より質」

### 1-1. たくさん回るより、一つの宿でゆっくりと

若い頃の旅行は、「あそこも行きたい、ここも見たい」と欲張りがちでした。

でも、60代からの旅行は違います。

**一つの宿にじっくり滞在して、時間を贅沢に使う——**

これこそが、人生経験を重ねた大人の旅の醍醐味です。

チェックインしてから、チェックアウトまで。
宿の中だけで完結する、**「動かない贅沢」**を楽しんでみませんか。

### 1-2. 露天風呂付き客室という「正解」

60代以上のご夫婦に、露天風呂付き客室を強くおすすめする理由があります。

**理由1：好きな時間に入れる**
大浴場だと、混雑する時間帯を避けたり、長湯を遠慮したりしがち。客室露天風呂なら、朝でも夜中でも、好きなだけ温泉を楽しめます。

**理由2：足腰の負担が少ない**
大浴場への往復がないので、体への負担が軽減されます。特に膝や腰に不安がある方には、この違いは大きいものです。

**理由3：ふたりだけの時間が守られる**
長年連れ添った夫婦だからこそ、わざわざ言葉にしなくても通じ合える時間。その静かな幸せを、誰にも邪魔されずに味わえます。

### 1-3. 「バリアフリー」という安心

![バリアフリー対応の客室]({img_B03_barrierfree})

60代以降の旅行では、**宿のバリアフリー対応**も大切なポイントです。

**チェックしたい項目：**
- 段差の少ない館内設計
- 手すりの設置（お風呂、トイレ、廊下）
- エレベーターの有無
- 客室内の段差
- 貸出用の杖や車椅子

予約時に「足腰に少し不安があるのですが…」と伝えれば、多くの宿が対応してくれます。遠慮せずに相談してみてください。

---

## 第2章：シニア夫婦におすすめの温泉地

![温泉街をゆっくり散歩するシニア夫婦]({img_B06_sanpo})

「あまり遠くまで行くのは疲れる」
「でも、せっかくなら良い温泉地に行きたい」

そんな60代以上のご夫婦に、**アクセスが良く、かつ上質な温泉地**をご紹介します。

### 2-1. 関東近郊のおすすめ温泉地

#### 箱根（神奈川県）
**東京から約1時間30分。日本を代表する温泉リゾート**

箱根は、交通の便が良く、シニア世代の旅行にぴったり。ロマンスカーを使えば、座ったまま旅館の最寄り駅まで行けます。

**箱根がシニアにおすすめの理由：**
- 新宿からロマンスカーで1本
- バリアフリー対応の宿が充実
- 美術館巡りなど、歩かなくても楽しめる観光

[箱根の露天風呂付き客室を探す →](/kanto/hakone)

#### 熱海（静岡県）
**新幹線で35分。海を望む温泉リゾート**

熱海は、東京駅から新幹線「こだま」でわずか35分。日帰りでも行ける近さですが、ぜひ1泊して、海を眺めながらゆっくり過ごしてほしい温泉地です。

**熱海がシニアにおすすめの理由：**
- 東京から新幹線で35分
- 海を望む絶景の宿が多い
- 温泉街の散策は平坦な道が多い

[熱海の露天風呂付き客室を探す →](/kanto/atami)

#### 伊香保温泉（群馬県）
**石段街の情緒と、名湯「黄金の湯」**

伊香保温泉は、365段の石段街で有名な温泉地。ただし、石段を登るのが大変な場合は、石段から離れた静かな宿を選ぶのがおすすめです。

**伊香保がシニアにおすすめの理由：**
- 「黄金の湯」は体がよく温まる
- 石段を避ければ、静かに過ごせる宿多数
- 水沢うどんなど、名物料理も楽しめる

[伊香保温泉の露天風呂付き客室を探す →](/kanto/ikaho)

### 2-2. 関西近郊のおすすめ温泉地

#### 有馬温泉（兵庫県）
**日本最古の温泉。大阪・神戸から1時間以内**

有馬温泉は、太閤秀吉も愛したという歴史ある温泉地。大阪や神戸からのアクセスが良く、関西在住のシニア夫婦には特におすすめです。

**有馬がシニアにおすすめの理由：**
- 大阪から電車で約1時間
- 「金泉」は保温効果が高く、冷え性に◎
- 温泉街はコンパクトで歩きやすい

[有馬温泉の露天風呂付き客室を探す →](/kinki/arima)

#### 南紀白浜（和歌山県）
**白い砂浜と、開放的な露天風呂**

南紀白浜は、関西の「リゾート温泉地」。海を望む開放的な露天風呂と、新鮮な海の幸が魅力です。

**南紀白浜がシニアにおすすめの理由：**
- 大阪から特急で約2時間
- 海沿いの絶景露天風呂
- クエなど、地元の美味しい魚介

[南紀白浜の露天風呂付き客室を探す →](/kinki/shirahama)

### 2-3. 特別な記念日にふさわしい名湯

#### 下呂温泉（岐阜県）
**日本三名泉の一つ。とろりとした美肌の湯**

下呂温泉は、草津・有馬と並ぶ「日本三名泉」の一つ。アルカリ性単純泉のお湯は、肌をすべすべにしてくれます。

**下呂がシニアにおすすめの理由：**
- 名古屋から特急で約1時間30分
- 肌に優しい「美肌の湯」
- 温泉街の規模がちょうどよい

[下呂温泉の露天風呂付き客室を探す →](/chubu/gero)

#### 別府温泉（大分県）
**日本一の湧出量。多彩な泉質を楽しむ**

別府は、日本一の温泉湧出量を誇る温泉都市。「地獄めぐり」で有名ですが、宿でゆっくり過ごすだけでも十分に楽しめます。

**別府がシニアにおすすめの理由：**
- 福岡から特急で約2時間
- 泉質の異なる温泉を楽しめる
- 地獄蒸しプリンなど、名物スイーツも

[別府温泉の露天風呂付き客室を探す →](/kyushu/beppu)

---

## 第3章：シニア夫婦のための宿選びのポイント

### 3-1. 「食事」で選ぶ

![健康的な朝食を楽しむ]({img_B05_breakfast})

60代以上になると、若い頃のように「量」は食べられなくなるもの。でも、「質」へのこだわりは、むしろ高まっているのではないでしょうか。

**宿選びで確認したいポイント：**

#### 量より質のプランがあるか
「少量美味」「量控えめプラン」など、品数を抑えて質を高めたプランを用意している宿が増えています。

#### 部屋食または個室食事処か
大きな食事会場での食事は、周囲が気になって落ち着かないことも。部屋食や個室の食事処なら、ふたりのペースでゆっくり食事を楽しめます。

#### アレルギーや苦手な食材への対応
「生ものが苦手」「甲殻類アレルギーがある」など、事前に伝えておけば対応してくれる宿がほとんどです。

### 3-2. 「客室」で選ぶ

露天風呂付き客室といっても、さまざまなタイプがあります。

**シニア夫婦におすすめの客室タイプ：**

#### 和洋室
ベッドで眠れる洋室と、くつろげる和室が一体になったタイプ。布団の上げ下ろしがないので、足腰への負担が少なくて済みます。

#### 段差の少ない客室
最近は、バリアフリーを意識した段差の少ない客室も増えています。予約時に確認してみましょう。

#### テラスや縁側のある客室
露天風呂に入らなくても、テラスや縁側で外の空気を感じられる客室は、気持ちが良いものです。

### 3-3. 「サービス」で選ぶ

宿のサービスで、滞在の快適さは大きく変わります。

**シニア夫婦に嬉しいサービス：**

#### 送迎サービス
駅や空港からの送迎があると、荷物を持っての移動が楽になります。

#### 荷物の事前配送
大きな荷物は事前に宿へ送っておけば、身軽に旅行できます。

#### 記念日のお祝い対応
結婚記念日の旨を伝えると、ケーキや花束、記念写真など、さまざまなサービスを用意してくれる宿も多くあります。

---

## 第4章：結婚記念日を「忘れられない一日」にするアイデア

### 4-1. 節目の記念日の過ごし方

![還暦祝いの温泉旅行]({img_B09_kanreki})

長年連れ添った夫婦だからこそ、節目の記念日は特別に祝いたいもの。

**銀婚式（結婚25周年）の過ごし方**
銀婚式は「夫婦として四半世紀」という大きな節目。少し奮発して、憧れの高級旅館を予約してみてはいかがでしょう。

**真珠婚式（結婚30周年）の過ごし方**
真珠は「健康と富の象徴」。お互いの健康に感謝しつつ、真珠のように輝く海を望む温泉地を選んでみては。

**ルビー婚式（結婚40周年）の過ごし方**
40年という歳月を共に歩んできた、深い絆。普段は照れくさくて言えない感謝の言葉を、この日だけは伝えてみましょう。

**金婚式（結婚50周年）の過ごし方**

![金婚式のお祝い]({img_B02_kinkon})

金婚式は、文字通り「金色に輝く」特別な記念日。家族を招いてのお祝いも素敵ですが、まずは夫婦ふたりで静かにお祝いするのも良いものです。

### 4-2. 「昔の写真」を持っていく

温泉旅行に、**若い頃の写真**を持っていくことをおすすめします。

- 結婚式の写真
- 新婚旅行の写真
- 子どもが小さかった頃の写真

部屋でくつろぎながら、「こんな時代もあったね」「あの頃は大変だったね」と振り返る時間。それは、長年連れ添った夫婦だけが味わえる、かけがえのないひとときです。

### 4-3. 「これからの夢」を語り合う

![三世代で楽しむ温泉旅行]({img_B07_sansedai})

60代からの人生は、「第二の人生」とも言われます。

温泉に浸かりながら、これからの夢を語り合ってみませんか。

- いつか行ってみたい場所
- 挑戦してみたい趣味
- 孫との思い出づくり
- ふたりで続けていきたいこと

未来を語ることは、心を若く保つ秘訣でもあります。

---

## 第5章：シニア夫婦の旅行「準備編」

### 5-1. 無理のないスケジュールを組む

![連泊を楽しむシニア夫婦]({img_B04_renpaku})

若い頃のような「朝から晩まで動き回る」スケジュールは禁物。**余裕を持ったスケジュール**を心がけましょう。

**おすすめのスケジュール例：**

**1日目**
- 午後にチェックイン（早すぎると疲れる）
- 到着後は部屋でひと休み
- 夕方に温泉
- 夕食
- 就寝

**2日目**
- 朝風呂を楽しむ
- 朝食
- 部屋でゆっくり
- 11時頃にチェックアウト
- 帰宅（または途中で軽い観光）

「何もしない」ことを恐れず、ゆったりと過ごすのがコツです。

### 5-2. 体調管理のポイント

![療養・健康目的の入浴を楽しむ]({img_B08_health})

温泉旅行を楽しむために、**体調管理**も大切です。

**旅行前**
- 睡眠をしっかり取る
- 持病の薬を忘れずに準備
- 保険証のコピーを持参

**温泉の入り方**
- 入浴前後に水分補給
- 長湯しすぎない（1回15分程度）
- 食後すぐの入浴は避ける
- 立ちくらみに注意（ゆっくり立ち上がる）

**旅行中**
- 無理をしない
- 疲れたら休む
- お酒は控えめに

### 5-3. 持ち物チェックリスト

**必需品：**
- [ ] 常備薬・処方薬
- [ ] 保険証（コピーでも可）
- [ ] 眼鏡・老眼鏡
- [ ] 着替え
- [ ] スマートフォン・充電器

**あると便利なもの：**
- [ ] 羽織もの（館内は冷えることも）
- [ ] 歩きやすい靴（散策用）
- [ ] 折りたたみ傘
- [ ] 本や雑誌
- [ ] 昔の写真（会話のきっかけに）

---

## 第6章：よくある質問（Q&A）

### Q1. 足腰に不安があるのですが、温泉旅行は難しいでしょうか？

**A. バリアフリー対応の宿を選べば、十分楽しめます。**

最近は、段差のない客室、手すり付きのお風呂、車椅子対応など、バリアフリー設備を整えた宿が増えています。予約時に「足腰に不安がある」と伝えれば、適した客室を案内してもらえます。

### Q2. 夫婦で旅行するのは久しぶりで、何を話していいかわかりません。

**A. 「昔の写真」と「これからの夢」が会話のきっかけになります。**

長年連れ添っていると、日常会話はあっても、深い話をする機会は減りがちです。昔の写真を見ながら思い出話をしたり、「これからやりたいこと」を語り合ったりすれば、自然と会話が弾みます。

### Q3. 記念日のサプライズをしたいのですが、どうすればいいですか？

**A. 宿に事前相談するのが確実です。**

多くの旅館では、記念日のケーキ手配、花束の用意、記念写真の撮影など、さまざまなサービスを用意しています。予約時に「結婚○周年のお祝いで伺います」と伝えれば、相談に乗ってもらえます。

### Q4. 体力的に1泊が限界なのですが、それでも楽しめますか？

**A. もちろんです。1泊でも十分に楽しめます。**

1泊2日でも、チェックインからチェックアウトまで約18時間。温泉に2〜3回入り、美味しい夕食と朝食を楽しみ、ゆっくり眠る——これだけで、心身ともにリフレッシュできます。

---

## おわりに：「ありがとう」を伝える旅

![温泉旅行を楽しむシニア夫婦]({img_B10_outro})

60代、70代——
長い人生を共に歩んできた夫婦には、言葉にしなくても通じ合える絆があります。

でも、だからこそ。
**たまには、言葉にして伝えてみませんか。**

「一緒にいてくれて、ありがとう」
「これからも、よろしくね」

温泉旅行は、そんな言葉を交わすのにぴったりの機会です。

静かな露天風呂で、ふたりで湯に浸かりながら。
美味しい食事を前に、「おいしいね」と笑い合いながら。
布団に入る前に、そっと手を重ねながら。

長年の感謝を伝え合う——
それが、何よりの記念日の過ごし方なのかもしれません。

**今年の結婚記念日、温泉旅行で「ありがとう」を伝えてみませんか？**

---

## 関連記事

温泉地別の詳しい情報は、こちらからご覧ください。

- [箱根の露天風呂付き客室｜おすすめ宿厳選](/kanto/hakone)
- [熱海の露天風呂付き客室｜おすすめ宿厳選](/kanto/atami)
- [伊香保温泉の露天風呂付き客室｜おすすめ宿厳選](/kanto/ikaho)
- [有馬温泉の露天風呂付き客室｜おすすめ宿厳選](/kinki/arima)
- [南紀白浜の露天風呂付き客室｜おすすめ宿厳選](/kinki/shirahama)
- [下呂温泉の露天風呂付き客室｜おすすめ宿厳選](/chubu/gero)
- [別府温泉の露天風呂付き客室｜おすすめ宿厳選](/kyushu/beppu)

---

【メタディスクリプション】
60代からの結婚記念日温泉旅行ガイド。銀婚式・金婚式にふさわしい宿の選び方、シニア夫婦におすすめの温泉地、バリアフリー対応のポイント、旅行準備のコツまで。ゆとりある時間を楽しむ大人の旅を。
"""


# =====================================================
# 画像挿入位置の設定
# =====================================================

# A: 働いている世代向け（30-50代）の画像設定
# Cloudflare R2の実際のファイル名
IMAGES_WORKING_COUPLES = {
    "img_A01_main": "A01_main_visual.png",           # A-1. メインビジュアル
    "img_A02_rotenburo": "A02_private_rotenburo.png", # A-2. 露天風呂付き客室
    "img_A03_kodure": "A03_family_trip.png",          # A-3. 子連れ温泉旅行
    "img_A04_surprise": "A04_anniversary_surprise.png", # A-4. サプライズ演出
    "img_A05_dinner": "A05_kaiseki_dinner.png",       # A-5. 記念日ディナー
    "img_A06_sanpo": "A06_onsen_town_walk.png",       # A-6. 温泉街散策
    "img_A07_departure": "A07_train_departure.png",   # A-7. 週末旅行の出発
    "img_A08_asaburo": "A08_morning_bath.png",        # A-8. 朝風呂の風景
    "img_A09_letter": "A09_writing_letter.png",       # A-9. 手紙を書くシーン
    "img_A10_outro": "A10_couple_back_view.png",      # A-10. 記事締めくくり
}

# 監修者画像（両記事共通）
# onsen-images/authors/ に保存（ファイル名にスペースあり）
IMAGES_AUTHORS = {
    "img_author_fujiwara": "miyu fujiwara.webp",     # 藤原 美湯
    "img_author_tanaka": "seiichi tanaka.webp",      # 田中 誠一
    "img_author_kobayashi": "kaori kobayashi.webp",  # 小林 香織
}

# B: シニア世代向け（60代以上）の画像設定
# Cloudflare R2の実際のファイル名
IMAGES_SENIORS = {
    "img_B01_main": "B01_main_visual_senior.webp",    # B-1. メインビジュアル
    "img_B02_kinkon": "B02_golden_anniversary.webp",  # B-2. 金婚式のお祝い
    "img_B03_barrierfree": "B03_accessible_room.webp", # B-3. バリアフリー対応の客室
    "img_B04_renpaku": "B04_leisurely_reading.webp",  # B-4. 連泊を楽しむシニア夫婦
    "img_B05_breakfast": "B05_healthy_breakfast.webp", # B-5. 健康的な朝食
    "img_B06_sanpo": "B06_slow_walk.webp",            # B-6. 温泉街をゆっくり散歩
    "img_B07_sansedai": "B07_three_generations.webp",  # B-7. 三世代旅行
    "img_B08_health": "B08_therapeutic_bath.webp",   # B-8. 療養・健康目的の入浴
    "img_B09_kanreki": "B09_kanreki_celebration.webp", # B-9. 還暦祝い
    "img_B10_outro": "B10_sunset_elderly.webp",      # B-10. 記事締めくくり
}


def build_image_url(filename: str) -> str:
    """Cloudflare R2の画像URLを構築（記事画像用）"""
    # パス内のスペースをURLエンコード
    encoded_path = IMAGE_PATH.replace(' ', '%20')
    return f"{CLOUDFLARE_BASE_URL}/{encoded_path}/{filename}"


def build_author_image_url(filename: str) -> str:
    """Cloudflare R2の監修者画像URLを構築"""
    # スペースをURLエンコード
    encoded_filename = filename.replace(' ', '%20')
    return f"{CLOUDFLARE_BASE_URL}/onsen-images/authors/{encoded_filename}"


def apply_images_to_content(content: str, images: dict) -> str:
    """コンテンツに画像URLを適用"""
    for placeholder, filename in images.items():
        image_url = build_image_url(filename)
        # マークダウン形式の画像プレースホルダーを実際のURLに置換
        content = content.replace(f"{{{placeholder}}}", image_url)
    return content


def apply_author_images(content: str) -> str:
    """コンテンツに監修者画像URLを適用"""
    for placeholder, filename in IMAGES_AUTHORS.items():
        image_url = build_author_image_url(filename)
        content = content.replace(f"{{{placeholder}}}", image_url)
    return content


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='ピラーコンテンツ挿入スクリプト')
    parser.add_argument('--type', choices=['working', 'seniors', 'both'],
                        default='both', help='挿入するコンテンツタイプ')
    parser.add_argument('--dry-run', action='store_true',
                        help='実際には挿入せず、内容を確認')
    parser.add_argument('--with-images', action='store_true',
                        help='画像URLを適用する')
    parser.add_argument('--update', action='store_true',
                        help='既存のレコードを更新する')

    args = parser.parse_args()

    inserter = PillarContentInserter()

    if not args.dry_run:
        inserter.connect()

    try:
        results = []

        # 働いている世代向けガイド
        if args.type in ['working', 'both']:
            content = GUIDE_WORKING_COUPLES
            if args.with_images:
                content = apply_images_to_content(content, IMAGES_WORKING_COUPLES)
                content = apply_author_images(content)

            if args.dry_run:
                print("=" * 60)
                print("【働いている世代向けガイド】")
                print("=" * 60)
                print(f"URL: /guides/wedding-anniversary-working-couples")
                print(f"文字数: {len(content)}")
                print("-" * 60)
                print(content[:1000] + "...")
            else:
                if args.update:
                    result = inserter.update_pillar_page(
                        url_slug='guides/wedding-anniversary-working-couples',
                        page_title='結婚記念日は温泉旅行で特別な時間を｜忙しい30〜50代夫婦のための完全ガイド',
                        content=content,
                        meta_description='結婚記念日に温泉旅行を計画中の30〜50代夫婦へ。露天風呂付き客室の選び方、おすすめ温泉地、予算別プラン、サプライズアイデアまで完全ガイド。',
                        hero_image_url=build_image_url('A01_main_visual.png') if args.with_images else None
                    )
                    results.append(('working', result))
                    print(f"✅ 働いている世代向けガイドを更新しました: {result}")
                else:
                    result = inserter.insert_pillar_page(
                        url_slug='guides/wedding-anniversary-working-couples',
                        page_title='結婚記念日は温泉旅行で特別な時間を｜忙しい30〜50代夫婦のための完全ガイド',
                        content=content,
                        meta_description='結婚記念日に温泉旅行を計画中の30〜50代夫婦へ。露天風呂付き客室の選び方、おすすめ温泉地、予算別プラン、サプライズアイデアまで完全ガイド。',
                        hero_image_url=build_image_url('A01_main_visual.png') if args.with_images else None
                    )
                    results.append(('working', result))
                    print(f"✅ 働いている世代向けガイドを挿入しました: {result}")

        # シニア世代向けガイド
        if args.type in ['seniors', 'both']:
            content = GUIDE_SENIORS
            if args.with_images:
                content = apply_images_to_content(content, IMAGES_SENIORS)
                content = apply_author_images(content)

            if args.dry_run:
                print("\n" + "=" * 60)
                print("【シニア世代向けガイド】")
                print("=" * 60)
                print(f"URL: /guides/wedding-anniversary-seniors")
                print(f"文字数: {len(content)}")
                print("-" * 60)
                print(content[:1000] + "...")
            else:
                if args.update:
                    result = inserter.update_pillar_page(
                        url_slug='guides/wedding-anniversary-seniors',
                        page_title='60代からの結婚記念日温泉旅行｜ゆとりある時間を楽しむ大人の宿選びと過ごし方',
                        content=content,
                        meta_description='60代からの結婚記念日温泉旅行ガイド。銀婚式・金婚式にふさわしい宿の選び方、シニア夫婦におすすめの温泉地、バリアフリー対応のポイントまで。',
                        hero_image_url=build_image_url('B01_main_visual_senior.webp') if args.with_images else None
                    )
                    results.append(('seniors', result))
                    print(f"✅ シニア世代向けガイドを更新しました: {result}")
                else:
                    result = inserter.insert_pillar_page(
                        url_slug='guides/wedding-anniversary-seniors',
                        page_title='60代からの結婚記念日温泉旅行｜ゆとりある時間を楽しむ大人の宿選びと過ごし方',
                        content=content,
                        meta_description='60代からの結婚記念日温泉旅行ガイド。銀婚式・金婚式にふさわしい宿の選び方、シニア夫婦におすすめの温泉地、バリアフリー対応のポイントまで。',
                        hero_image_url=build_image_url('B01_main_visual_senior.webp') if args.with_images else None
                    )
                    results.append(('seniors', result))
                    print(f"✅ シニア世代向けガイドを挿入しました: {result}")

        if not args.dry_run and results:
            print("\n" + "=" * 60)
            action = "更新" if args.update else "挿入"
            print(f"{action}完了")
            print("=" * 60)
            for content_type, result in results:
                slug = result['url_slug']
                print(f"🔗 https://www.premium-travel-japan.com{slug}")

    finally:
        if not args.dry_run:
            inserter.close()


if __name__ == '__main__':
    main()
