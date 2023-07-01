<script lang="ts">
  import type { RGBColor } from "../types/client";
  import Sheet from "./Sheet.svelte";
  export let headers: Array<string>;
  export let entries: Array<Array<string>>;
  export let scrollTop = 0;
  export let scrollLeft = 0;
  export let selected: [number, number] | undefined = undefined;
  export let setCellColor: (i: number, j: number, color: RGBColor) => void;
  let main: HTMLDivElement;
  const setScroll = () => {
    if (main === undefined) return;
    main.scrollTop = scrollTop;
    main.scrollLeft = scrollLeft;
  };

  $: scrollTop, setScroll()
  $: scrollLeft, setScroll()
</script>

<div class="parent" bind:this={main} on:scroll>
  <div class="child">
    <Sheet
      headers={headers}
      entries={entries}
      bind:selected={selected}
      bind:setCellColor={setCellColor}
    />
  </div>
  <div class="scrollspace"></div>
</div>

<style>
  .child {
    display: inline-block;
    position: relative;
  }
  .parent {
    position: relative;
    display: flex;
    flex-direction: row;
    box-sizing: block;
    box-shadow: inset 1px 1px 1px gray, inset -1px -1px 1px gray;
    overflow: scroll;
  }
  .scrollspace {
    position: sticky;
    border: 1px solid red;
    top: 0px;
    right: 0px;
    background-color: lightgrey;
    min-width: 10px;
    height: 100%;
  }
</style>
