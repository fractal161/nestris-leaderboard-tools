<script lang="ts">
  import DualView from "./DualView.svelte";
  import type { SheetProps } from "../types/client";
  let MIN_REV = 853;
  let MAX_REV = 39065;
  let current_rev = MIN_REV;
  let fetching: Array<boolean> = [ false, false ];
  let nextRev: Array<number | undefined> = [ undefined, undefined ];

  let props: Array<SheetProps> = [
    {
      title: current_rev.toString(),
      subtitle: "",
      headers: [ ],
      entries: [ [ ] ],
      key: "",
    },
    {
      title: (current_rev + 1).toString(),
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

  const updateSheet = async (rev: number | undefined, index: number): Promise<void> => {
    if (rev == undefined) return;
    if (fetching[index]) {
      nextRev[index] = rev;
      return;
    }
    nextRev[index] = undefined;
    try {
      fetching[index] = true;
      const sheetFetch = await fetch("/sheet?" + new URLSearchParams({
          id: (1078039113).toString(),
          rev: rev.toString(),
        }), {
        method: 'GET',
        headers: {
          'Content-type': 'application/json',
        },
      });
      fetching[index] = false;
      if (sheetFetch.status != 200) {
        throw Error("error fetching sheet");
      }
      const { entries, context } = await sheetFetch.json();
      console.log(context);
      props[index] = {
        title: rev.toString(),
        subtitle: `${formatTime(context.time) ?? "unknown time"} by ${context.editors ?? "unknown editor"}`,
        headers: entries[0],
        entries: entries.slice(1),
        key: rev.toString(),
      };
    }
    catch (err) {
      console.error(err);
    }
    await updateSheet(nextRev[index], index);
  };

  const updateProps = async (): Promise<void> => {
    await Promise.all([
      updateSheet(current_rev, 0),
      updateSheet(current_rev+1, 1)
    ]);
  };
  $: current_rev, updateProps();
</script>

<div id=layout>

  <div id=view>
    <DualView
      leftProps={props[0]}
      rightProps={props[1]}
    />
  </div>

  <div id=scrollbar>
    <button class=scroll-button on:click={() => { current_rev = Math.max(MIN_REV, current_rev-1) }}>-</button>
    <input type=range min={ MIN_REV } max= { MAX_REV } bind:value={current_rev}>
    <button class=scroll-button on:click={() => { current_rev = Math.min(MAX_REV, current_rev+1) }}>+</button>
  </div>

  <div id=sidebar>
    Unsure of what to put here
  </div>
</div>

<style>
  #layout {
    border: 0px;
    height: 100vh;
    width: 100vw;
    display: grid;
    grid-template-rows: minmax(0, 1fr) auto;
    grid-template-columns: minmax(0, 1fr) 25%;
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
