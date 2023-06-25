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
    const id = req.url.searchParams.get("id");
    const rev = req.url.searchParams.get("rev");
    const entries = await parseCsvFile(`data/revs/${id}/${rev}.csv`);
    return json(entries);
  } catch (err) {
    console.error(err);
    throw error(404, "bad");
  }
}
