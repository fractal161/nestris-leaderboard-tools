<script lang="ts">
  import SheetView from "./SheetView.svelte";
  let index = 1;
  let left: SheetView;
  let right: SheetView;
  let scrollLeft: number;
  let scrollTop: number;
  let leftHead: string;
  let inTimeout = false;
  let nextIndex: number | undefined = undefined;

  let leftSheetProps = {
    headers: [ "RANK", "NAME" ],
    entries: [
      [ "test", "test", "test", "test" ]
    ],
  }

  let rightSheetProps = {
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
    leftHead = await res.text();
  };


  const setScroll = (e: Event) => {
    if (e.target instanceof Element) {
      scrollTop = e.target.scrollTop;
      scrollLeft = e.target.scrollLeft;
    }
  };
</script>

<div id=layout>
  <div class=left-title>
    {#await fetchData(index)}
      <h2>{leftHead}</h2>
    {:then}
      <h2>{leftHead}</h2>
    {:catch}
      <h2>File not found</h2>
    {/await}
  </div>

  <div class=right-title>
    <h2>{index+1}</h2>
  </div>

  <SheetView
    {...leftSheetProps}
    bind:this={left}
    bind:scrollTop={scrollTop}
    bind:scrollLeft={scrollLeft}
    on:scroll={setScroll}
  />
  <SheetView
    {...rightSheetProps}
    bind:this={right}
    bind:scrollTop={scrollTop}
    bind:scrollLeft={scrollLeft}
    on:scroll={setScroll}
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
    grid-template-rows: auto 1fr auto;
    grid-template-columns: 1fr 1fr 25%;
    grid-template-areas:
      "left-title right-title side"
      "left right side"
      "slider slider side";
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
  .left-title {
    grid-area: left-title;
    overflow: auto;
  }
  .right-title {
    grid-area: right-title;
    overflow: auto;
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
  h2 {
    margin: 2px;
  }
</style>
