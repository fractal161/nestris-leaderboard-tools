<script lang="ts">
  import DualView from "./DualView.svelte";
  let MIN_REV = 853;
  let MAX_REV = 39067;
  let rev = MIN_REV;
  let fetching = false;
  let nextIndex: number | undefined = undefined;

  let leftProps = {
    title: (rev).toString(),
    headers: [ ],
    entries: [ [ ] ],
    key: "",
  }

  let rightProps = {
    title: (rev + 1).toString(),
    headers: [ ],
    entries: [ [ ] ],
    key: "",
  }

  const updateSheets = async (rev: number | undefined): Promise<void> => {
    if (rev === undefined) return;
    if (fetching) {
      nextIndex = rev;
      return;
    }
    nextIndex = undefined;
    try {
      fetching = true;
      const sheetFetch = await fetch("/sheet?" + new URLSearchParams({
          id: (1078039113).toString(),
          rev: rev.toString(),
        }), {
        method: 'GET',
        headers: {
          'Content-type': 'application/json',
        },
      });
      fetching = false;
      if (sheetFetch.status != 200) {
        throw Error("error fetching sheet");
      }
      const leftEntries = await sheetFetch.json();
      leftProps.title = rev.toString();
      leftProps.headers = leftEntries[0];
      leftProps.entries = leftEntries.slice(1);
      leftProps.key = rev.toString();
    }
    catch (err) {
      console.error(err);
    }
    await updateSheets(nextIndex);
    // leftProps.title = await res.text();
  };
  $: rev, updateSheets(rev);
</script>

<div id=layout>

  <div id=view>
    <DualView
      leftProps={leftProps}
      rightProps={rightProps}
    />
  </div>

  <div id=scrollbar>
    <button class=scroll-button on:click={() => { rev = Math.max(MIN_REV, rev-1) }}>-</button>
    <input type=range min={ MIN_REV } max= { MAX_REV } bind:value={rev}>
    <button class=scroll-button on:click={() => { rev = Math.min(MAX_REV, rev+1) }}>+</button>
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
