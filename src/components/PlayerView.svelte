<script lang="ts">
  export let playerList = ["player1", "player2"];
  export let scoreList = ["score1", "score2"];
  export let selectedPlayer: string | undefined = undefined;
</script>

<div class="main">
  <div class="player-menu">
    <h3>Players</h3>
    <div class="scroll-container">
      {#each playerList as player}
        <input
          type="radio"
          bind:group={selectedPlayer}
          name="players"
          id={player}
          value={player}
        />
        <label class="player-option" for={player}>{player} </label>
      {/each}
    </div>
  </div>
  <div class="scores">
    <h3>Scores for {selectedPlayer || "unselected"}</h3>
    <div class="scroll-container">
      <ul>
        {#each scoreList as score}
          <li value={score}>{score}</li>
        {/each}
      </ul>
    </div>
  </div>
</div>

<style>
  h3 {
    margin: 4px;
  }
  ul {
    list-style: none;
    text-align: left;
    padding: 0px;
    margin: 0px;
    border-collapse: collapse;
  }
  li {
    padding-left: 5px;
    border-top: 1px solid grey;
    border-bottom: 1px solid grey;
  }
  .main {
    display: flex;
    flex-direction: row;
    height: 100%;
  }
  .player-menu {
    border: 1px solid grey;
    display: flex;
    flex-direction: column;
    flex: 1;
  }
  .scroll-container {
    border-top: 1px solid grey;
    overflow: scroll;
    height: 100%;
  }
  .scores {
    border: 1px solid grey;
    flex: 5;
    display: flex;
    flex-direction: column;
  }
  .player-option {
    display: block;
    border: 1px solid grey;
    margin: 0px -1px 0px -1px;
    padding-left: 5px;
  }
  .scroll-container input[type="radio"] {
    position: absolute;
    opacity: 0;
    cursor: pointer;
    height: 0;
    width: 0;
  }
  .player-option:hover {
    background-color: lightgrey;
  }
  .scroll-container input[type="radio"]:checked + label {
    background-color: lightblue;
  }
</style>
