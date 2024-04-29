

export const liveResults = {

  initializeLiveResults() {
    /**
     * Initialize live results.
     */

    // FIXME: Get parameters.
    const periodName = '1M';

    // FIXME: Connect to a specific series.
    const seriesName = 'Total THC';
    const seriesKey = 'total_thc';

    // FIXME: Get the data from Firestore:
    // stats/trends/{analyte}/{date}
    var data = [
      { date: new Date("2023-01-01"), value: 20 },
      { date: new Date("2023-01-02"), value: 21 },
      { date: new Date("2023-01-03"), value: 20 },
      { date: new Date("2023-01-04"), value: 22 },
      { date: new Date("2023-01-05"), value: 24 },
      { date: new Date("2023-01-06"), value: 24 },
      { date: new Date("2023-01-07"), value: 20 },
      { date: new Date("2023-01-08"), value: 21 },
      { date: new Date("2023-01-09"), value: 20 },
      { date: new Date("2023-01-10"), value: 22 },
      { date: new Date("2023-01-11"), value: 24 },
      { date: new Date("2023-01-12"), value: 24 },
      { date: new Date("2023-01-13"), value: 20 },
      { date: new Date("2023-01-14"), value: 25 },
      { date: new Date("2023-01-15"), value: 19 },
      { date: new Date("2023-01-16"), value: 25 },
      { date: new Date("2023-01-17"), value: 23 },
      { date: new Date("2023-01-18"), value: 21 },
      { date: new Date("2023-01-19"), value: 22 },
      { date: new Date("2023-01-20"), value: 18 },
      { date: new Date("2023-01-21"), value: 20 },
      { date: new Date("2023-01-22"), value: 19 },
      { date: new Date("2023-01-23"), value: 24 },
      { date: new Date("2023-01-24"), value: 18 },
      { date: new Date("2023-01-25"), value: 18 },
      { date: new Date("2023-01-26"), value: 19 },
      { date: new Date("2023-01-27"), value: 21 },
      { date: new Date("2023-01-28"), value: 21 },
      { date: new Date("2023-01-29"), value: 26 },
      { date: new Date("2023-01-30"), value: 18 },
      { date: new Date("2023-01-31"), value: 26 }
  ];
    console.log('DATA:');
    console.log(data);

    // Render the chart.
    const chart = (() => {
    
      // Figure
      const width = 928;
      const height = 500;
      const marginTop = 20;
      const marginRight = 30;
      const marginBottom = 30;
      const marginLeft = 40;
      let svg = d3.create("svg")
          .attr("viewBox", [0, 0, width, height])
          .attr("width", width)
          .attr("height", height)
          .attr("style", "max-width: 100%; height: auto; height: intrinsic; font: 10px sans-serif;")
          .style("-webkit-tap-highlight-color", "transparent")
          .style("overflow", "visible");
    
      // X values
      const x = d3.scaleUtc()
          .domain(d3.extent(data, d => d.date))
          .range([marginLeft, width - marginRight]);
    
      // Y values
      const y = d3.scaleLinear()
          .domain([0, d3.max(data, d => d.value)])
          .range([height - marginBottom, marginTop]);
    
      // Line
      const line = d3.line().x(d => x(d.date)).y(d => y(d.value));
      svg.append("path")
          .datum(data)
          .attr("fill", "none")
          .attr("stroke", "#00c805")
          .attr("stroke-width", 5)
          .attr("d", line);
    
      // X-axis
      const xAxis = svg.append("g")
          .attr("transform", `translate(0,${height - marginBottom})`)
          .call(d3.axisBottom(x));
      xAxis.selectAll("text")
          .attr("font-size", "16px"); // Set x-axis label size
    
      // Y-axis
      const yAxis = svg.append("g")
          .attr("transform", `translate(${marginLeft},0)`)
          .call(d3.axisLeft(y));
      yAxis.selectAll("text")
          .attr("font-size", "16px"); // Set y-axis label size

      // Create the vertical dotted line
      svg = this.addChartFunctionality(data, x, y, svg, height, marginTop, marginBottom);

      // Return the chart.
      document.getElementById('chart').appendChild(svg.node());
    })();
  },

  addChartFunctionality(data, x, y, svg, height, marginTop, marginBottom) {
    /**
     * Add chart functionality.
     */
    // Add overlay for mouse interaction
    const hoverGroup = svg.append("g")
      .attr("class", "hover-group")
      .style("display", "none");

    // Add interaction to the line on mouse hover.
    const hoverLine = hoverGroup.append("line")
      .attr("class", "hover-line")
      .attr("stroke", "gray")
      .attr("stroke-width", 1)
      .attr("stroke-dasharray", "4,4")
      .attr("y1", marginTop)
      .attr("y2", height - marginBottom);

    // Create the bullet point
    const hoverDot = hoverGroup.append("circle")
      .attr("class", "hover-dot")
      .attr("r", 4)
      .attr("fill", "#00c805");

    // Create the div to display the value
    const valueDiv = d3.select("body").append("div")
      .attr("class", "value-div")
      .style("position", "absolute")
      .style("background-color", "white")
      .style("border", "1px solid black")
      .style("padding", "5px")
      .style("display", "none");

    // Function to update the hover elements
    function updateHoverElements(event) {
      const x0 = x.invert(d3.pointer(event)[0]);
      try {
        const bisectDate = d3.bisector(d => d.date).left;
        const i = bisectDate(data, x0, 1);
        const d0 = data[i - 1];
        const d1 = data[i];
        const d = x0 - d0.date > d1.date - x0 ? d1 : d0;
        hoverLine.attr("transform", `translate(${x(d.date)},0)`);
        hoverDot.attr("transform", `translate(${x(d.date)},${y(d.value)})`);
        // TODO: Spruce up tooltip:
        // - Date: E.g. Apr 20, 2024
        // - Pass series name
        // - Number of tests?
        valueDiv.html(`Value: ${d.value}`)
          .style("left", `${event.pageX + 10}px`)
          .style("top", `${event.pageY - 28}px`);
      } catch (error) {
        return;
      }
    }

    // Add event listeners to show/hide hover elements
    svg.on("mouseover", () => {
      hoverGroup.style("display", null);
      valueDiv.style("display", null);
    })
      .on("mouseout", () => {
        hoverGroup.style("display", "none");
        valueDiv.style("display", "none");
      })
      .on("mousemove", updateHoverElements);
    
    // Return the chart.
    return svg;
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