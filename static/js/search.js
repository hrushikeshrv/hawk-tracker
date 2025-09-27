const searchInput = document.querySelector('#search-bar');
const searchResults = document.querySelector('#search-results');
const searchAPIUrl = document.querySelector('#search-api-url').value;

let typingTimer;
const typingDelay = 500; // milliseconds

searchInput.addEventListener('keyup', () => {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(() => {search(searchInput.value)}, typingDelay);
})

searchInput.addEventListener('input', () => {
    if (searchInput.value.length < 2) {
        hideSearchResults();
    }
})

function search(query) {
    console.log(`Searching for ${query}`);
    if (query.length < 2) {
        hideSearchResults();
        return;
    }
    showSearchResults();
    fetch(`${searchAPIUrl}?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.jobs.length === 0 && data.companies.length === 0 && data.pages.length === 0) {
                searchResults.innerHTML = '<span>No results found</span>';
                return;
            }
            searchResults.innerHTML = '';
            if (data.companies.length > 0) {
                const companiesHeader = document.createElement('strong');
                companiesHeader.textContent = 'Companies';
                companiesHeader.style.padding = '10px 0';
                searchResults.appendChild(companiesHeader);
                const companiesList = document.createElement('div');
                data.companies.forEach(company => {
                    const companyLink = document.createElement('a');
                    companyLink.classList.add('flexbox-column', 'aifs', 'jcfs', 'search-result-item');
                    companyLink.href = company.company_url;
                    companyLink.textContent = company.name;
                    companiesList.appendChild(companyLink);
                });
                searchResults.appendChild(companiesList);
            }
            if (data.pages.length > 0) {
                const pagesHeader = document.createElement('strong');
                pagesHeader.textContent = 'Pages';
                pagesHeader.style.padding = '10px 0';
                searchResults.appendChild(pagesHeader);
                const pagesList = document.createElement('div');
                data.pages.forEach(page => {
                    const pageItem = document.createElement('div');
                    pageItem.classList.add('flexbox-column', 'aifs', 'jcfs', 'search-result-item');
                    pageItem.innerHTML = `
                        <a href="${page.page_url}" class="page-title">${page.name}</a>
                        <a href="${page.company_url}">${page.company}</a>
                    `;
                    pagesList.appendChild(pageItem);
                });
                searchResults.appendChild(pagesList);
            }
            if (data.jobs.length > 0) {
                const jobsHeader = document.createElement('strong');
                jobsHeader.style.padding = '10px 0';
                jobsHeader.textContent = 'Jobs';
                searchResults.appendChild(jobsHeader);
                const jobsList = document.createElement('div');
                data.jobs.forEach(job => {
                    const jobItem = document.createElement('div');
                    jobItem.classList.add('flexbox-column', 'aifs', 'jcfs', 'search-result-item');
                    jobItem.innerHTML = `
                        <div class="flexbox-row column-full aic jcsb" style="flex-wrap: nowrap;">
                            <span class="job-title">${job.title}</span>
                            ${job.url ? `<a href="${job.url}" class="a space-lr" target="_blank">Apply</a>` : ''} 
                        </div>
                        <div class="flexbox-row aic aux-links">
                            <a class="muted-link company-name" href="${job.company_url}">${job.company}</a>
                            <a href="${job.page_url}" class="muted-link">${job.page}</a>
                            <a href="${job.page_link}" class="muted-link" target="_blank">View Page</a>
                        </div>
                    `;
                    jobsList.appendChild(jobItem);
                });
                searchResults.appendChild(jobsList);
            }
        })
        .catch(error => {
            console.error('Error fetching search results:', error);
            searchResults.innerHTML = '<p>Error fetching search results</p>';
        });
}

function showSearchResults() {
    searchResults.classList.remove('hidden');
    searchResults.innerHTML = '<span class="flexbox-row aic"><div class="donutSpinner smallSpinner" style="margin-right: 10px;" id="search-loading-spinner"></div> Searching</span>';
}

function hideSearchResults() {
    searchResults.classList.add('hidden');
    searchResults.innerHTML = '';
}