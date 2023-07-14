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
