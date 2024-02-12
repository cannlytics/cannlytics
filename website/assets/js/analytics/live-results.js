

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

  // Function to render strains
  function renderStrains(strains) {
      const container = document.getElementById('strainsContainer');
      strains.forEach(strain => {
          const card = `
              <div class="card" style="width: 18rem;">
                  <img src="${strain.image_url}" class="card-img-top" alt="${strain.name}">
                  <div class="card-body">
                      <h5 class="card-title">${strain.name}</h5>
                      <p class="card-text">Discovered by: ${strain.discovered_by}</p>
                      <p class="card-text">Avg. Terpenes: ${strain.avg_terpenes}</p>
                      <p class="card-text">Dominant Terpenes: ${strain.dominant_terpenes.join(", ")}</p>
                  </div>
              </div>
          `;
          container.innerHTML += card;
      });
  }

  // Call renderStrains on page load
  document.addEventListener('DOMContentLoaded', () => {
      renderStrains(strains);
  });
  },

};