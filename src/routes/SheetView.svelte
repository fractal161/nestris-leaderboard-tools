<script lang="ts">
  import Sheet from "./Sheet.svelte";
  export let headers: Array<string>;
  export let entries: Array<Array<string>>;
  export let scrollTop = 0;
  export let scrollLeft = 0;
  export let selected: [number, number] | undefined = undefined;
  let main: HTMLDivElement;
  const setScroll = () => {
    if (main === undefined) return;
    main.scrollTop = scrollTop;
    main.scrollLeft = scrollLeft;
  };

  $: scrollTop, setScroll()
  $: scrollLeft, setScroll()
</script>

<div bind:this={main} on:scroll>
  <Sheet headers={headers} entries={entries} bind:selected={selected}/>
</div>

<style>
  div {
    overflow: auto;
    box-shadow: inset 1px 1px 1px gray, inset -1px -1px 1px gray;
  }
</style>
