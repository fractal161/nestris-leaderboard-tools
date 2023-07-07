import * as fs from "fs";
import { parse } from "csv-parse";
import type { Sheet } from "../types/client";

const timestamps = JSON.parse(fs.readFileSync('data/timestamps.json').toString());
const histories = JSON.parse(fs.readFileSync('data/sheet_history.json').toString());

const parseCsvFile = async (filename: string): Promise<string[][]> => {
    const parser = parse({
        delimiter: ',',
        relax_column_count: true,
        skip_empty_lines: true,
    });
    const rows: Array<Array<string>> = [];
    return new Promise((resolve, reject) => {
        fs.createReadStream(filename)
            .on('error', (err) => reject(err))
            .pipe(parser);
        parser.on("readable", () => {
            let row;
            while ((row = parser.read()) !== null) {
                for (const cell of row) {
                  if (cell !== "") {
                    rows.push(row);
                    break;
                  }
                }
            }
        });
        parser.on("error", (err) => reject(err));
        parser.on("end", () => resolve(rows.length > 0 ? rows : [ [] ]));
    });
};

export const getSheetRev = async (id: string, rev: number): Promise<Sheet> => {
  const context = timestamps[rev];
  const history = histories[id];
  context.name = "";
  const cells = await parseCsvFile(`data/revs/${id}/${rev}.csv`);
  if (history !== undefined) {
    for (const interval of history) {
      if (interval.start <= rev && rev <= interval.end) {
        context.name = interval.title;
        break;
      }
    }
  }
  return {
    cells: cells,
    context: context,
    rev: rev,
  };
}
