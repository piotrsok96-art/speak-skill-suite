import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from "recharts";

export interface SkillPoint {
  axis: string;
  value: number;
}

export function SkillRadar({ data }: { data: SkillPoint[] }) {
  return (
    <div className="rounded-xl border bg-card p-5">
      <h3 className="text-sm font-semibold mb-2">Radar umiejętności</h3>
      <div className="w-full h-64">
        <ResponsiveContainer>
          <RadarChart data={data} outerRadius="75%">
            <PolarGrid stroke="hsl(var(--border))" />
            <PolarAngleAxis dataKey="axis" tick={{ fontSize: 11 }} />
            <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
            <Radar
              dataKey="value"
              stroke="hsl(var(--primary))"
              fill="hsl(var(--primary))"
              fillOpacity={0.35}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
