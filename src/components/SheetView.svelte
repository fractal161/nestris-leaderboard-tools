<script lang="ts">
  import { onMount } from "svelte";
  export let scrollTop = 0;
  export let scrollLeft = 0;
  export let height;
  let main: HTMLDivElement;
  const setScroll = () => {
    if (main === undefined) return;
    main.scrollTop = scrollTop;
    main.scrollLeft = scrollLeft;
  };

  $: scrollTop, setScroll();
  $: scrollLeft, setScroll();
  onMount(() => {
    console.log("SheetView mounted");
    setScroll();
  });
</script>

<div class="parent" bind:this={main} bind:clientHeight={height} on:scroll>
  <div class="child">
    <slot />
  </div>
  <div class="scrollspace" />
</div>

<style>
  .child {
    display: inline-block;
    position: relative;
    min-width: 100%;
    flex-shrink: 0;
  }
  .parent {
    position: relative;
    display: flex;
    flex-direction: row;
    box-shadow: inset 1px 1px 1px gray, inset -1px -1px 1px gray;
    overflow: scroll;
  }
  .scrollspace {
    position: sticky;
    border: 1px solid darkgrey;
    top: 0px;
    right: 0px;
    background-color: lightgrey;
    min-width: 10px;
    height: 100%;
  }
</style>
