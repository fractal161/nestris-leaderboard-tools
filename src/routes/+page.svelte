<script lang="ts">
  let index = 1;
  let left: Element;
  let right: Element;
  let scrollLeft: number;
  let scrollTop: number;

  const setScroll = () => {
    if (left.scrollTop !== scrollTop) {
      scrollTop = left.scrollTop;
      right.scrollTop = scrollTop;
    }
    else {
      scrollTop = right.scrollTop;
      left.scrollTop = scrollTop;
    }

    if (left.scrollLeft !== scrollLeft) {
      scrollLeft = left.scrollLeft;
      right.scrollLeft = scrollLeft;
    }
    else {
      scrollLeft = right.scrollLeft;
      left.scrollLeft = scrollLeft;
    }
  };
</script>

<div id=layout>
  <div class=left-title>
    <h2>{index}</h2>
  </div>

  <div class=right-title>
    <h2>{index+1}</h2>
  </div>

  <div class=left bind:this={left} on:scroll={setScroll}>
    <table>
      <thead>
        <tr>
          <th>RANK</th>
          <th>NAME</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>test</td>
          <td>test</td>
          <td>test</td>
          <td>test</td>
        </tr>
      </tbody>
    </table>
  </div>
  <div class=right bind:this={right}>
    <table>
      <thead>
        <tr>
          <th>RANK</th>
          <th>NAME</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>test</td>
          <td>test</td>
          <td>test</td>
          <td>test</td>
        </tr>
      </tbody>
    </table>
  </div>
  <div id=scrollbar>
    <button class=scroll-button on:click={() => { index = Math.max(0, index-1) }}>-</button>
    <input type=range min=1 max=100 bind:value={index}>
    <button class=scroll-button on:click={() => { index = Math.min(100, index+1) }}>+</button>
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
  }
  .right-title {
    grid-area: right-title;
  }
  .left {
    grid-area: left;
    overflow: auto;
  }
  .right {
    grid-area: right;
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
  table {
    border-collapse: collapse;
  }
  td, th {
    border: 1px solid gray;
  }
  .scroll-button {
    margin: 3px;
  }
  h2 {
    margin: 2px;
  }
</style>
