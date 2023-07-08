import * as fs from "fs";
import type { RequestEvent } from "@sveltejs/kit";
import { error, json } from "@sveltejs/kit";
import assert from "node:assert";
import { getSheetRev } from "$lib/sheet";

const histories = JSON.parse(
  fs.readFileSync("data/sheet_history.json").toString(),
);

export async function GET(req: RequestEvent): Promise<Response> {
  try {
    // TODO: better error handling
    const id = req.url.searchParams.get("id") ?? assert.fail("id is null");
    const index =
      req.url.searchParams.get("index") ?? assert.fail("index is null");
    const unique = req.url.searchParams.get("unique") === "true";
    if (unique) {
      // just return the index in unique_revs.json
      const unique_revs = JSON.parse(
        (
          await fs.promises.readFile(`data/revs/${id}/unique_revs.json`)
        ).toString(),
      );
      const rev = unique_revs[index];
      return json(await getSheetRev(id, rev));
    }
    const indexNum = parseInt(index);
    const history = histories[id];
    assert(history !== undefined, "spreadsheet history not found");
    const start = history[0].start;
    const rev = indexNum + start;
    return json(await getSheetRev(id, rev));
  } catch (err) {
    console.error(err);
    throw error(404, "bad");
  }
}
