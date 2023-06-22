<script>
  export let index = 1;
</script>

<div id=layout>
  <div id=left>
    <h2>{index}</h2>
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
  <div id=right>
    <h2>{index+1}</h2>
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
  <input type=range min=1 max=10 bind:value={index}>
  <div id=sidebar>
  </div>
</div>

<style>
  #layout {
    border: 0px;
    height: 100vh;
    width: 100vw;
    display: grid;
    grid-template-rows: 1fr 1fr auto;
    grid-template-columns: 1fr 1fr 20%;
    grid-template-areas:
      "left right side"
      "left right side"
      "slider slider side";
    font-family: monospace;
  }
  div {
    border: 1px solid gray;
  }
  input[type="range"] {
    grid-area: slider;
    display: block;
    width: 96%;
    margin: auto;
    padding: 10px 0px 10px 0px;
  }
  #left {
    grid-area: left;
    overflow: auto;
  }
  #right {
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
</style>
