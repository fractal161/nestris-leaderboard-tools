<script lang="ts">
  import type { RGBColor } from "../types/client";
  import SheetView from "./SheetView.svelte";
  export let scrollLeft = 0;
  export let scrollTop = 0;
  let setCellColor: (i: number, j: number, color: RGBColor) => void;
  export let leftProps: {
    title: string,
    subtitle: string,
    headers: Array<string>,
    entries: Array<Array<string>>,
    key?: string,
  } = {
    title: "",
    subtitle: "",
    headers: [],
    entries: [[]],
    key: ""
  };

  export let rightProps: {
    title: string,
    subtitle: string,
    headers: Array<string>,
    entries: Array<Array<string>>,
    key?: string,
  } = {
    title: "",
    subtitle: "",
    headers: [],
    entries: [[]],
    key: ""
  };

  let selected: [number, number] | undefined = undefined;

  const setScroll = (e: Event) => {
    if (e.target instanceof Element) {
      scrollTop = e.target.scrollTop;
      scrollLeft = e.target.scrollLeft;
    }
  };
</script>

<div id=layout>
  <div id=left-title>
    <h2>{leftProps.title}</h2>
    <p>{leftProps.subtitle}</p>
  </div>

  <div id=right-title>
    <h2>{rightProps.title}</h2>
    <p>{rightProps.subtitle}</p>
  </div>

  {#key leftProps.key}
    <SheetView
      headers={leftProps.headers}
      entries={leftProps.entries}
      bind:scrollTop={scrollTop}
      bind:scrollLeft={scrollLeft}
      bind:selected={selected}
      bind:setCellColor={setCellColor}
      on:scroll={setScroll}
    />
  {/key}

  {#key rightProps.key}
    <SheetView
      headers={rightProps.headers}
      entries={rightProps.entries}
      bind:scrollTop={scrollTop}
      bind:scrollLeft={scrollLeft}
      bind:selected={selected}
      bind:setCellColor={setCellColor}
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
  p {
    font-size: 10px;
    margin: 2px;
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
