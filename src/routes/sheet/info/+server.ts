import * as fs from "fs";
import type { RequestEvent } from "@sveltejs/kit";
import { error, json } from "@sveltejs/kit";
import assert from "node:assert";

const histories = JSON.parse(fs.readFileSync('data/sheet_history.json').toString());

export async function GET( req: RequestEvent ): Promise<Response> {
  try {
    // TODO: better error handling
    const id = req.url.searchParams.get("id") ?? assert.fail("id is null");
    const unique = req.url.searchParams.get("unique") == "true";
    if (unique) {
      return json({
        count: await getUniqueCount(id)
      });
    }
    return json({
      count: await getTotalCount(id)
    });
  } catch (err) {
    console.error(err);
    throw error(404, "bad");
  }
}

async function getTotalCount(id: string): Promise<number> {
  const history = histories[id];
  if (history !== undefined) {
    let start = Infinity;
    let end = 0;
    for (const interval of history) {
      start = Math.min(start, interval.start);
      end = Math.max(end, interval.end);
    }
    if (start === Infinity && end === 0) throw Error("No intervals found");
    // NOTE: this may not always be correct
    return end - start + 1;
  }
  throw Error("id not found");
}

async function getUniqueCount(id: string): Promise<number> {
  const unique_revs = JSON.parse(
    (await fs.promises.readFile(`data/revs/${id}/unique_revs.json`))
      .toString()
  );
  return unique_revs.length;
}
