import * as fs from "fs";
import type { Sheet } from "../types/client";
import { parseCsvFile } from "$lib/util";

const timestamps = JSON.parse(
  fs.readFileSync("data/timestamps.json").toString(),
);
const histories = JSON.parse(
  fs.readFileSync("data/sheet_history.json").toString(),
);

export const getSheetRev = async (id: string, rev: number): Promise<Sheet> => {
  const context = timestamps[rev];
  const history = histories[id];
  context.name = "";
  const cells = await parseCsvFile(`data/revs/${id}/${rev}.csv`);
  // strip out excessive empty rows
  const rowIsEmpty = (row: Array<string>) => row.every((cell) => cell === "");
  let i = cells.length - 1;
  while (i >= 0 && rowIsEmpty(cells[i])) {
    i--;
  }
  i++;
  if (history !== undefined) {
    for (const interval of history) {
      if (interval.start <= rev && rev <= interval.end) {
        context.name = interval.title;
        break;
      }
    }
  }
  return {
    cells: cells
      .slice(0, i)
      .concat([[(cells.length - i).toString(), "empty rows"]]),
    context: context,
    rev: rev,
  };
};
