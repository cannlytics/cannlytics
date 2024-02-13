

export const liveResults = {

  initializeLiveResults() {
    /**
     * Initialize live results.
     */
    // Mock data to simulate "aapl" data
    var aapl = [
      { Date: new Date("2023-01-01"), Close: 150 },
      { Date: new Date("2023-01-02"), Close: 152 },
      { Date: new Date("2023-01-03"), Close: 155 },
      { Date: new Date("2023-01-04"), Close: 157 },
      { Date: new Date("2023-01-05"), Close: 156 },
      // Add more data points as needed
    ];
    console.log('DATA:');
    console.log(aapl);

    // Chart code
    const chart = (() => {
      const width = 928;
      const height = 500;
      const marginTop = 20;
      const marginRight = 30;
      const marginBottom = 30;
      const marginLeft = 40;
    
      const svg = d3.create("svg")
          .attr("viewBox", [0, 0, width, height])
          .attr("width", width)
          .attr("height", height)
          .attr("style", "max-width: 100%; height: auto; height: intrinsic; font: 10px sans-serif;")
          .style("-webkit-tap-highlight-color", "transparent")
          .style("overflow", "visible");
    
      const x = d3.scaleUtc()
          .domain(d3.extent(aapl, d => d.Date))
          .range([marginLeft, width - marginRight]);
    
      const y = d3.scaleLinear()
          .domain([0, d3.max(aapl, d => d.Close)])
          .range([height - marginBottom, marginTop]);
    
      const line = d3.line()
          .x(d => x(d.Date))
          .y(d => y(d.Close));
    
      svg.append("path")
          .datum(aapl)
          .attr("fill", "none")
          .attr("stroke", "steelblue")
          .attr("stroke-width", 1.5)
          .attr("d", line);
    
      svg.append("g")
          .attr("transform", `translate(0,${height - marginBottom})`)
          .call(d3.axisBottom(x));
    
      svg.append("g")
          .attr("transform", `translate(${marginLeft},0)`)
          .call(d3.axisLeft(y));
    
      // Append the svg object to the div called 'chart'
      document.getElementById('chart').appendChild(svg.node());
    })();
  },

  initializeNewestStrains() {
    // Mock data for demonstration purposes
    const strains = [
      {
          name: 'Strain A',
          image_url: 'https://via.placeholder.com/150',
          discovered_by: 'Researcher 1',
          avg_terpenes: '1.2%',
          dominant_terpenes: ['Myrcene', 'Limonene', 'Caryophyllene', 'Pinene', 'Humulene']
      },
      {
          name: 'Strain B',
          image_url: 'https://via.placeholder.com/150',
          discovered_by: 'Researcher 2',
          avg_terpenes: '1.5%',
          dominant_terpenes: ['Pinene', 'Myrcene', 'Limonene', 'Caryophyllene', 'Humulene']
      },
      // Add more mock strains as needed
    ];
    console.log('Strains:');
    console.log(strains);

    // Render strains
    const container = document.getElementById('strains-container');
    strains.forEach(strain => {
        const card = `
            <div class="card" style="width: 18rem;">
                <img src="${strain.image_url}" class="card-img-top" alt="${strain.name}">
                <div class="card-body text-dark text-small">
                    <h5 class="card-title">${strain.name}</h5>
                    <p class="card-text">Discovered by: ${strain.discovered_by}</p>
                    <p class="card-text">Avg. Terpenes: ${strain.avg_terpenes}</p>
                    <p class="card-text">Dominant Terpenes: ${strain.dominant_terpenes.join(", ")}</p>
                </div>
            </div>
        `;
        container.innerHTML += card;
    });
  },

  initializeNewestLicenses() {
    // Mock data for demonstration purposes
    const licenses = [
      {
        license_number: "C10-0000423-LIC",
        license_status: "Active",
        license_type: "Commercial - Retailer",
        license_designation: "Adult-Use and Medicinal",
        issue_date: "2019-07-15T00:00:00",
        expiration_date: "2023-07-14T00:00:00",
        business_legal_name: "Movocan",
        premise_city: "Calexico",
        premise_state: "CA",
      },
      // Add more mock licenses as needed
    ];
    console.log('Licenses:');
    console.log(licenses);
  
    // Render licenses
    const container = document.getElementById('licenses-container'); // Ensure you have this container in your HTML
    licenses.forEach(license => {
        const card = `
            <div class="card" style="width: 18rem;">
                <div class="card-body text-dark">
                    <h5 class="card-title">${license.license_number}</h5>
                    <p class="card-text">Status: ${license.license_status}</p>
                    <p class="card-text">Type: ${license.license_type}</p>
                    <p class="card-text">Designation: ${license.license_designation}</p>
                    <p class="card-text">Issue Date: ${license.issue_date.split('T')[0]}</p>
                    <p class="card-text">Expiration Date: ${license.expiration_date.split('T')[0]}</p>
                    <p class="card-text">Legal Name: ${license.business_legal_name}</p>
                    <p class="card-text">Location: ${license.premise_city}, ${license.premise_state}</p>
                </div>
            </div>
        `;
        container.innerHTML += card;
    });
  },

  initializeNewestResults() {
    // Mock data for demonstration purposes
    const results = [
      {
        product_name: "Blue Rhino Pre-Roll",
        analyses: ["cannabinoids"],
        cannabinoids_method: "HPLC",
        cannabinoids_status: "pass",
        date_tested: "2022-04-20T16:20",
        producer: "Grow Tent",
        producer_city: "SF",
        producer_state: "CA",
        lab_results_url: "https://cannlytics.com/results/blue_rhino_pre_roll",
      },
      // Add more mock results as needed
    ];
  
    // Render results
    const container = document.getElementById('results-container'); // Ensure you have this container in your HTML
    results.forEach(result => {
      const card = `
        <div class="card mb-3" style="width: 100%;">
          <div class="card-body markdown text-dark">
            <h5 class="card-title">${result.product_name}</h5>
            <p class="card-text">Analyses: ${result.analyses.join(", ")}</p>
            <p class="card-text">Method: ${result[`${result.analyses[0]}_method`]}</p>
            <p class="card-text">Status: ${result[`${result.analyses[0]}_status`]}</p>
            <p class="card-text">Date Tested: ${new Date(result.date_tested).toLocaleDateString()}</p>
            <p class="card-text">Producer: ${result.producer}, ${result.producer_city}, ${result.producer_state}</p>
            <a href="${result.lab_results_url}" class="card-link">View Results</a>
          </div>
        </div>
      `;
      container.innerHTML += card;
    });
  },  

};