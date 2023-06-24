<script lang="ts">
  import SheetView from "./SheetView.svelte";
  export let scrollLeft = 0;
  export let scrollTop = 0;
  export let leftProps: {
    title: string,
    headers: Array<string>,
    entries: Array<Array<string>>,
    key?: string,
  } = {
    title: "",
    headers: [],
    entries: [[]],
    key: ""
  };

  export let rightProps: {
    title: string,
    headers: Array<string>,
    entries: Array<Array<string>>,
    key?: string,
  } = {
    title: "",
    headers: [],
    entries: [[]],
    key: ""
  };

  // TODO: probably breaks when a cell is undefined on one side
  let selected: [number, number] | undefined = undefined;

  let left: SheetView;
  let right: SheetView;

  const setScroll = (e: Event) => {
    if (e.target instanceof Element) {
      scrollTop = e.target.scrollTop;
      scrollLeft = e.target.scrollLeft;
    }
  };
</script>

<div id=layout>
  <div id=left-title>
    <h2>{leftProps.title}
  </div>

  <div id=right-title>
    <h2>{rightProps.title}</h2>
  </div>

  {#key leftProps.key}
    <SheetView
      headers={leftProps.headers}
      entries={leftProps.entries}
      bind:this={left}
      bind:scrollTop={scrollTop}
      bind:scrollLeft={scrollLeft}
      bind:selected={selected}
      on:scroll={setScroll}
    />
  {/key}

  {#key rightProps.key}
    <SheetView
      headers={rightProps.headers}
      entries={rightProps.entries}
      bind:this={right}
      bind:scrollTop={scrollTop}
      bind:scrollLeft={scrollLeft}
      bind:selected={selected}
      on:scroll={setScroll}
    />
  {/key}
</div>

<style>
  #layout {
    border: 0px;
    display: grid;
    height: 100%;
    grid-template-rows: auto 1fr;
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      "left-title right-title"
      "left right";
    font-family: monospace;
  }
  div {
    border: 1px solid gray;
  }
  #left-title {
    grid-area: left-title;
    overflow: auto;
  }
  #right-title {
    grid-area: right-title;
    overflow: auto;
  }
  h2 {
    margin: 2px;
  }
</style>
