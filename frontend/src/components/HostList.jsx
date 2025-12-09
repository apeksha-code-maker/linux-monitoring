import React from "react";
import HostCard from "./HostCard";

export default function HostList({ hosts, onSelect }) {
  return (
    <div className="col-span-1">
      <h2 className="text-xl font-semibold mb-3">Hosts</h2>
      <div className="flex flex-col gap-2">
        {hosts.map((h) => (
          <HostCard
            key={h.hostname}
            hostname={h.hostname}
            lastSeen={h.last_seen}
            onClick={() => onSelect(h.hostname)}
          />
        ))}
      </div>
    </div>
  );
}
