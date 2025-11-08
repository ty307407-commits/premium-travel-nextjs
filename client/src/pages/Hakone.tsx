import { trpc } from "@/lib/trpc";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, MapPin, Star } from "lucide-react";

export default function Hakone() {
  // Fetch hotels from Rakuten Travel API via tRPC
  const { data: hotels, isLoading, error } = trpc.rakuten.searchHotels.useQuery({
    regionName: "箱根",
    limit: 5,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-lg text-muted-foreground">箱根の宿を検索中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-destructive">エラーが発生しました</p>
          <p className="text-sm text-muted-foreground mt-2">{error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-primary/10 to-background py-16">
        <div className="container">
          <h1 className="text-4xl md:text-5xl font-bold text-center mb-4">
            箱根温泉の宿
          </h1>
          <p className="text-lg text-center text-muted-foreground max-w-2xl mx-auto">
            結婚5周年記念を迎える50代夫婦に向けた、箱根温泉の特別な宿選びをご紹介します。
          </p>
        </div>
      </section>

      {/* Hotels List */}
      <section className="py-12">
        <div className="container">
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {hotels?.map((hotel) => (
              <Card key={hotel.hotelNo} className="overflow-hidden hover:shadow-lg transition-shadow">
                {/* Hotel Image */}
                <div className="aspect-video relative overflow-hidden bg-muted">
                  <img
                    src={hotel.hotelImageUrl}
                    alt={hotel.hotelName}
                    className="object-cover w-full h-full"
                    loading="lazy"
                  />
                </div>

                <CardHeader>
                  <CardTitle className="text-xl">{hotel.hotelName}</CardTitle>
                  <CardDescription className="line-clamp-2">
                    {hotel.hotelSpecial}
                  </CardDescription>
                </CardHeader>

                <CardContent className="space-y-3">
                  {/* Rating */}
                  <div className="flex items-center gap-2">
                    <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    <span className="font-semibold">{hotel.reviewAverage}</span>
                    <span className="text-sm text-muted-foreground">
                      ({hotel.reviewCount}件)
                    </span>
                  </div>

                  {/* Location */}
                  <div className="flex items-start gap-2 text-sm">
                    <MapPin className="h-4 w-4 mt-0.5 text-muted-foreground flex-shrink-0" />
                    <span className="text-muted-foreground">
                      {hotel.address1}{hotel.address2}
                    </span>
                  </div>

                  {/* Price */}
                  <div className="pt-2">
                    <p className="text-2xl font-bold text-primary">
                      ¥{hotel.hotelMinCharge.toLocaleString()}
                      <span className="text-sm font-normal text-muted-foreground">〜</span>
                    </p>
                  </div>
                </CardContent>

                <CardFooter>
                  <Button asChild className="w-full">
                    <a
                      href={hotel.hotelInformationUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      楽天トラベルで詳細を見る
                    </a>
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <section className="py-12 bg-muted/50">
        <div className="container text-center">
          <p className="text-muted-foreground">
            箱根温泉で、ふたりだけの特別な時間をお過ごしください。
          </p>
        </div>
      </section>
    </div>
  );
}
