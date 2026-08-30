let jobsData = [];
let currentSort = { column: 'score', desc: true };

async function loadJobs() {
    try {
        const response = await fetch('data.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        jobsData = await response.json();
        renderTable();
    } catch (error) {
        console.error("Error loading jobs:", error);
        document.getElementById('jobs-body').innerHTML = `
            <tr>
                <td colspan="6" style="text-align:center; padding: 20px;">
                    <strong>No data found yet.</strong><br>
                    Make sure to push your code to GitHub so the GitHub Action can run and generate the data.json file.
                </td>
            </tr>
        `;
    }
}

function renderTable() {
    const searchTerm = document.getElementById('search').value.toLowerCase();
    const sourceFilter = document.getElementById('source-filter').value;
    
    let filtered = jobsData.filter(job => {
        const title = job.title || "";
        const inst = job.institution || "";
        const country = job.country || "";
        
        const matchesSearch = inst.toLowerCase().includes(searchTerm) || 
                              title.toLowerCase().includes(searchTerm) || 
                              country.toLowerCase().includes(searchTerm);
        const matchesSource = sourceFilter === 'all' || job.source === sourceFilter;
        return matchesSearch && matchesSource;
    });

    // Sort
    filtered.sort((a, b) => {
        let valA = a[currentSort.column];
        let valB = b[currentSort.column];
        
        if (currentSort.column === 'score') {
            valA = parseFloat(valA) || 0;
            valB = parseFloat(valB) || 0;
        }

        if (valA < valB) return currentSort.desc ? 1 : -1;
        if (valA > valB) return currentSort.desc ? -1 : 1;
        return 0;
    });

    const tbody = document.getElementById('jobs-body');
    tbody.innerHTML = '';
    
    filtered.forEach(job => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><span class="score-badge">${job.score || 0}</span></td>
            <td><strong>${job.institution}</strong></td>
            <td>${job.title}</td>
            <td>${job.country}</td>
            <td>${job.deadline ? job.deadline : '-'}</td>
            <td>
                ${job.link && job.link !== 'None' ? `<a href="${job.link}" target="_blank" class="apply-btn">View</a>` : ''}
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function sortTable(column) {
    if (currentSort.column === column) {
        currentSort.desc = !currentSort.desc;
    } else {
        currentSort.column = column;
        currentSort.desc = true;
    }
    renderTable();
}

document.getElementById('search').addEventListener('input', renderTable);
document.getElementById('source-filter').addEventListener('change', renderTable);

loadJobs();
