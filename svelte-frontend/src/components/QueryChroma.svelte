<script lang="ts">
  let query: string = '';
  let nResults: number = 10;
  let result: any | null = null;

  async function handleSubmit() {
    const response = await fetch(`/query_chroma?n_results=${nResults}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });
    const data = await response.json();
    result = data.response;
  }
</script>

<div class="card">
  <h2>Query Chroma</h2>
  <form on:submit|preventDefault={handleSubmit}>
    <input bind:value={query} placeholder="Enter query" />
    <input
      type="number"
      bind:value={nResults}
      placeholder="Number of results"
    />
    <button type="submit">Query</button>
  </form>
  {#if result}
    <div class="result">
      <h3>Results:</h3>
      <pre>{JSON.stringify(result, null, 2)}</pre>
    </div>
  {/if}
</div>

<style>
  /* Similar styles as EmbedDocuments.svelte */
  pre {
    white-space: pre-wrap;
    word-wrap: break-word;
  }
</style>
