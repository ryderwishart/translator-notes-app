<script lang="ts">
  let query: string = '';
  let result: string | null = null;

  async function handleSubmit() {
    const response = await fetch(
      `/check_verse_string?query=${encodeURIComponent(query)}`,
    );
    result = await response.text();
  }
</script>

<div class="card">
  <h2>Check Verse String</h2>
  <form on:submit|preventDefault={handleSubmit}>
    <input bind:value={query} placeholder="Enter verse reference" />
    <button type="submit">Check</button>
  </form>
  {#if result}
    <div class="result">
      <h3>Verse:</h3>
      <p>{result}</p>
    </div>
  {/if}
</div>

<style>
  /* Similar styles as EmbedDocuments.svelte */
</style>
