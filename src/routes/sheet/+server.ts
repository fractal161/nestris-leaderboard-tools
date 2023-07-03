import * as fs from "fs";
import type { RequestEvent } from "@sveltejs/kit";
import { error, json } from "@sveltejs/kit";
import { parse } from "csv-parse";
import assert from "node:assert";

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

export async function GET( req: RequestEvent ): Promise<Response> {
  try {
    // TODO: better error handling
    const id = req.url.searchParams.get("id") ?? assert.fail("id is null");
    const rev = req.url.searchParams.get("rev") ?? assert.fail("rev is null");
    const cells = await parseCsvFile(`data/revs/${id}/${rev}.csv`);
    const revNum = parseInt(rev);
    const context = timestamps[revNum];
    context.name = "";
    const history = histories[id];
    if (history !== undefined) {
      for (const interval of history) {
        if (interval.start <= revNum && revNum <= interval.end) {
          context.name = interval.title;
          break;
        }
      }
    }
    return json({
        cells: cells,
        context: context,
    });
  } catch (err) {
    console.error(err);
    throw error(404, "bad");
  }
}
