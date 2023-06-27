import * as fs from "fs";
import type { RequestEvent } from "@sveltejs/kit";
import { error, json } from "@sveltejs/kit";
import { parse } from "csv-parse";
import assert from "node:assert";

const timestamps = JSON.parse(fs.readFileSync('data/timestamps.json').toString());

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
                rows.push(row);
            }
        });
        parser.on("error", (err) => reject(err));
        parser.on("end", () => resolve(rows));
    });
};

export async function GET( req: RequestEvent ): Promise<Response> {
  try {
    // TODO: better error handling
    const id = req.url.searchParams.get("id") ?? assert.fail("id is null");
    const rev = req.url.searchParams.get("rev") ?? assert.fail("rev is null");
    const entries = await parseCsvFile(`data/revs/${id}/${rev}.csv`);
    const revNum = parseInt(rev);
    return json({
        entries: entries,
        context: timestamps[revNum],
    });
  } catch (err) {
    console.error(err);
    throw error(404, "bad");
  }
}
