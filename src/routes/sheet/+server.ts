import * as fs from "fs";
import type { RequestEvent } from '@sveltejs/kit';
import { error } from '@sveltejs/kit';

export async function GET( req: RequestEvent ): Promise<Response> {
  try {
    const i = parseInt(req.url.searchParams.get("index"));
    const text = await fs.promises.readFile(`data/test${i}.txt`);
    return new Response(text);
  } catch (e) {
    throw error(404, "bad");
  }
}
