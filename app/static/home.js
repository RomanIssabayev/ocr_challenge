// Trigger file input when the "Select JSON File" button is clicked.
document.getElementById('selectFileButton').addEventListener('click', function() {
  document.getElementById('jsonInput').click();
});

// On file selection, send the file to the /process_json endpoint using FormData.
document.getElementById('jsonInput').addEventListener('change', function(event) {
  const file = event.target.files[0];
  if (file) {
    // Show spinner while processing.
    document.getElementById('spinner').style.display = 'block';
    // Clear previous table and download link.
    document.getElementById('tableContainer').innerHTML = '';
    document.getElementById('downloadContainer').innerHTML = '';

    const formData = new FormData();
    formData.append('file', file);
    fetch('/process_json', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(result => {
      // Hide spinner after processing.
      document.getElementById('spinner').style.display = 'none';
      // Build table using structured_data from response.
      if(result.structured_data) {
        generateTable(result.structured_data);
      } else {
        document.getElementById('tableContainer').innerHTML = '<p>No valid structured data received.</p>';
      }
      // Add download link if available.
      if(result.download_url) {
        document.getElementById('downloadContainer').innerHTML = `<a id="downloadLink" href="${result.download_url}" download>Download Processed File</a>`;
      }
    })
    .catch(error => {
      console.error('Error:', error);
      document.getElementById('spinner').style.display = 'none';
      document.getElementById('tableContainer').innerHTML = '<p>Error processing file.</p>';
    });
  }
});

// Generate a table from JSON data (expects an array of objects).
function generateTable(data) {
  const container = document.getElementById('tableContainer');
  container.innerHTML = '';

  if (!Array.isArray(data)) {
    container.innerHTML = '<p>JSON data is not an array.</p>';
    return;
  }
  if (data.length === 0) {
    container.innerHTML = '<p>No data to display.</p>';
    return;
  }

  // Create table headers from keys of the first object.
  const keys = Object.keys(data[0]);
  const table = document.createElement('table');

  // Build the table header row.
  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');
  keys.forEach(key => {
    const th = document.createElement('th');
    th.textContent = key;
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);
  table.appendChild(thead);

  // Build the table body rows.
  const tbody = document.createElement('tbody');
  data.forEach(item => {
    const row = document.createElement('tr');
    keys.forEach(key => {
      const td = document.createElement('td');
      td.textContent = item[key];
      row.appendChild(td);
    });
    tbody.appendChild(row);
  });
  table.appendChild(tbody);

  container.appendChild(table);
}