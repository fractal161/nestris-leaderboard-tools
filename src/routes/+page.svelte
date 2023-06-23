<script lang="ts">
  import DualView from "./DualView.svelte";
  import { beforeUpdate } from "svelte";
  let index = 1;
  let inTimeout = false;
  let nextIndex: number | undefined = undefined;

  let leftProps = {
    title: "",
    headers: [ "RANK", "NAME" ],
    entries: [
      [ "test", "test", "test", "test" ]
    ],
  }

  let rightProps = {
    title: (index + 1).toString(),
    headers: [ "RANK", "NAME" ],
    entries: [
      [ "test", "test", "test", "test" ]
    ],
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
    const res = await fetch(`/sheet?index=${index}`);
    leftProps.title = await res.text();
  };

  beforeUpdate(async () => {
    await fetchData(index);
  });
</script>

<div id=layout>

  <DualView
    leftProps={leftProps}
    rightProps={rightProps}
  />

  <div id=scrollbar>
    <button class=scroll-button on:click={() => { index = Math.max(1, index-1) }}>-</button>
    <input type=range min=1 max=10 bind:value={index}>
    <button class=scroll-button on:click={() => { index = Math.min(10, index+1) }}>+</button>
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
    grid-template-rows: 1fr auto;
    grid-template-columns: 1fr 25%;
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
    width: 100%;
    margin: auto;
    padding: 5px 0px 5px 0px;
    display: flex;
    flex-direction: row;
  }
  #sidebar {
    grid-area: side;
    border: 1px solid blue;
  }
  :global(body) {
    margin: 0;
    padding: 0;
  }
  .scroll-button {
    margin: 3px;
  }
</style>
