export const formatDay = (time: number): string => {
  const date = new Date(time);
  const m = (date.getUTCMonth() + 1).toString().padStart(2, "0");
  const d = date.getUTCDate().toString().padStart(2, "0");
  const y = date.getUTCFullYear().toString().padStart(2, "0");
  return `${m}/${d}/${y}`;
};

export const formatTime = (time: number): string => {
  const date = new Date(time);
  const h = date.getUTCHours().toString().padStart(2, "0");
  const m = date.getUTCMinutes().toString().padStart(2, "0");
  const s = date.getUTCSeconds().toString().padStart(2, "0");
  return `${h}:${m}:${s} UTC`;
};

export const formatFullDate = (time: number): string => {
  return formatDay(time) + " " + formatTime(time);
};
