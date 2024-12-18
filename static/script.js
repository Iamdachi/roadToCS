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

function draw(data, lectures) {
  d3.select('svg g')
    .selectAll('rect')
    .data(data)
    .join(
      enter => enter
        .append("g") // Group for each rectangle and progress bar
        .each(function (d, i) {
          const group = d3.select(this);

          // Main rectangle
          group.append("rect")
            .attr('x', d.x)
            .attr('y', d.y)
            .attr('width', 250)
            .attr('height', 80)
            .attr('id', (d, i) => "n" + i)
            .attr('fill', 'rgb(123, 24, 40)')
            .attr('rx', 20)
            .attr('ry', 20);

          // Progress bar background
          group.append("rect")
            .attr('x', d.x + 10)
            .attr('y', d.y + 60)
            .attr('width', 230)
            .attr('height', 10)
            .attr('fill', 'white')
            .attr('rx', 5)
            .attr('ry', 5);

          // Progress bar (green)
          group.append("rect")
            .attr('x', d.x + 10)
            .attr('y', d.y + 60)
            .attr('width', 0) // Initially empty
            .attr('height', 10)
            .attr('fill', 'green')
            .attr('rx', 5)
            .attr('ry', 5)
            .attr('class', `progress-bar-${i}`); // Unique class for easy selection

          // Title inside rectangle
          group.append("text")
            .attr("x", d.x + 125) // Center horizontally
            .attr("y", d.y + 40)  // Center vertically
            .attr("fill", "white")
            .attr("text-anchor", "middle")
            .style("font-family", "Roboto")
            .style("font-weight", "bold")
            .text(d.title);
        })
        .on('click', function (event, d) {
          const lectureItems = lectures[d.id]; // Use `d.id` to fetch lectures
          if (!lectureItems) return;

          d3.select('#sidebar')
            .classed('active', true);

          d3.select('#sidebar h2')
            .text(d.title);

          const ul = d3.select('#sidebar ul');
          ul.selectAll('li').remove();

          ul.selectAll('li')
            .data(lectureItems)
            .enter()
            .append('li')
            .each(function (lecture) {
              const li = d3.select(this);

              li.append('input')
                .attr('type', 'checkbox')
                .attr('class', 'lecture-checkbox')
                .on('change', function () {
                  const checkboxes = ul.selectAll('.lecture-checkbox');
                  const checkedCount = checkboxes.filter(':checked').size();
                  const totalLectures = checkboxes.size();
                  const progress = (checkedCount / totalLectures) * 230; // Scale to bar width

                  d3.select(`.progress-bar-${d.id}`)
                    .attr('width', progress);
                });

              li.append('a')
                .attr('href', lecture.link)
                .attr('target', '_blank')
                .text(lecture.title);
            });
        })
    );

  d3.select('#close-btn').on('click', function () {
    d3.select('#sidebar').classed('active', false);
  });
}

function drawPaths(paths) {
  const coordinates = [];
  paths.forEach(path => {
    // Start x y
    let rect1 = d3.select(`#n${path[0]}`).node().parentNode; // Select parent group of the first rectangle
    let rect2 = d3.select(`#n${path[1]}`).node().parentNode; // Select parent group of the second rectangle

    if (!rect1 || !rect2) {
      console.warn(`Could not find elements for path:`, path);
      return;
    }

    let x = +d3.select(rect1).select('rect').attr('x');
    let widthOne = +d3.select(rect1).select('rect').attr('width');
    let y = +d3.select(rect1).select('rect').attr('y');
    const height1 = +d3.select(rect1).select('rect').attr('height');
    x = x + widthOne / 2;
    y = y + height1;

    // End x y
    let ex = +d3.select(rect2).select('rect').attr('x');
    let ey = +d3.select(rect2).select('rect').attr('y');
    let width2 = +d3.select(rect2).select('rect').attr('width');
    ex = ex + width2 / 2;

    // Check if any coordinate is null
    if (x !== null && y !== null && ex !== null && ey !== null) {
      const pathString = `M ${x} ${y} C ${x} ${y + 50}, ${ex} ${ey - 60}, ${ex} ${ey - 20}`;
      coordinates.push(pathString);
    } else {
      console.warn("Could not find coordinates for path:", path);
    }
  });

  d3.select('svg g')
    .selectAll('path')
    .data(coordinates)
    .join('path')
    .attr('d', d => d) // Set the 'd' attribute for the path
    .attr('fill', 'none') // No fill for the curve
    .attr('stroke', 'white') // Stroke color
    .attr('stroke-width', 2); // Stroke width
}

initZoom();

document.addEventListener("DOMContentLoaded", () => {
  Promise.all([
    fetch('/mit-lectures').then(response => response.json()),
    fetch('/mit-roadmap').then(response => response.json())
  ]).then(([lecturesResponse, roadmapResponse]) => {
    const lectures = lecturesResponse;
    const data = roadmapResponse.data;
    const paths = roadmapResponse.paths;

    console.log("SHOW ME THE LECTURES");
    console.log(lectures);

    draw(data, lectures); // Now `lectures` is guaranteed to be available
    drawPaths(paths);
  }).catch(error => {
    console.error("Error loading data:", error);
  });
});


