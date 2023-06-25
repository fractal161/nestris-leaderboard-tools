import * as fs from "fs";
import type { RequestEvent } from "@sveltejs/kit";
import { error, json } from "@sveltejs/kit";
import { parse } from "csv-parse";


const parseCsvFile = async (filename: string): Promise<string[][]> => {
    const parser = parse({
        delimiter: ',',
        relax_column_count: true,
        skip_empty_lines: true,
    });
    fs.createReadStream(filename).pipe(parser);
    const rows: Array<Array<string>> = [];
    return new Promise((resolve, reject) => {
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
    const i = parseInt(req.url.searchParams.get("index"));
    const entries = await parseCsvFile(`data/revs/1078039113/${i}.csv`);
    return json(entries);
  } catch (e) {
    console.error(e);
    throw error(404, "bad");
  }
}
