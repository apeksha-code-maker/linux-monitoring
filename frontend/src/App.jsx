import React, { useEffect, useState } from "react";
import HostList from "./components/HostList";
import HostDetails from "./components/HostDetails";

export default function App() {
  const [hosts, setHosts] = useState([]);
  const [selectedHost, setSelectedHost] = useState(null);

  async function fetchHosts() {
    const res = await fetch("http://localhost:5000/hosts");
    const data = await res.json();
    setHosts(data);
  }

  useEffect(() => {
    fetchHosts();
    const timer = setInterval(fetchHosts, 10000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6 text-center">
        Linux Monitoring Dashboard
      </h1>

      <div className="grid grid-cols-3 gap-4">
        <HostList hosts={hosts} onSelect={setSelectedHost} />
        {selectedHost && <HostDetails hostname={selectedHost} />}
      </div>
    </div>
  );
}
