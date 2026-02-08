'use client';

import { Radar } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    RadialLinearScale,
    PointElement,
    LineElement,
    Filler,
    Tooltip,
    Legend,
} from 'chart.js';

ChartJS.register(
    RadialLinearScale,
    PointElement,
    LineElement,
    Filler,
    Tooltip,
    Legend
);

interface RadarChartProps {
    data: {
        atmosphere: number;
        cleanliness: number;
        onsen_quality: number; // 欠けている場合は0など適宜処理
        meals: number;
        hospitality: number;
    };
    hotelName?: string;
}

export const RadarChart = ({ data, hotelName }: RadarChartProps) => {
    // データ配列（必須5項目）
    // 順番: 雰囲気 -> 清潔感 -> 泉質 -> 食事 -> 接客 -> (戻る)
    const chartData = {
        labels: ['雰囲気', '清潔感', '泉質', '食事', '接客'],
        datasets: [
            {
                label: hotelName ? `${hotelName}の評価` : '評価',
                data: [
                    data.atmosphere || 0,
                    data.cleanliness || 0,
                    data.onsen_quality || 0,
                    data.meals || 0,
                    data.hospitality || 0,
                ],
                backgroundColor: 'rgba(32, 178, 170, 0.4)', // LightSeaGreen (心地よいTeal) #20B2AA
                borderColor: '#008080', // Teal (濃い緑青) #008080 - 視認性確保
                borderWidth: 2,
                pointBackgroundColor: '#fff',
                pointBorderColor: '#FF7F50', // Coral (珊瑚色) #FF7F50 - アクセント、楽しさ
                pointHoverBackgroundColor: '#FF7F50',
                pointHoverBorderColor: '#fff',
                pointRadius: 4, // ポイントを少し大きくして目立たせる
                fill: true,
            },
        ],
    };

    const options = {
        scales: {
            r: {
                angleLines: {
                    color: 'rgba(0, 0, 0, 0.1)', // 薄いグレー
                },
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)', // さらに薄いグレー
                },
                pointLabels: {
                    color: '#333', // 濃い文字色で見やすく
                    font: {
                        size: 14,
                        family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
                        weight: 500, //'bold'
                    },
                },
                ticks: {
                    display: false, // 数値は出さない（シンプルさ優先）
                    max: 5,
                    min: 0,
                    stepSize: 1,
                },
                suggestedMin: 0,
                suggestedMax: 5,
            },
        },
        plugins: {
            legend: {
                display: false, // タイトルで十分な場合は隠す
            },
            tooltip: {
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                titleColor: '#333',
                bodyColor: '#666',
                borderColor: '#ddd',
                borderWidth: 1,
                displayColors: false,
                callbacks: {
                    label: function (context: any) {
                        return context.raw + ' / 5.0';
                    }
                }
            }
        },
        maintainAspectRatio: false, // 親要素に合わせてリサイズ
    };

    return (
        <div className="w-full h-64 md:h-80 relative flex justify-center items-center">
            <Radar data={chartData} options={options} />
        </div>
    );
};
