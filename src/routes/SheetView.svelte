<script lang="ts">
  import { afterUpdate } from "svelte";
  import Sheet from "./Sheet.svelte";
  export let headers: Array<string>;
  export let entries: Array<Array<string>>;
  export let scrollTop = 0;
  export let scrollLeft = 0;
  let main: HTMLDivElement;
  const setScroll = () => {
    if (main === undefined) return;
    main.scrollTop = scrollTop;
    main.scrollLeft = scrollLeft;
  };

  afterUpdate(async () => {
    setScroll();
  });
</script>

<div bind:this={main} on:scroll>
  <Sheet headers={headers} entries={entries} />
</div>

<style>
  div {
    overflow: auto;
    border: 1px solid black;
  }
</style>
