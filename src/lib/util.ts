import * as fs from "fs";
import { parse } from "csv-parse";

export const parseCsvFile = async (filename: string): Promise<string[][]> => {
  const parser = parse({
    delimiter: ",",
    relax_column_count: true,
    skip_empty_lines: true,
  });
  const rows: Array<Array<string>> = [];
  return new Promise((resolve, reject) => {
    fs.createReadStream(filename)
      .on("error", (err) => reject(err))
      .pipe(parser);
    parser.on("readable", () => {
      let row;
      while ((row = parser.read()) !== null) {
        rows.push(row);
      }
    });
    parser.on("error", (err) => reject(err));
    parser.on("end", () => resolve(rows.length > 0 ? rows : [[]]));
  });
};

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
