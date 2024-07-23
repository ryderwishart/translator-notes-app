<script lang="ts">
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';
  import EmbedDocuments from './components/EmbedDocuments.svelte';
  import GenerateResponse from './components/GenerateResponse.svelte';
  import CheckVerseString from './components/CheckVerseString.svelte';
  import QueryChroma from './components/QueryChroma.svelte';
  import { marked } from 'marked';

  // Create stores for shared state
  export const verse = writable('');
  export const query = writable('');
  export const examples = writable<string[]>([]);
  export const response = writable('');
  export const verseError = writable('');
  export const checkedVerse = writable('');
  export const isEditing = writable(false);
  export const debugMode = writable(false);

  // Function to validate the verse
  async function validateVerse(verseValue: string) {
    if (!verseValue.match(/^[A-Za-z]+\s\d+:\d+$/)) {
      verseError.set('Invalid verse format. Use "Book Chapter:Verse"');
      checkedVerse.set('');
      examples.set([]);
    } else {
      try {
        const response = await fetch(
          `/check_verse_string?query=${encodeURIComponent(verseValue)}`,
        );
        const result = await response.text();
        if (result.trim()) {
          verseError.set('');
          checkedVerse.set(result);
          await fetchExamples(verseValue);
        } else {
          verseError.set('Verse not found. Please check the reference.');
          checkedVerse.set('');
          examples.set([]);
        }
      } catch (error) {
        console.error('Error validating verse:', error);
        verseError.set('Error validating verse. Please try again.');
        checkedVerse.set('');
        examples.set([]);
      }
    }
  }

  // Function to retrieve examples
  async function fetchExamples(verseValue: string) {
    try {
      const response = await fetch('/query_chroma?n_results=10', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: `${verseValue} translation notes` }),
      });
      const data = await response.json();
      examples.set(
        data.response.documents[0].map(
          (doc: string) => doc.substring(0, 50) + '...',
        ),
      );
    } catch (error) {
      console.error('Error fetching examples:', error);
      examples.set(['Error fetching examples. Please try again.']);
    }
  }

  // Function to generate a response
  async function generateResponse(queryValue: string, verseValue: string) {
    try {
      const apiResponse = await fetch('/generate_response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: queryValue,
          verse_reference: verseValue,
        }),
      });
      const result = await apiResponse.json();
      response.set(result.response);
    } catch (error) {
      console.error('Error generating response:', error);
      response.set('Error generating response. Please try again.');
    }
  }

  // Subscribe to verse changes
  verse.subscribe((value) => {
    validateVerse(value);
  });

  // Function to convert markdown to HTML
  function markdownToHtml(markdown: string): string {
    return marked(markdown);
  }

  // Function to toggle editing mode
  function toggleEditing() {
    isEditing.update((value) => !value);
  }

  // Function to save edited response
  function saveResponse() {
    isEditing.set(false);
  }
</script>

<main>
  <h1>Translator's Notes Generator</h1>

  <div>
    <label for="verse">Enter Bible Verse:</label>
    <input
      id="verse"
      type="text"
      bind:value={$verse}
      placeholder="e.g., John 3:16"
    />
    {#if $verseError}
      <p style="color: red;">{$verseError}</p>
    {/if}
    {#if $checkedVerse}
      <div>
        <h3>Verse:</h3>
        <p>{$checkedVerse}</p>
      </div>
    {/if}
  </div>

  <div>
    <label for="query">Optional Instructions:</label>
    <input
      id="query"
      type="text"
      bind:value={$query}
      placeholder="Enter any additional instructions"
    />
  </div>

  {#if $examples.length > 0}
    <div>
      <h2>Examples:</h2>
      <ul>
        {#each $examples as example}
          <li>{example}</li>
        {/each}
      </ul>
    </div>
  {/if}

  <button on:click={() => generateResponse($query, $verse)}
    >Generate Response</button
  >

  {#if $response}
    <div>
      <h2>Response:</h2>
      {#if $isEditing}
        <textarea bind:value={$response} rows="10" cols="50"></textarea>
        <button on:click={saveResponse}>Save</button>
      {:else}
        <div class="markdown-content">
          {@html markdownToHtml($response)}
        </div>
        <button on:click={toggleEditing}>Edit</button>
      {/if}
    </div>
  {/if}

  <button class="debug-mode-button" on:click={() => debugMode.set(!$debugMode)}
    >Toggle Debug Mode</button
  >
  {#if $debugMode}
    <EmbedDocuments />
    <GenerateResponse />
    <CheckVerseString />
    <QueryChroma />
  {/if}
</main>

<style>
  main {
    font-family: Arial, sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }

  h1 {
    color: #333;
    text-align: center;
  }

  label {
    display: block;
    margin-top: 20px;
  }

  input,
  textarea {
    width: 100%;
    padding: 10px;
    margin-top: 5px;
  }

  button {
    display: block;
    margin: 20px 0;
    padding: 10px 20px;
    background-color: green;
    color: white;
    border: none;
    cursor: pointer;
  }

  button:hover {
    background-color: darkgreen;
  }

  .debug-mode-button {
    background-color: red;
    color: white;
    border: none;
    cursor: pointer;
  }

  .debug-mode-button:hover {
    background-color: darkred;
  }

  ul {
    list-style-type: none;
    padding: 0;
  }

  li {
    background-color: #f9f9f9;
    margin: 3px 0;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }

  p {
    margin: 10px 0;
  }

  .markdown-content {
    background-color: #f9f9f9;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 15px;
    margin-top: 10px;
  }

  .markdown-content :global(h1),
  .markdown-content :global(h2),
  .markdown-content :global(h3),
  .markdown-content :global(h4),
  .markdown-content :global(h5),
  .markdown-content :global(h6) {
    margin-top: 20px;
    margin-bottom: 10px;
    color: #333;
  }

  .markdown-content :global(p) {
    margin-bottom: 10px;
  }

  .markdown-content :global(ul),
  .markdown-content :global(ol) {
    margin-bottom: 10px;
    padding-left: 20px;
  }

  .markdown-content :global(pre) {
    background-color: #f1f1f1;
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 10px;
    overflow-x: auto;
  }

  .markdown-content :global(code) {
    font-family: monospace;
    background-color: #f1f1f1;
    padding: 2px 4px;
    border-radius: 3px;
  }

  .markdown-content :global(blockquote) {
    border-left: 4px solid #ccc;
    margin: 0;
    padding-left: 16px;
    color: #666;
  }
</style>
