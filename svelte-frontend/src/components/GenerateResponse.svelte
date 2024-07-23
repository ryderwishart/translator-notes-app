<script lang="ts">
  let query: string = '';
  let verseReference: string = '';
  let result: { response: string; verse: string } | null = null;

  async function handleSubmit() {
    const response = await fetch('/generate_response', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, verse_reference: verseReference }),
    });
    result = await response.json();
  }
</script>

<div class="card">
  <h2>Generate Response</h2>
  <form on:submit|preventDefault={handleSubmit}>
    <input bind:value={query} placeholder="Enter query" />
    <input bind:value={verseReference} placeholder="Enter verse reference" />
    <button type="submit">Generate</button>
  </form>
  {#if result}
    <div class="result">
      <h3>Response:</h3>
      <p>{result.response}</p>
      <h3>Verse:</h3>
      <p>{result.verse}</p>
    </div>
  {/if}
</div>

<style>
  /* Similar styles as EmbedDocuments.svelte */
</style>
