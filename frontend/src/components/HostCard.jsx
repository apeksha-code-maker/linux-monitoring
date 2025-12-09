import React from "react";

export default function HostCard({ hostname, lastSeen, onClick }) {
  return (
    <div
      onClick={onClick}
      className="p-3 bg-white shadow rounded cursor-pointer hover:bg-gray-100"
    >
      <p className="text-lg font-medium">{hostname}</p>
      <p className="text-sm text-gray-600">{lastSeen}</p>
    </div>
  );
}
