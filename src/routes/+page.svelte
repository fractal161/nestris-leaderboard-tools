<script lang="ts">
  import DualView from "./DualView.svelte";
  import { beforeUpdate } from "svelte";
  let index = 30000;
  let inTimeout = false;
  let nextIndex: number | undefined = undefined;

  let leftProps = {
    title: (index).toString(),
    headers: [ "RANK", "NAME" ],
    entries: [
      [ "test", "test", "test", "test" ]
    ],
    key: "",
  }
  for (let i = 0; i < 200; i++) {
    leftProps.entries.push([ "test", "test" ]);
  }

  let rightProps = {
    title: (index + 1).toString(),
    headers: [ "RANK", "NAME" ],
    entries: [
      [ "test", "test", "test", "test" ]
    ],
    key: "",
  }

  const fetchData = async (index: number | undefined): Promise<void> => {
    if (index === undefined) return;
    if (inTimeout) {
      nextIndex = index;
      return;
    }
    inTimeout = true;
    nextIndex = undefined;
    setTimeout(() => {
      inTimeout = false;
      fetchData(nextIndex);
    }, 200);
    const leftEntries = await (await fetch(`/sheet?index=${index}`)).json();
    leftProps.title = index.toString();
    leftProps.headers = leftEntries[0];
    leftProps.entries = leftEntries.slice(1);
    leftProps.key = index.toString();
    // leftProps.title = await res.text();
  };

  beforeUpdate(async () => {
    await fetchData(index);
  });
</script>

<div id=layout>

  <div id=view>
    <DualView
      leftProps={leftProps}
      rightProps={rightProps}
    />
  </div>

  <div id=scrollbar>
    <button class=scroll-button on:click={() => { index = Math.max(1000, index-1) }}>-</button>
    <input type=range min=1000 max=39000 bind:value={index}>
    <button class=scroll-button on:click={() => { index = Math.min(39000, index+1) }}>+</button>
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
    border: 1px solid blue;
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
