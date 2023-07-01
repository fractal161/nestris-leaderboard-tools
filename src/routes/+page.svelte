<script lang="ts">
  import DualView from "./DualView.svelte";
  import type { SheetProps } from "../types/client";
  import type { PageServerData } from "./$types";
  import { onMount } from "svelte";
  export let data: PageServerData;
  let MIN_INDEX: number;
  let MAX_INDEX: number;
  let current_index: number;
  let index_is_updating: boolean;
  let index_has_changed: boolean;
  let menuGid: string;
  let sheetIds: Array<string> = [];
  let boards: {
    [key: string]: Array<{
      gid: string,
      start: number,
      end: number,
    }>
  } = {};
  let menuBoard = "";
  let mode = "leaderboard";

  let props: Array<SheetProps> = [
    {
      title: "",
      subtitle: "",
      headers: [ ],
      entries: [ [ ] ],
      key: "",
    },
    {
      title: "",
      subtitle: "",
      headers: [ ],
      entries: [ [ ] ],
      key: "",
    },
  ];

  const formatTime = (time: number): string => {
    const date = new Date(time);
    const mm = (date.getUTCMonth() + 1).toString().padStart(2, "0");
    const d = date.getUTCDate().toString().padStart(2, "0");
    const y = date.getUTCFullYear().toString().padStart(2, "0");
    const h = date.getUTCHours().toString().padStart(2, "0");
    const m = date.getUTCMinutes().toString().padStart(2, "0");
    const s = date.getUTCSeconds().toString().padStart(2, "0");
    return `${mm}/${d}/${y} ${h}:${m}:${s} UTC`;
  };

  const updateSheet = async (index: number, id: string, rev: number | undefined): Promise<void> => {
    if (rev == undefined) return;
    try {
      const sheetFetch = await fetch("/sheet?" + new URLSearchParams({
          id: id,
          rev: rev.toString(),
        }), {
        method: 'GET',
        headers: {
          'Content-type': 'application/json',
        },
      });
      if (sheetFetch.status != 200) {
        throw Error("error fetching sheet");
      }
      const { entries, context } = await sheetFetch.json();
      props[index] = {
        title: rev.toString() + ": " + context.name,
        subtitle: `${formatTime(context.time) ?? "unknown time"} by ${context.editors ?? "unknown editor"}`,
        headers: entries[0],
        entries: entries.slice(1),
        key: rev.toString(),
      };
    }
    catch (err) {
      console.error(err);
    }
  };

  const updateProps = async (): Promise<void> => {
    if (current_index === undefined) return;
    // use index to compute the rev+id that's needed to be fetched
    if (index_is_updating) {
      index_has_changed = true;
      return;
    }
    index_is_updating = true;
    if (mode === "sheet") {
      await Promise.all([
        updateSheet(0, menuGid, current_index),
        updateSheet(1, menuGid, current_index+1)
      ]);
    }
    else if (mode === "leaderboard") {
      const board = boards[menuBoard];
      if (board !== undefined) {
        const getVersion = (index: number): {
          id: string,
          rev: number,
        } => {
          let intLength = 0;
          for (const sheet of board) {
            const newIntLength = intLength + sheet.end - sheet.start + 1;
            if (index < newIntLength) {
              return {
                id: sheet.gid,
                rev: index - intLength + sheet.start,
              };
            }
            intLength = newIntLength;
          }
          throw Error("invalid index");
        };
        const version1 = getVersion(current_index);
        const version2 = getVersion(current_index+1);
        await Promise.all([
          updateSheet(0, version1.id, version1.rev),
          updateSheet(1, version2.id, version2.rev)
        ]);
      }
      else {
        throw Error("invalid leaderboard name");
      }
    }
    index_is_updating = false;
    if (index_has_changed) {
      index_has_changed = false;
      await updateProps();
    }
  };
  const updateInterval = async (): Promise<void> => {
    if (menuGid === undefined) return;
    if (mode === "sheet") {
      const history = data.histories[menuGid];
      if (history !== undefined) {
        let min = Infinity;
        let max = 0;
        for (const interval of history) {
          min = Math.min(min, interval.start);
          max = Math.max(max, interval.end-1);
        }
        MIN_INDEX = min;
        MAX_INDEX = max;
        current_index = MIN_INDEX;
      }
      else {
        throw Error("invalid gid");
      }
    }
    else if (mode === "leaderboard") {
      const board = boards[menuBoard];
      if (board !== undefined) {
        let max = 0;
        for (const sheet of board) {
          max += sheet.end - sheet.start + 1;
        }
        MIN_INDEX = 0;
        MAX_INDEX = max-2; // figured out by trial and error lmao
        current_index = 0;
      }
      else {
        throw Error("invalid leaderboard name");
      }
    }
    await updateProps();
  }
  onMount(async () => {
    current_index = MIN_INDEX;
    sheetIds = data.gids;
    boards = data.boards;
    menuGid = sheetIds[0];
    menuBoard = Object.keys(boards)[0];
    await updateProps();
  });
  $: current_index, updateProps();
  $: menuGid, updateInterval();
  $: menuBoard, updateInterval();
  $: mode, updateInterval();
</script>

<div id=layout>

  <div id=view>
    <DualView
      leftProps={props[0]}
      rightProps={props[1]}
    />
  </div>

  <div id=scrollbar>
    <button class=scroll-button on:click={() => {
      current_index = Math.max(MIN_INDEX, current_index-1)
    }}>-</button>
    <input
      type=range
      min={ MIN_INDEX }
      max= { MAX_INDEX }
      bind:value={current_index}
    >
    <button class=scroll-button on:click={() => {
      current_index = Math.min(MAX_INDEX, current_index+1)
    }}>+</button>
  </div>

  <div id=sidebar>
    <p>Mode:</p>
    <select bind:value={mode}>
      <option value="leaderboard">leaderboard</option>
      <option value="sheet">sheet</option>
    </select>

    {#if mode === "sheet"}
      <p>Sheet ID:</p>
      <select bind:value={menuGid}>
      {#each sheetIds as id}
        <option value={id}>
          {id}
        </option>
      {/each}
      </select>
    {:else if mode === "leaderboard"}
      <p>Leaderboard:</p>
      <select bind:value={menuBoard}>
      {#each Object.keys(boards) as id}
        <option value={id}>
          {id}
        </option>
      {/each}
      </select>
    {/if}
  </div>
</div>

<style>
  #layout {
    border: 0px;
    height: 100vh;
    width: 100vw;
    display: grid;
    grid-template-rows: minmax(0, 1fr) auto;
    grid-template-columns: minmax(0, 1fr) 15%;
    grid-template-areas:
      "view side"
      "slider side";
    font-family: monospace;
  }
  div {
    border: 1px solid gray;
  }
  input[type=range] {
    border: none;
    width: 100%;
  }
  #scrollbar {
    grid-area: slider;
    margin: auto;
    padding: 5px 0px 5px 0px;
    width: 100%;
    display: flex;
    flex-direction: row;
  }
  #sidebar {
    grid-area: side;
    padding: 6px;
  }
  #view {
    grid-area: view;
  }
  :global(body) {
    margin: 0;
    padding: 0;
  }
  .scroll-button {
    margin: 3px;
  }
</style>
