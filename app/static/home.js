let originalTitle = document.title;
let titleInterval = null;

function startTitleSpinner() {
  const frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
  let i = 0;
  titleInterval = setInterval(() => {
    document.title = `${frames[i % frames.length]} Processing...`;
    i++;
  }, 150);
}

function stopTitleSpinner() {
  clearInterval(titleInterval);
  document.title = originalTitle;
}

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
    startTitleSpinner();

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
        stopTitleSpinner();

        // Build table using structured_data from response.
        if (result.structured_data) {
          generateTable(result.structured_data);
        } else {
          document.getElementById('tableContainer').innerHTML = '<p>No valid structured data received.</p>';
        }

        // Add download link if available.
        if (result.download_url) {
          document.getElementById('downloadContainer').innerHTML = `<a id="downloadLink" href="${result.download_url}" download>Download Processed File</a>`;
        }

        if (result.overall_scores) {
          const { lexical_score, numerical_score } = result.overall_scores;
          const resultLine = document.createElement('p');
          resultLine.textContent = `Overall results: Lexical score - ${lexical_score} Numerical score - ${numerical_score}`;
          resultLine.style.fontWeight = 'bold';
          resultLine.style.marginTop = '20px';
          resultLine.style.color = '#333';
          resultLine.style.fontSize = '20px'

          document.getElementById('tableContainer').prepend(resultLine);
        }
      })
      .catch(error => {
        console.error('Error:', error);
        document.getElementById('spinner').style.display = 'none';
        stopTitleSpinner();
        document.getElementById('tableContainer').innerHTML = '<p>Error processing file.</p>';
      });
  }
});

function generateTable(data) {
  const container = document.getElementById('tableContainer');
  container.innerHTML = '';

  if (!Array.isArray(data) || data.length === 0) {
    container.innerHTML = '<p>No data to display.</p>';
    return;
  }

  const orderedKeys = [
    "Page number",
    "Lexical score %",
    "Numerical score %",
    "Problems"
  ];

  const keys = orderedKeys;
  const table = document.createElement('table');
  const colWidths = {
    "Page number": "65px",
    "Lexical score %": "80px",
    "Numerical score %": "85px",
    "Problems": "400px",
  };

  const colgroup = document.createElement('colgroup');
  keys.forEach(key => {
    const col = document.createElement('col');
    col.style.width = colWidths[key] || 'auto';
    colgroup.appendChild(col);
  });
  table.appendChild(colgroup);

  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');
  keys.forEach(key => {
    const th = document.createElement('th');
    th.textContent = key;
    th.style.overflowWrap = 'anywhere';
    th.style.textAlign = 'center';
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);
  table.appendChild(thead);

  const tbody = document.createElement('tbody');
  data.forEach((item, rowIndex) => {
    const row = document.createElement('tr');
    keys.forEach((key, colIndex) => {
      const td = document.createElement('td');
      if (key === 'Problems') {
        td.classList.add('accordion-cell');
        td.innerHTML = `
          <div class="summary" style="text-align: center">Click to expand</div>
          <div class="accordion-content">${item[key]}</div>
        `;
        td.addEventListener('click', () => {
          document.querySelectorAll('.accordion-cell').forEach(cell => {
            if (cell !== td) cell.classList.remove('expanded');
          });
          td.classList.toggle('expanded');
        });
      } else {
        td.textContent = item[key];
        td.style.textAlign = 'center';
      }
      row.appendChild(td);
    });
    tbody.appendChild(row);
  });
  table.appendChild(tbody);
  container.appendChild(table);
}
