<script lang="ts">
  let input: string = '';
  let result: { message: string; files_processed: number } | null = null;
  let selectedFiles: File[] = [];
  let showClearDbButton = false;

  async function handleSubmit() {
    const formData = new FormData();
    selectedFiles.forEach((file, index) => {
      formData.append(`file${index}`, file);
    });

    const response = await fetch('/embed_documents', {
      method: 'POST',
      body: formData,
    });
    result = await response.json();
    showClearDbButton = true;
  }

  async function handleClick() {
    try {
      if ('showOpenFilePicker' in window) {
        const fileHandles = await (window as any).showOpenFilePicker({
          types: [
            {
              description: 'TSV Files',
              accept: {
                'text/tab-separated-values': ['.tsv'],
              },
            },
          ],
          multiple: true,
        });

        selectedFiles = [];
        for (const fileHandle of fileHandles) {
          const file = await fileHandle.getFile();
          if (file.name.endsWith('.tsv')) {
            selectedFiles.push(file);
          }
        }

        if (selectedFiles.length === 0 && fileHandles.length === 1) {
          const dirHandle = fileHandles[0];
          if (dirHandle.kind === 'directory') {
            await listTsvFilesInDirectory(dirHandle);
            input = dirHandle.name + ' (Directory)';
          }
        } else {
          input = selectedFiles.map((f) => f.name).join(', ');
        }
      } else {
        alert(
          'File picker not supported in this browser. Please enter the path manually.',
        );
      }
    } catch (error) {
      console.error('Error selecting file or directory:', error);
      alert(
        'Failed to select file or directory. Please try again or enter the path manually.',
      );
    }
  }

  async function listTsvFilesInDirectory(dirHandle: any) {
    for await (const entry of dirHandle.values()) {
      if (entry.kind === 'file' && entry.name.endsWith('.tsv')) {
        selectedFiles.push(await entry.getFile());
      } else if (entry.kind === 'directory') {
        await listTsvFilesInDirectory(entry);
      }
    }
  }

  async function clearDatabase() {
    const response = await fetch('/clear_database', { method: 'POST' });
    const result = await response.json();
    alert(result.message);
    showClearDbButton = false;
  }
</script>

<div class="card">
  <h2>Embed Documents</h2>
  <form on:submit|preventDefault={handleSubmit}>
    <input
      bind:value={input}
      placeholder="Enter file path or folder"
      readonly
    />
    <button type="button" on:click={handleClick}>Select Files</button>
    <button type="submit">Embed</button>
  </form>
  {#if selectedFiles.length > 0}
    <h3>Selected Files:</h3>
    <ul>
      {#each selectedFiles as file}
        <li>{file.name}</li>
      {/each}
    </ul>
  {/if}
  {#if result}
    <div class="result">
      <p>{result.message}</p>
      <p>Files processed: {result.files_processed}</p>
    </div>
  {/if}
  {#if showClearDbButton}
    <button on:click={clearDatabase}>Clear Database</button>
  {/if}
</div>

<style>
  .card {
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 1rem;
    margin-bottom: 1rem;
  }
  ul {
    list-style-type: none;
    padding-left: 0;
  }
  li {
    margin-bottom: 0.5rem;
  }
</style>
