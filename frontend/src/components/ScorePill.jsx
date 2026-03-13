import React from 'react';

const ScorePill = ({ score }) => {
  if (score === null || score === undefined) {
    return (
      <span className="px-3 py-1 rounded-full text-sm font-medium bg-[#F1EFE8] text-[#444441]">
        ...
      </span>
    );
  }

  let styles = "";
  if (score >= 8) {
    styles = "bg-[#E1F5EE] text-[#0F6E56]"; // green
  } else if (score >= 5) {
    styles = "bg-[#FAEEDA] text-[#854F0B]"; // amber
  } else {
    styles = "bg-[#FCEBEB] text-[#A32D2D]"; // red
  }

  return (
    <span className={`px-3 py-1 rounded-full text-sm font-medium ${styles}`}>
      {score}
    </span>
  );
};

export default ScorePill;
