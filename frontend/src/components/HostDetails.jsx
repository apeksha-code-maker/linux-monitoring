import React, { useEffect, useState } from "react";
import {
  LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip
} from "recharts";

export default function HostDetails({ hostname }) {
  const [history, setHistory] = useState([]);

  async function fetchHistory() {
    const res = await fetch(
      `http://localhost:5000/host/${hostname}/history?limit=50`
    );
    const data = await res.json();
    setHistory(data);
  }

  useEffect(() => {
    fetchHistory();
  }, [hostname]);

  return (
    <div className="col-span-2 p-4 bg-white shadow rounded">
      <h2 className="text-xl font-bold mb-4">Details for {hostname}</h2>

      <LineChart width={600} height={300} data={history}>
        <Line type="monotone" dataKey="cpu_percent" stroke="blue" />
        <CartesianGrid stroke="#ccc" />
        <XAxis dataKey="ts" hide />
        <YAxis />
        <Tooltip />
      </LineChart>
    </div>
  );
}
