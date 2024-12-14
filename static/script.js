let zoom = d3.zoom()
	.scaleExtent([0.25, 10])
	.on('zoom', handleZoom);


function initZoom() {
  d3.select('svg')
    .call(zoom);
}

function handleZoom(e) {
	d3.select('svg g')
		.attr('transform', e.transform);
}

function draw(data) {
  d3.select('svg g')
    .selectAll('rect')
    .data(data)
    .join(
      enter => enter
        .append("rect")
        .attr('x', d => d.x)
        .attr('y', d => d.y)
        .attr('width', 250)
        .attr('height', 80)
        .attr('fill', 'rgb(123, 24, 40)')
        .attr('rx', 20)
        .attr('ry', 20)
        .attr('id', (d, i) => "n" + i)
        .on('click', function (event, d) {
          d3.select('#sidebar')
            .classed('active', true) // Add the 'active' class to slide in
            .html(`<h2>${d.title}</h2><p>Additional details about ${d.title}</p>`); // Add content
        })
        .each(function (d, i) {
          if (i > 0) { // Only draw triangles for rectangles with id > 0
            d3.select(this.parentNode)
              .append("polygon")
              .attr("points", () => {
                const x = d.x + 125;  // Center of the rect horizontally
                const y = d.y;        // Top edge of the rect
                return `${x - 15},${y - 20} ${x + 15},${y - 20} ${x},${y}`; // Adjusted to touch by lower vertex
              })
              .attr("fill", "white");
          }

          // Add title inside the rectangle
          d3.select(this.parentNode)
            .append("text")
            .attr("x", d.x + 125) // Center horizontally
            .attr("y", d.y + 40)  // Center vertically
            .attr("fill", "white") // White font color
            .attr("text-anchor", "middle") // Center text
            .style("font-family", "Roboto") // Apply the cute font
            .style("font-weight", "bold") // Set font weight to bold
            .text(d.title); // Set text from data.title
        })
    );
    // Close sidebar when "esc" button is clicked
    d3.select('#close-btn').on('click', function() {
      d3.select('#sidebar')
        .classed('active', false); // Remove 'active' class to slide out
    });
}




function drawPaths(paths) {
  // Calculate bezier curve for each path
  const coordinates = [];
  paths.forEach(path => {
    console.log(path[0]);
    console.log(path[1]);
    // Start x y
    let x = d3.select(`#${path[0]}`).attr('x');
    console.log(x);
    let widthOne = d3.select(`#${path[0]}`).attr('width');
    console.log(widthOne);
    let y = d3.select(`#${path[0]}`).attr('y');
    const height1 = d3.select(`#${path[0]}`).attr('height');
    x = parseInt(x) + parseInt(widthOne) / 2;
    y = parseInt(y) + parseInt(height1);
    console.log(typeof x);
    console.log(x);
    console.log("HERE I AAM");

    // End x y
    let ex = d3.select(`#${path[1]}`).attr('x'); // Use escape for a single digit
    let ey = d3.select(`#${path[1]}`).attr('y');
    let width2 = d3.select(`#${path[0]}`).attr('width');
    ex = parseInt(ex) + parseInt(width2) / 2;

    // Check if any coordinate is null
    if (x !== null && y !== null && ex !== null && ey !== null) {
      const pathString = `M ${x} ${y} C ${x} ${y+50}, ${ex} ${ey-60}, ${ex} ${ey-20}`;
      console.log(pathString);
      coordinates.push(pathString);
    } else {
      console.warn("Could not find coordinates for path:", path);
    }
  });

  d3.select('svg g')
    .selectAll('path')
    .data(coordinates)
    .join('path')
    .attr('d', function(d) { return d; }) // Set the 'd' attribute for the path
    .attr('fill', 'none') // No fill for the curve
    .attr('stroke', 'white') // Stroke color
    .attr('stroke-width', 2); // Stroke width
}


initZoom();

document.addEventListener("DOMContentLoaded", () => {
  fetch('/mit-roadmap')
    .then(response => response.json())
    .then(responseData => {
      const data = responseData.data;
      const paths = responseData.paths;

      console.log(data, paths);
      draw(data);
      drawPaths(paths);
    })
    .catch(error => console.error("Error fetching data:", error));
});


